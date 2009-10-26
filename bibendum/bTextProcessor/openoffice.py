# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------
#    Bibendum's Text Processor OpenOffice.org module
#    
#    bTextProcessor/openoffice.py,
#    this file is part of the Bibendum Reference Manager project
#    
#    Etienne Gaudrain <egaudrain@gmail.com>, 2009-10-23
#    $Revision$ $Date$
#-------------------------------------------------------------------------
#    
#    Copyright 2009 Etienne Gaudrain
#    
#    Bibendum Reference Manager is a free software: you can redistribute it
#    and/or modify it under the terms of the GNU General Public License as
#    published by the Free Software Foundation, version 3 of the License.
#    
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#    
#-------------------------------------------------------------------------

import _generic
import uno
import re

"""This module is used to communicate with OpenOffice.org Writer using `PyUNO <http://udk.openoffice.org/python/python-bridge.html>`_."""

class bridge(_generic.bridge):
	"""Communication with OpenOffice.org Writer.
	
	.. automethod:: _getRealText
	"""
	
	def __init__(self, options=None):
		localContext = uno.getComponentContext()
		self.resolver = localContext.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", localContext )
		
		if options is not None:
			self.connect(options)
	
	def connect(self, options):
		"""Initiates a connection with the text processor. *options* is ``dict`` with the following entries:
		
		  * *'type'*: is either "pipe" or "socket"
		  * if *'type'* is "pipe", an item *'name'* containing the pipe name should be provided
		  * if *'type'* is socket, *'host'* and *'port'* should be provided
		
		Once the connected, the method searches for an active window of the correct type and store in ``self.doc``.
		"""
		
		self.options = options
		
		self.unourl = "uno:%s" % options['type']
		if options['type']=='pipe':
			self.unourl += ",name=%s" % options['name']
		elif options['type']=='socket':
			self.unourl += ",host=%s,port=%s" % (options['host'], options['port'])
		self.unourl += ";urp;StarOffice.ComponentContext"
		
		try:
			self.ctx = self.resolver.resolve( self.unourl )
			self.smgr = self.ctx.ServiceManager
			self.desktop = self.smgr.createInstanceWithContext( "com.sun.star.frame.Desktop", self.ctx)
			self.doc = self.desktop.getCurrentComponent()
			
			if self.doc.getImplementationName()!='SwXTextDocument':
				raise TypeError('The active document is not of type Writer.')
			
		except Exception as e:
			self.connected = False
			return False, e
		
		self.connected = True
		return True, None

	# TODO: Mechanism to check the connection is valid to be able to re-use the connection
	
	def _getRealText(self, obj=None):
		"""A helper function that returns the text content (Python ``unicode``) of *obj* in a way that allows correspondance with UNO cursor operations.
		
		This is done because when moving a cursor by a step of 1 on a field, the cursor jumps the whole field while the ``String`` property of the object includes the textual representation of the field.
		
		If *obj* is None, the current document is used.
		"""
		
		if obj is None:
			obj = self.doc.Text
		
		real_txt = ''
		
		if obj.ImplementationName in ['SwXTextPortion']:
			if obj.TextPortionType=='Text':
				s = obj.String
			elif obj.TextPortionType=='TextField':
				s = ' '
			else:
				s = ''
			real_txt += s
		elif obj.ImplementationName in ['SwXCell', 'SwXParagraph', 'SwXBodyText']:
			e = obj.createEnumeration()
			while e.hasMoreElements():
				real_txt += self._getRealText(e.nextElement())
			if obj.ImplementationName == 'SwXParagraph':
				real_txt += '\n'
		elif obj.ImplementationName in ['SwXTextTable']:
			for i in range(obj.Rows.Count):
				for j in range(obj.Columns.Count):
					real_txt += self._getRealText(obj.getCellByPosition(i,j))
		
		return real_txt
	
	def findCitations(self, regexp):
		"""Returns a list of possible citations using the provided regular expression.
		Given the limitations of the regular expression engine in OOo, a text compatible
		with cursor operation is first extracted, then Python regular expressions are used.
		
		Note: If *regexp* is a string, it will be compiled using the ``re.UNICODE`` option."""
		
		txt = self._getRealText()
		
		if type(regexp)==type(''):
			regexp = re.compile(regexp, re.UNICODE)
		
		citations = list()
		for f in regexp.finditer(txt):
			citations.append((f.group(), f.span()))
		
		return citations
	
	def highlight(self, on, range=None):
		"""Highlights (*on*=True) or not (*on*=False) the *range*. If a range was previously
		highlighted it is set back to normal first. If no range is provided and *on*=False,
		any previous highlight is removed.
		
		Note: it is better to let the function manage the suppression since it restores user defined highlights."""
		
		if range is None and on:
			# Should not happen. Do nothing.
			return
		
		# Restore Background
		if self.highlighted_range is not None:
			old_range, old_color = self.highlighted_range
			c = self.doc.Text.createTextCursorByRange(self.doc.Text.getStart())
			c.goRight(old_range[0], False)
			c.goRight(old_range[1], True)
			c.CharBackColor =  old_color
			c.collapseToEnd()
			c.setAllPropertiesToDefault()
			
			self.highlighted_range = None
			
		# Restore view cursor
		if self.previous_view_cursor is not None:
			c = self.doc.getCurrentController().getViewCursor()
			c.gotoRange(self.previous_view_cursor, False)
		
		if range is not None:
			color = int('0x00'+self.highlight_color, 16)
			c = self.doc.Text.createTextCursorByRange(self.doc.Text.getStart())
			c.goRight(range[0], False)
			c.goRight(range[1]-range[0], True)
			
			old_color = c.CharBackColor
			self.highlighted_range = (range, old_color)
			
			c.CharBackColor = color
			c.collapseToStart()
			c.setAllPropertiesToDefault()
			
			# Save view cursor
			v = self.doc.getCurrentController().getViewCursor()
			self.previous_view_cursor = v.getStart()
			v.gotoRange(c.getStart(), False)
		

