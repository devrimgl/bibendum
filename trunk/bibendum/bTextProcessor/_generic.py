# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------
#    Bibendum's Text Processor generic module
#    
#    _generic.py,
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

"""This module is used to communicate with text processors such as MS Word or OpenOffice.org."""

class bridge:
	"""Generic class for communication with text processor. This class defines the method that needs to be implemented in the specific text processor classes."""
	
	def __init__(self):
		"""The __init__ method of the specific implementation should establish connection with the text processor."""
		pass
	
	def connect(self, options=None):
		"""Establish connection with the text processor."""
		pass
	