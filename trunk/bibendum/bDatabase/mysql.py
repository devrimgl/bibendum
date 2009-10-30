# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------
#    Bibendum's Database Class MySQL implementation
#    
#    bDatabase/mysql.py,
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

import bDatabase._generic
import MySQLdb 


class database(bDatabase._generic.database):
	"""Implementation of the :class:`bDatabase._generic.database` class for MySQL. `options` must specify:
	
	   * 'host': the address of the host server.
	   * 'user': the name of the user used for connection to the server.
	   * 'password': the password associated with that username.
	   * 'db_name': the database name.
	   * 'entry_table': the name of the entry table.
	   * 'field_table': the name of the field table.
	   * 'search_table': the name of the easy search table
	   * 'backup_table': the table for backup
	   * 'journal_table': the table that contains the list of journals
	
	This module depends on mysql-python module :mod:`MySQLdb` (`Pypi page <http://pypi.python.org/pypi/MySQL-python>`_
	and `project page <http://mysql-python.sourceforge.net/>`_).
	"""
	
	def __init__(self, options):
		self.host = options['host']
		self.user = options['user']
		self.password = options['password']
		self.db_name = options['db_name']
		
		self.entry_table = options['entry_table']
		self.field_table = options['field_table']
		self.search_table = options['search_table']
		self.backup_table = options['backup_table']
		self.journal_table = options['journal_table']
		
		
		self.dbc = None
		self.db  = None
	
	def open(self):
		"""Establish a connection. Returns ``(True,None)`` in case of 
		success and ``(False,error)`` where ``error`` is an :class:`Exception` in case of failure."""
		
		try:
			self.dbc = MySQLdb.connect(host=self.host, usr=self.user, passwd=self.password, db=self.db_name)
			self.db  = self.dbc.cursor()
		except Exception as e:
			return False, e
		
		return True, None
		
	
	def close(self):
		"""Close the connection."""
		
		self.db  = None
		self.dbc.close()
		self.dbc = None
	
	def _query(self, sql, args=None):
		"""Executes a SQL query. In case of SELECT query, a tuple of lists is returned.
		"""
		
		try:
			self.db.execute(sql, args)
		except Exception as e:
			self.last_query_exception = e
			return None
		self.last_query_exception = None
		
		result  = self.db.fetchall()
		description = self.db.description
		
		if description==None:
			return None
		
		n = len(description)
		
		if len(result)==0:
			return tuple([ list() for i in range(n) ])
		
		t = list()
		for i in range(n) :
			t.append(list())
		for row in result :
			for i in range(n) :
				t[i].append(row[i])
		
		return tuple(t)
	
	def insertEntry(self, entry, force=False):
		"""Inserts the :class:`bBase.entry` `e` in the database."""
		
		if force:
			e = self.findDuplicates(entry)
			if len(e)>0:
				return False, (entry, e)
		
		
		citeRef = None
		id_entry = None
		while id_entry is None:
			citeRef = entry.make_ref(citeRef)
			
			ids, = self._query("SELECT id_entry FROM `%s` WHERE `cite_ref`=\"%s\"", [self.entry_table, citeRef])
			
			if len(ids) == 0 :
				sql = """INSERT INTO `%s` SET `cite_ref`='%s', 
				         `title`='%s', 
				         `author`='%s', 
				         `year`=%s,
				         `type`='%s', 
				         `creation_date`=NOW()"""
				args = [self.entry_table, citeRef, entry.title, entry.author.to_string(), entry.year, entry.type]
				self._query(sql, args)
				id_entry = self.db.lastrowid
				break
			
		
		for name, value in entry.fields.iteritems():
			sql = """INSERT INTO `%s` SET ".
			       "id_entry=".$id_entry.", ".
			       "field_name='".$this->protect($name)."', ".
			       "field_value='".$this->protect($value)."'"""
			args = [self.field_table,]
			mysql_query($sql, $this->dbh);
		}
		
		return array($id_entry, array());
	
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
	
	

