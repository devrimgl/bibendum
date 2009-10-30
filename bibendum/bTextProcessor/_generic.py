# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------
#    Bibendum's Text Processor generic module
#    
#    bTextProcessor/_generic.py,
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

import pickle
import base64

"""This module is used to communicate with text processors such as MS Word or OpenOffice.org.

Imports :mod:`pickle`, :mod:`base64`."""

#====================================================================

# Warning: Any change will endanger backward compatibility. In any event, '_' must stay first.
FIELD_PROTECTED_CHARS = '_=+-/\\?![]{}()@#<>,.:;|%&*'
FIELD_PROTECTION_TABLE = list()
for c in FIELD_PROTECTED_CHARS:
	FIELD_PROTECTION_TABLE.append((c, '_x%03dx_' % ord(c)))

#====================================================================
class bridge:
	"""Generic class for communication with text processor. This class defines the method that needs to be implemented in the specific text processor classes.
	
	.. attribute:: connected
	   
	   Weither the connection is established or not (``True`` or ``False``).
	
	.. attribute:: highlighted_range
	   
	   The information of the currently highlighted text range: either ``None`` or ``(range, original_color)``.
	   The original color should be stored in the text-processor specific format. The range is a tuple with the two cursor positions.
	
	.. attribute:: highlight_color
	   
	   The color for highlighting. A string in hexa containing the RGB values (*e.g.* 'ffdd66').
	   This format will be converted into the text-processor specific format by the :meth:`highlight` method.
	
	.. attribute:: previous_view_cursor
	   
	   Previous view cursor position. Either ``None`` or a text-processor specific representation of the view cursor.
	
	.. attribute:: bibendumFieldPrefix
	   
	   The prefix used for Bibendum field names.
	
	.. automethod:: _protectFieldName
	.. automethod:: _unprotectFieldName
	
	"""
	
	connected = False
	
	highlighted_range = None
	highlight_color   = 'ffff66'
	previous_view_cursor = None
	
	bibendumFieldPrefix  = 'Bibendum_'
	
	def connect(self, options=None):
		"""**Abstract method**. Implementation must establish connection with the text processor
		and return a boolean reflecting the success of the operation, and the error that occurred if any
		(or ``None`` otherwise)."""
		
		raise NotImplementedError()
	
	def findRegexp(self, regexp):
		"""**Abstract method**. Implementation must return a list of matches using the provided regular expression. The list format is::
		
		   [(matched_text, (start_index, end_index), groups), ...]
		
		The indices must be compatible with cursor operations.
		
		If the text processor handles regular expression search, this functionnality should be used, possibly after translating some parts of the regular expression.
		
		Finally, *regexp* can be either a string or a regular expression object.
		
		Note: The matches list **must** be returned starting with the last one.
		"""
		
		raise NotImplementedError()
	
	def highlight(self, on, range=None):
		"""**Abstract method**. Implementation should highlight (*on*\ =True) or not (*on*\ =False) the *range*. If a range was previously
		highlighted it is set back to normal first. If no range is provided and *on*\ =False,
		any previous highlight is removed.
		
		See also :attr:`highlighted_range` , :attr:`highlight_color` and :attr:`previous_view_cursor`.
		"""
		
		raise NotImplementedError()
	
	def insertField(self, range, properties, text):
		"""**Abstract method**. Implementation should insert a field containing the *properties* and showing
		the formatted *text* in place of *range*. The latter is a tuple of cursor indices."""
		
		raise NotImplementedError()
	
	def _protectFieldName(self, s):
		"""Field names are base64 encoded which means that some characters may remain problematic
		for some text processors. This function replaces some characters with their ASCII code using
		an escape sequence."""
		
		for c, p in FIELD_PROTECTION_TABLE:
			s = s.replace(c, p)
		return s
	
	def _unprotectFieldName(self, s):
		"""Does the reverse operation than :meth:`_protectFieldName`."""
		
		for c, p in FIELD_PROTECTION_TABLE:
			s = s.replace(p, c)
		return s
	
	def encodeField(self, i, d):
		"""Encodes a dictionary of properties into a field name using serialization.
		Practically any object is can be embedded, but it is recommended to keep the size small and to avoid fancy objects
		that wouldn't serialize properly (like context dependent objects).
		
		*i* provides the index of the field. This is used to ensure field names are unique.
		
		Returns a string."""
		
		s = pickle.dumps(d, 2)
		s = base64.b64encode(s)
		
		s = self.bibendumFieldPrefix + ("%d_" % i) + self._protectFieldName(s)
		
		return s
	
	def decodeField(self, s):
		"""Decodes a field name *s*. Returns the field index and the dictionary of properties."""
		
		if not s.startswith(self.bibendumFieldPrefix):
			return None
		
		s = s.split('_')
		i = int(s[1])
		s = self._unprotectFieldName("_".join(s[2:]))
		d = pickle.loads( base64.b64decode(s) )
		
		return i, d

#======================================================================================

def test_field_protect():
	s = '_abc_=+-/\\?![]{}()@#<>,.:;|%&*ABC___'
	b = bridge()
	
	sp = b._protectFieldName(s)
	print s
	print sp
	print b._unprotectFieldName(sp)
	

def test_field_encode():
	b = bridge()
	d = {'prop1': 'String', 'prop2': 'Fancy String ÇÁ+', 'prop3': 42.13258879, 'prop4': {'type': 'dict', 'value': 1}}
	i = 1
	
	s = b.encodeField(i, d)
	
	print i
	print d
	print "-"*30
	print s
	
	i, d = b.decodeField(s)
	
	print "-"*30
	print i
	print d
