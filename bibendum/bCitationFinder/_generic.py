# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------
#    Bibendum's Generic Citation Finder
#    
#    bCitationFinder/_generic.py,
#    this file is part of the Bibendum Reference Manager project
#    
#    Etienne Gaudrain <egaudrain@gmail.com>, 2009-10-28
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

import bTextProcessor

"""This module must defines a class :class:`finder` that is used to implement
method of search of citation in the text. Typically, citations can be searched for
in :mod:`natbib`\ -like format or in :mod:`plaintext`. Those class can also implement
the reverse mechanism."""

class finder:
	"""
	.. attribute:: implementedMethods
	   
	   A list of the implemented methods. In a non-abstract implementation, only some
	   of the recommended methods may be implemented. This can be used to avoid to raise
	   the ``NotImplementedError`` exception.
	"""
	
	implementedMethods = []
	
	def __init__(self, textProcessor):
		self.textProcessor = textProcessor
	
	def findCitations(self):
		"""Returns a list of tuples ``(citation, range)`` where ``citation`` is a :class:`bBase.citation`
		object, and ``range`` is a range returned by a :mod:`bTextProcessor` implementation."""
		raise NotImplementedError()
	
	def findReflist(self):
		raise NotImplementedError()
	
	def findStyleDefinition(self):
		raise NotImplementedError()
	
	def revertCitations(self, citation):
		raise NotImplementedError()
	
	def revertReflist(self, reflist_options):
		raise NotImplementedError()
	
	def revertStyleDefinition(self, style):
		raise NotImplementedError()
	

