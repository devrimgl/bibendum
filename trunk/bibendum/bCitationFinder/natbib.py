# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------
#    Bibendum's Natbib-like Citation Finder
#    
#    bCitationFinder/natbib.py,
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

import bBase
import bCitationFinder._generic
import re

"""Implements the conversion from natbib notation and back.

The current version has the limitation that optionnal arguments for
LaTeX commands in are not allowed. For example ``\citep[e.g.]{smith:2005}``
will **not** be recognized. You should use the ``\citealp`` method instead.

You can find more info on natbib `here <http://www.ctan.org/tex-archive/help/Catalogue/entries/natbib.html>`_ 
and a quick reference `there <http://merkel.zoneo.net/Latex/natbib.php>`_.
"""

class finder(bCitationFinder._generic.finder):
	
	implementedMethods = ['findCitations', 'findReflist', 'findStyleDefinition', 'revertCitations', 'revertReflist', 'revertStyleDefinition']
	
	def __init__(self, textProcessor):
		bCitationFinder._generic.finder.__init__(self, textProcessor)
		
		citet = re.compile("\\\\citet\\{[^}]*\\}")
		citep = re.compile("\\\\citep\\{[^}]*\\}")
	
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