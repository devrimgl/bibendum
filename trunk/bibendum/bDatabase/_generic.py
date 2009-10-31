# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------
#    Bibendum's Database Abstract Class
#    
#    bDatabase/_generic.py,
#    this file is part of the Bibendum Reference Manager project
#    
#    Etienne Gaudrain <egaudrain@gmail.com>, 2009-10-30
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

class database:
	"""Abstract class for access to databases. The constructor must take ``dict`` containing the options.
	
	.. attribute:: last_query
	
	   The last executed query.
	
	.. attribute:: last_query_exception
	   
	   The exception caused by the last executed query (if failed).
	"""
	
	last_query = None
	last_query_exception = None
	
	def open(self):
		"""**Abstract** Establish a connection. Returns ``(True,None)`` in case of 
		success and ``(False,error)`` where ``error`` is an :class:`Exception` in case of failure."""
		raise NotImplementedError()
	
	def close(self):
		"""**Abstract** Close the connection."""
		raise NotImplementedError()
	
	def insertEntry(self, e, force=False):
		"""**Abstract** Inserts the :class:`bBase.entry` `e` in the database."""
		raise NotImplementedError()
	
	def insertEntries(self, entries, force=False):
		"""Inserts a ``list`` of :class:`bBase.entry` objects If the `force` switch is ``True``,
		the entries are inserted even if they are thought to be duplicates."""
		
		ids = list()
		duplicates = list()
		for e in entries:
			id, d = self.insertEntry(e, force)
			if e is None or len(e)==0:
				ids.append(id)
			else:
				duplicates.extend(d)
		
		return ids, duplicates
	
	def deleteEntry(self, x):
		"""**Abstract** Deletes an entry from the database. Actually all entries must be kept
		in the backup database. `x` can be a database id, a cite_ref or a :class:`bBase.entry` object."""
		raise NotImplementedError()
	
	def updateEntry(self, e):
		"""**Abstract** Updates the :class:`bBase.entry` `e` in the database. 
		Should backup the old entry, and create a new one if doesn't already exist."""
		raise NotImplementedError()
	
	def getEntry(self, x):
		"""**Abstract** Retrieve an entry from the database. `x` can be a database id, a cite_ref
		or a :class:`bBase.entry` object. Returns a filled :class:`bBase.entry` object."""
		raise NotImplementedError()
	
	def findDuplicates(self, e, strict=True):
		"""**Abstract** Returns a list of :class:`bBase.entry` objects that
		are potential duplicates of `e`. If `strict` is ``True``, a duplicate has the same authors, year and title.
		If ``strict=False``, first author must be the same, year must be the same, and at least 50% of the word of
		the title must be the same."""
		raise NotImplementedError()
	
	def getJournal(self, journal, strict=True):
		"""**Abstract** Returns a ``dict`` with the alternative versions of a journal's title: long, pubmed,
		iso or short. If a version is empty in the database, the key should not be present in the returned ``dict``.
		The `journal` argument must be one of the versions of the journal's title.
		The `strict` flag may allow to get only best matches for journal titles."""
		raise NotImplementedError()
	
	def naturalSearch(self, q, limit=100):
		"""**Abstract** Searches in the database using a :class:`query` object. Must build the corresponding
		query for the specific implementation. This includes converting "*" into the specific query language wildcare.
		The expected behaviour is to return a first list of entries that satisfy all the criterion and a complementary list
		of partial matches sorted by decreasing relevance. The `limit` argument is used to limit the total number of matches."""
		raise NotImplementedError()
	
	def createTables(self):
		"""**Abstract** Create the tables. Wipe them if already exist."""
		raise NotImplementedError()
	
	

#============================================================================================

import re

reDate = re.compile('[0-9]{4}')
reEtal = re.compile('[^a-zA-Z0-9_-](et +al[^a-zA-Z0-9_]*)$')

class query:
	""":class:`query` objects are used to implement natural search. The user types in a
	string that is parsed, and then provided to the database :meth:`naturalSearch` implementation.
	The object allows ``dict``\ -like access. If an attribute is missing, it is set to ``None``.
	
	.. attribute:: author_names
	   
	   Author names (``string``) with prefix and possibly initials with no dot (e.g. "Patterson RD").
	
	.. attribute:: n_authors
	   
	   Number of authors. Negative number means "at least".
	
	.. attribute:: journal
	   
	   Journal's title in one of the known form (long, pubmed, iso, or short).
	
	.. attribute:: year
	   
	   The year (``int``).
	
	.. attribute:: q
	   
	   The original query string.
	   
	"""
	
	def __init__(self, x):
		
		self.author_names = None # author names with prefix and possibly initials with no dot (e.g. Patterson RD)
		self.n_authors = None # Number of authors
		self.journal = None # In one of the known formats
		self.year = None
		self.q = None
		
		if type(x)==type(str()):
			self.parseQuery(x)
		elif type(x)==type(self):
			self.from_dict(x.__dict__)
		else:
			raise TypeError('%s is not a valid type for query constructor.' % str(type(x)))
	
	def from_dict(self, x):
		keys = self.__dict__.keys()
		
		if x is not None:
			for k in keys:
				if x.has_key(k):
					object.__setattr__(self, k, x[k])
	
	def __getitem__(self, key):
		return self.__dict__[key]
	
	def __setitem__(self, key, value):
		if key not in self.__dict__.keys():
			raise IndexError('No new key can be created in citation objects.')
		self.__dict__[key] = value
		
		self._check_firstname()
	
	def parseQuery(self, q):
		"""Parses the string query `q` and fills the :class:`query` object. Any sequence of 4 digits will be
		interpreted a year. The year is expected to be used to separate authors from the journal title if provided.
		Author names must be separated by commas or "and" or "&". The "et al" keyword is used to indicate that there
		are more authors. The "*" symbol is accepted as wildcard."""
		
		self.q = q
		
		for c in '.()[]{}':
			q = q.replace(c, '')
		
		# Find a year
		m = reDate.findall(q)
		if len(m)!=0:
			authors, self.year, self.journal = q.partition(m[0])
			self.journal = self.journal.strip(' ,;')
			self.year = int(self.year)
		else:
			self.year = None
			self.journal = None
			authors = q
		
		authors = authors.strip(' ,;')
		
		# Search for et al.
		m = reEtal.findall(authors)
		if len(m)!=0:
			et_al = True
			authors, _, _ = authors.rpartition(m[0])
			authors = authors.strip(' ,;')
		else:
			et_al = False
		
		print authors
		authors = re.split('[,;]', authors)
		
		self.n_authors = 0
		self.author_names = list()
		for a in authors:
			a = a.strip(' ,;')
			if len(a)!=0:
				self.n_authors += 1
			self.author_names.append(a)
		
		if et_al:
			self.n_authors = - self.n_authors - 2
		
		if len( self.author_names )==0:
			self.author_names = None
	
	


#---------------------------

def test_query():
	
	q = query('patterson et al, 2006')
	print q.__dict__
	
	q = query('patterson rd, smith 2005 JASA')
	print q.__dict__




