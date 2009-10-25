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

"""This module is used to communicate with OpenOffice.org Writer using `PyUNO <http://udk.openoffice.org/python/python-bridge.html>`_."""

class bridge(_generic.bridge):
	"""Communication with OpenOffice.org Writer."""
	
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
		"""
		
		self.options = options
		
		self.unourl = "uno:%s" % options['type']
		if options['type']=='pipe':
			self.unourl += ",name=%s" % options['name']
		elif options['type']=='socket':
			self.unourl += ",host=%s,port=%s" % (options['host'], options['port'])
		self.unourl += ";urp;StarOffice.ComponentContext"
		
		try:
			ctx = self.resolver.resolve( self.unourl )
			self.smgr = ctx.ServiceManager
		except UnoException as e:
			return False, e
		else:
			return True, None
	