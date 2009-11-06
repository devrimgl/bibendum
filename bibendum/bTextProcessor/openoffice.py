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

import uno
import re

import bBase
import bTextProcessor._generic

from com.sun.star.text.ControlCharacter import PARAGRAPH_BREAK


"""This module is used to communicate with OpenOffice.org Writer using `PyUNO <http://udk.openoffice.org/python/python-bridge.html>`_."""

class bridge(bTextProcessor._generic.bridge):
	"""This implementation of :class:`bTextProcessor._generic` is used to communicate with
	OpenOffice.org Writer using `PyUNO <http://udk.openoffice.org/python/python-bridge.html>`_.
	
	.. automethod:: _getRealText
	
	.. automethod:: _setStyle
	
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
			
		except Exception, e:
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
	
	def findRegexp(self, regexp):
		"""Returns a list of match using the provided regular expression.
		Given the limitations of the regular expression engine in OOo, a text compatible
		with cursor operation is first extracted, then Python regular expressions are used.
		
		Note 1: If *regexp* is a string, it will be compiled using the ``re.UNICODE`` option.
		
		Note 2: The match list is returned starting with the last one."""
		
		txt = self._getRealText()
		
		if type(regexp)==type(''):
			regexp = re.compile(regexp, re.UNICODE)
		
		t_citations = dict()
		for f in regexp.finditer(txt):
			t_citations[f.span()[0]] = (f.group(), f.span(), f.groups())
		
		# Sort the citation list to start with the last one
		keys = t_citations.keys()
		keys.sort(None, None, True)
		citations = list()
		for k in keys:
			citations.append( t_citations[k] )
		
		return citations
	
	def highlight(self, on, range=None):
		"""Highlights (`on=True`) or not (`on=False`) the *range*. If a range was previously
		highlighted it is set back to normal first. If no range is provided and `on=False`,
		any previous highlight is removed.
		
		Note: it is better to let the function manage the suppression since it restores user defined highlights."""
		
		if range is None and on:
			# Should not happen. Do nothing.
			return
		
		# Restore Background
		if self.highlighted_range is not None:
			for old_range, old_color in zip(self.highlighted_range[0], self.highlighted_range[1]):
				c = self.doc.Text.createTextCursorByRange(old_range)
				if old_color is not None and old_color>=0:
					c.CharBackColor =  old_color
				else:
					c.CharBackColor = 0x00ffffff
				c.collapseToEnd()
				
			
			self.highlighted_range = None
			
		# Restore view cursor
		if self.previous_view_cursor is not None:
			c = self.doc.getCurrentController().getViewCursor()
			c.gotoRange(self.previous_view_cursor, False)
		
		# Apply the highlight if a range is provided (implies on=True)
		if range is not None:
			color = int('0x00'+self.highlight_color, 16)
			c = self.doc.Text.createTextCursor()
			c.gotoStart(False)
			c.goRight(range[0], False)
			c.goRight(range[1]-range[0], True)
			
			# Save the current background values. Needs to split down to TextPortions
			old_color = []
			old_range = []
			n = c.createEnumeration()
			while n.hasMoreElements():
				p = n.nextElement()
				f = p.createEnumeration()
				while f.hasMoreElements():
					t = f.nextElement()
					old_color.append(t.CharBackColor)
					old_range.append(t)
			
			self.highlighted_range = (old_range, old_color)
			
			c.CharBackColor = color
			c.collapseToStart()
			
			# Save view cursor
			v = self.doc.getCurrentController().getViewCursor()
			self.previous_view_cursor = v.getStart()
			v.gotoRange(c.getStart(), False)
			
	
	def getAllFields(self):
		"""Returns a `dict` of all Bibendum fields in the document, and the next available field index
		(Bibendum fields are numbered to be unique). The keys are the field names and the values are `dict`\ s with
		the following structure::
		
		   {'name': field_name, 'fieldmaster': OOoField, 'properties': properties, 'index'; index}
		
		The fields that have children, i.e. which have xref fields pointing to, also have a `children` key
		with a list of children field names.
		
		The function also remove all the Bibendum masters with no dependent field.
		"""
		
		OOoFieldPrefix = 'com.sun.star.text.fieldmaster.User.'
		
		masterNames = self.doc.TextFieldMasters.ElementNames
		fields = dict()
		indices = list()
		for m in masterNames:
			if m.startswith(OOoFieldPrefix+self.bibendumFieldPrefix):
				
				OOoField = self.doc.TextFieldMasters.getByName(m)
				# Remove the field masters that are not used anymore
				if OOoField.DependentTextFields is None or len(OOoField.DependentTextFields)==0:
					OOoField.dispose()
				
				field_name = m.replace(OOoFieldPrefix, '', 1)
				index, properties = self.decodeField(field_name)
				indices.append(index)
				fields[field_name] = {'name': field_name, 'fieldmaster': OOoField, 'properties': properties, 'index': index}
		
		for k, f in fields.iteritems():
			if f['properties']['fieldtype']=='xref':
				xref = f['properties']['fieldxref']
				if not fields[xref].has_key('xref'):
					fields[xref]['children'] = list()
				fields[xref]['children'].append( k )
		
		if len(indices)==0:
			i = 0
		else:
			i = max(indices)+1
		
		return fields, i
		
	
	def insertField(self, range, properties, text):
		"""Insert a field in place of *range* (a tuple of cursor positions), setting the *properties* (a dictionnary) and text (a Bibendum formatted text).
		
		Note: if replacing a list of ranges, you should always start by the one with the greatest cursor index.
		"""
		
		c = self.doc.Text.getStart()
		c.goRight(range[0], False)
		c.goRight(range[1]-range[0], True)
		
		self._insertFieldAtCursor(c, properties, text)
	
	def insertFieldHere(self, properties, text):
		"""Inserts a field in place of the current selection."""
		
		tr = self.doc.getCurrentController().getSelection().getByIndex(0)
		c  = self.doc.Text.createTextCursorByRange(tr)
		
		self._insertFieldAtCursor(c, properties, text)
	
	def _insertFieldAtCursor(self, c, properties, text, index=None):
		
		if index is None:
			_, index = self.getAllFields()
		
		for i, t in enumerate(text):
			
			if t[0]=='\n':
				self.doc.Text.insertControlCharacter(c, PARAGRAPH_BREAK, True)
				c.collapseToEnd()
				continue
			
			if i==0:
				# This is a 'cite' field
				p = dict(properties)
				p['fieldtype'] = 'cite'
				field_name = self.encodeField(index, p)
				fieldmain_name = field_name
			else:
				# This is a 'xref' field
				p = dict()
				p['fieldtype'] = 'xref'
				p['fieldxref'] = fieldmain_name
				field_name = self.encodeField(index, p)
				
			
			xMaster = self.doc.createInstance("com.sun.star.text.fieldmaster.User")
			xMaster.Name = field_name
			xMaster.Content = t[0]
			
			xUserField = self.doc.createInstance("com.sun.star.text.textfield.User")
			xUserField.attachTextFieldMaster(xMaster)
			
			if i==0:
				self.doc.Text.insertTextContent(c, xUserField, True)
			else:
				self.doc.Text.insertTextContent(c, xUserField, False)
			
			c.goLeft(1, True)
			self._setStyle(c, t[1])
			c.collapseToEnd()
			
			index += 1
		
	def _setStyle(self, cursor, style_dict):
		"""Applies the style defined in `style_dict` (Bibendum format) to the `object`.
		The `object` is for example an OOo cursor."""
		
		cursor.setAllPropertiesToDefault()
		for k, v in style_dict.iteritems():
			try:
				if k=='bold' and v:
					cursor.setPropertyValue('CharWeight', 150.)
				elif k=='italics' and v:
					cursor.setPropertyValue('CharPosture', 2)
				elif k=='underline' and v:
					cursor.setPropertyValue('CharUnderline', 1)
				elif k=='case':
					cursor.setPropertyValue('CharCaseMap', {'normal': 0, 'upper': 1, 'lower': 2, 'title': 3, 'smallcaps': 4}[v])
				elif k=='color':
					cursor.setPropertyValue('CharColor', int('0x00'+v, 16))
				elif k=='margin':
					cursor.setPropertyValue('ParaTopMargin', int(1000*v[0]))
					cursor.setPropertyValue('ParaRightMargin', int(1000*v[1]))
					cursor.setPropertyValue('ParaBottomMargin', int(1000*v[2]))
					cursor.setPropertyValue('ParaLeftMargin', int(1000*v[3]))
				elif k=='indent':
					cursor.setPropertyValue('ParaFirstLineIndent', int(1000*v))
				elif k=='char_style':
					cursor.setPropertyValue('CharStyleName', v)
				elif k=='para_style':
					cursor.setPropertyValue('ParaStyleName', v)
			except:
				pass
	
	def deleteField(self, field):
		"""Deletes the field, i.e. the master field and all the occurrences in the text.
		The `field` argument is a ``dict`` as returned by :meth:`getAllFields()`."""
		
		try:
			for f in field['fieldmaster'].DependentTextFields:
				f.dispose()
			field['fieldmaster'].dispose()
		except Exception, e:
			return False, e
		
		return True, None
	
	def updateField(self, field, properties, text):
		"""Update the `field` using the given `properties` and `text`. The `field` must be a 
		`dict` as returned by :meth:`getAllFields()`.
		
		Returns `(True,None)` in case of success, or `(False,e)`, where `e` is the exception, in case of failure.
		"""
		
		fields, i = self.getAllFields()
		
		if not fields.has_key(field['name']):
			return False, LookupError('The field "%s" is not present')
		
		# Wipe the attached 'xref' fields if any
		if field.has_key('children'):
			for c in field['children']:
				self.deleteField(fields[c])
		
		for f in field['fieldmaster'].DependentTextFields:
			c = self.doc.Text.createTextCursorByRange(f.Anchor)
			self._insertFieldAtCursor(c, properties, text, i)
			i += 1
		field['fieldmaster'].dispose()
	
	def createDocumentStyles(self, char_styles, para_styles):
		"""Create the document wide styles if they don't already exist. Each argument is a ``dict`` which keys are the style names and
		values ares ``dict`` with the format properties as defined in :class:`bBase.text`."""
		
		AllStyles = self.doc.getStyleFamilies()
		CharStyles = AllStyles.getByName('CharacterStyles')
		ParaStyles = AllStyles.getByName('ParagraphStyles')
		
		for k, v in char_styles.iteritems():
			if k in CharStyles.getElementNames():
				continue
			xStyle = self.doc.createInstance("com.sun.star.style.CharacterStyle")
			self._setStyle(xStyle, v)
			CharStyles.insertByName(k, xStyle)
		
		for k, v in para_styles.iteritems():
			if k in ParaStyles.getElementNames():
				continue
			xStyle = self.doc.createInstance("com.sun.star.style.ParagraphStyle")
			self._setStyle(xStyle, v)
			ParaStyles.insertByName(k, xStyle)

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

def test_insertField():
	OOoBridge = bridge()
	ok, e = OOoBridge.connect({'type': 'pipe', 'name':'OOo_pipe'})
	if not ok:
		print e
		return
	
	p = {'cite_ref': 'smith:2009', 'type': 'a'}
	t = [('A portion of', {}),
	     ('\n', {}),
	     ('formatted', {'bold': True}),
	     (' text.', {})]
	
	OOoBridge.insertFieldHere(p, t)

#================================================================================


