# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------
#    Bibendum's Base Classes
#    
#    bBase.py,
#    this file is part of the Bibendum Reference Manager project
#    
#    Etienne Gaudrain <egaudrain@gmail.com>, 2009-10-25
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

class text:
	"""This class provides an abstraction for formatted text.
	
	The Bibendum formatted text is a ``list`` of ``tuple``\ s. Each ``tuple`` contains the text itself and a ``dict`` defining the style::
	
	   [('The big ', {}),
	    ('bold', {'bold': True}),
	    (' text.', {})]
	
	The text items are concatenated to form the complete string. ``bTextProcessor`` implementations should implement the conversion of the Bibendum text.
	
	The constructor accepts the following syntaxes::
	
	   bBase.text('This is text')
	   bBase.text('This is text', {'bold': True})
	   bBase.text(['This is text ', 'in bold'], [{}, {'bold': True}])
	   bBase.text([('The big ', {}), ('bold', {'bold': True}), (' text.', {})])
	
	Note: the format is somewhat not practical but is handy for text processor that does not allow formatting variations inside fields.
	
	"""
	
	def __init__(self, txt='', style=None):
		
		LIST = type(list())
		TUPLE = type(tuple())
		
		if type(txt)==LIST and type(style)==LIST:
			self.t = zip(txt, style)
		elif type(txt)==LIST and type(style!=LIST):
			if style is None:
				if type(txt[0])==TUPLE:
					self.t = txt
				else:
					self.t = list()
					for x in txt:
						self.t.append( (x, dict()) )
			else:
				raise TypeError("If a list of tuples is supplied, no second argument should be provided (%s given)." % str(style))
		else:
			if style is None:
				self.t = [(txt, dict())]
			elif type(style)==type(dict()):
				self.t = [(txt, style)]
			else:
				raise TypeError("When 'txt' is not a list, 'style' should be None or a dict (%s given)." % str(style))
	
	def __str__(self):
		return "".join([x[0] for x in self.t])
	
	def __iter__(self):
		"""To implement iteration."""
		return self.t.__iter__()
	
	def append(self, txt, style=None, sep=''):
		"""Adds a portion of text with its format at the end of the string.
		
		The ``sep`` argument can be used to add a separator to the previous chunk of text so that the style of the separator is the one of the previous bit of text."""
		
		if style is None:
			style = dict()
		if len(self.t)!=0:
			self.t[-1] = (self.t[-1][0]+sep, self.t[-1][1])
		
		self.t.append((txt, style))
	
	def extend(self, t, sep=''):
		"""Extends the text with a list of formatted text or a `bBase.text` object."""
		
		if len(self.t)!=0:
			self.t[-1] = (self.t[-1][0]+sep, self.t[-1][1])
		if isinstance(t, text):
			self.t.extend(t.t)
		else:
			self.t.extend(t)
	
	def reduce(self):
		"""Concatenates all the consecutive portions of text that have the same format. Operates in place."""
		if len(self.t)==0:
			return
		
		nt = [self.t[0]]
		for i in range(1,len(self.t)):
			if self.t[i][1] == nt[-1][1]:
				nt[-1] = (nt[-1][0]+self.t[i][0], nt[-1][1])
			else:
				nt.append(self.t[i])
		
		self.t = nt
	
	def strip(self, chars=None):
		"""Applies the `strip()` method to the first and last items. See `Python string method <http://docs.python.org/library/stdtypes.html#str.strip>`_ for details.
		
		Operates in place."""
		self.lstrip(chars)
		self.rstrip(chars)
	
	def lstrip(self, chars=None):
		"""Applies `lstrip()` to the first item. See `Python string method <http://docs.python.org/library/stdtypes.html#str.lstrip>`_ for details.
		
		Operates in place."""
		self.t[0] = (self.t[0][0].lstrip(chars), self.t[0][1])
	
	def rstrip(self, chars=None):
		"""Applies `rstrip()` to the last item. See `Python string method <http://docs.python.org/library/stdtypes.html#str.rstrip>`_ for details.
		
		Operates in place."""
		self.t[-1] = (self.t[-1][0].rstrip(chars), self.t[-1][1])

#−−−−−−−−−−−−−−−
def test_text():
	print text('This is text').t
	print text('This is text', {'bold': True}).t
	print text(['This is text ', 'in bold'], [{}, {'bold': True}]).t
	print text([('The big ', {}), ('bold', {'bold': True}), (' text.', {})]).t
	txt = text('This is text')
	print txt.t
	txt.append('in bold', {'bold': True}, ' ')
	print txt.t
	
	txt.extend( text('More text.', {'italics': True}), '. ')
	print txt.t
	print txt
	
	txt = text('Not bold.', {})
	txt.append('Bold.', {'bold': True}, ' ')
	txt.append('Bold.', {'bold': True}, ' ')
	txt.append('Not bold.', {}, ' ')
	print txt.t
	txt.reduce()
	print txt.t
	
	txt = text(['   This is text ', 'in bold   '], [{}, {'bold': True}])
	txt.strip()
	print txt
	
	for x in txt:
		print x
	#~ print text('This is text', [{'bold': True}, {}])


#============================================================================================
if __name__=='__main__':
	test_text()