#--------------------------------

def test_bridge_connection():
	OOoBridge = bridge()
	ok, e = OOoBridge.connect({'type': 'pipe', 'name':'OOo_pipe'})
	if ok:
		print OOoBridge.connected
	else:
		print e

def test_find_citations():
	OOoBridge = bridge()
	ok, e = OOoBridge.connect({'type': 'pipe', 'name':'OOo_pipe'})
	if not ok:
		print e
		return
	
	lowercase = 'éèçàôêîù';
	uppercase = 'ÉÈÇÀÔÊÎÙ';
	
	author  = '((?:[vV]an |[vV]on |[dD]e |[dD]e la |[dD]el )?(?:Mc)?[A-Z%s][a-z%s-]+)' % (uppercase, lowercase)
	authorI = '((?:[vV]an |[vV]on |[dD]e |[dD]e la |[dD]el )?)((?:Mc)?[A-Z%s][a-z%s-]+)' % (uppercase, lowercase)
	date    = '([1-2][0-9]{3}[a-z]?)'
	
	authorBlock = '%s(?:,? (et al\\.)?|(?:, %s)*,? (?:&|and) %s)?' % (author,author,author)
	dateBlock   = '%s(?:, %s)*' % (date, date)
	dateBlock   = '(?:(?:%s)|(?:\\(%s\\)))' % (dateBlock, dateBlock)
	
	citation = '('+authorBlock+',? '+dateBlock+')'
	
	reCite = re.compile(citation, re.UNICODE)
	
	print OOoBridge.findCitations(reCite)

def test_highlight():
	import time
	
	OOoBridge = bridge()
	ok, e = OOoBridge.connect({'type': 'pipe', 'name':'OOo_pipe'})
	if not ok:
		print e
		return
	
	lowercase = 'éèçàôêîù';
	uppercase = 'ÉÈÇÀÔÊÎÙ';
	
	author  = '((?:[vV]an |[vV]on |[dD]e |[dD]e la |[dD]el )?(?:Mc)?[A-Z%s][a-z%s-]+)' % (uppercase, lowercase)
	authorI = '((?:[vV]an |[vV]on |[dD]e |[dD]e la |[dD]el )?)((?:Mc)?[A-Z%s][a-z%s-]+)' % (uppercase, lowercase)
	date    = '([1-2][0-9]{3}[a-z]?)'
	
	authorBlock = '%s(?:,? (et al\\.)?|(?:, %s)*,? (?:&|and) %s)?' % (author,author,author)
	dateBlock   = '%s(?:, %s)*' % (date, date)
	dateBlock   = '(?:(?:%s)|(?:\\(%s\\)))' % (dateBlock, dateBlock)
	
	citation = '('+authorBlock+',? '+dateBlock+')'
	
	reCite = re.compile(citation, re.UNICODE)
	
	c = OOoBridge.findCitations(reCite)
	
	OOoBridge.highlight(True, c[0][1])
	time.sleep(3)
	OOoBridge.highlight(False)

#================================================================================
if __name__=='__main__':
	#~ test_bridge_connection()
	#~ test_find_citations()
	test_highlight()


