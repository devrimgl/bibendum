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

import bBase
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
			self.dbc = MySQLdb.connect(host=self.host, user=self.user, passwd=self.password, db=self.db_name)
			self.db  = self.dbc.cursor()
		except Exception as e:
			return False, e
		
		return True, None
		
	
	def close(self):
		"""Close the connection."""
		
		self.db  = None
		self.dbc.close()
		self.dbc = None
	
	def _protect(self, s):
		return self.db.connection.escape_string(str(s))
	
	def _query(self, sql, *args):
		"""Executes a SQL query. In case of SELECT query, a tuple of lists is returned.
		The query can contain ``%s``, that will be replaced by the following arguments.
		Unlike the MySQLdb function, quotes must be included::
		
		   self._query("SELECT * FROM `%s` WHERE id=%s OR name='%s'", 'tableName', 1, 'toto "the zero"')
		
		The arguments are converted to strings and protected using :meth:`_protect`.
		"""
		
		targs = list()
		for a in args:
			targs.append(self._protect(a))
		sql = sql % tuple(targs)
		
		self.last_query = sql
		
		try:
			self.db.execute(sql)
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
	
	def _queryd(self, sql, *args):
		"""Same as :meth:`_query` but returns a list of ``dict``.
		"""
		
		targs = list()
		for a in args:
			targs.append(self._protect(a))
		sql = sql % tuple(targs)
		
		self.last_query = sql
		
		try:
			self.db.execute(sql)
		except Exception as e:
			self.last_query_exception = e
			return None
		self.last_query_exception = None
		
		result  = self.db.fetchall()
		description = self.db.description
		
		if description==None:
			return None
		
		field_names = [x[0] for x in description]
		
		n = len(description)
		
		if len(result)==0:
			return tuple([ list() for i in range(n) ])
		
		t = list()
		for row in result :
			t.append(dict(zip(description, row)))
		
		return t
	
	def insertEntry(self, entry, force=False):
		"""Inserts the :class:`bBase.entry` `e` in the database."""
		
		if not force:
			e = self.findDuplicates(entry)
			if len(e)>0:
				return False, (entry, e)
		
		
		citeRef = None
		id_entry = None
		while id_entry is None:
			citeRef = entry.make_ref(citeRef)
			
			ids, = self._query("SELECT id_entry FROM `%s` WHERE `cite_ref`=%s", (citeRef,))
			
			if len(ids) == 0 :
				sql = """INSERT INTO `%s` SET `cite_ref`="%s", 
				         `title`="%s", 
				         `author`="%s", 
				         `year`="%s",
				         `type`="%s", 
				         `creation_date`=NOW()"""
				args = (self.entry_table, citeRef, entry.title, entry.author.to_string(), entry.year, entry.type)
				self._query(sql, *args)
				id_entry = self.db.lastrowid
				break
			
		
		for name, value in entry.fields.iteritems():
			sql = """INSERT INTO `%s` SET 
			         `id_entry`="%s", 
			         `field_name`="%s", 
			         `field_value`="%s" """
			args = (self.field_table, id_entry, name, value)
			self._query(sql, *args)
		
		self.makeSearch(id_entry)
		
		return id_entry, tuple()
	
	def deleteEntry(self, x):
		"""Deletes an entry from the database. Actually all entries must be kept
		in the backup database. `x` can be a database id, a cite_ref or a :class:`bBase.entry` object.
		Returns ``True`` in case of success, and ``False`` otherwise."""
		
		sql = "SELECT `id_entry` FROM `%s` WHERE `id_entry`='%s' OR `cite_ref`='%s' LIMIT 1";
		args = (self.entry_table, x, x)
		id, = self._query(sql, *args)
		if len(id)==0:
			return False
		id = id[0]
		
		self.backupEntry(id, 'deleted')
		
		sql = "DELETE FROM `%s` WHERE id_entry='%s'"
		self._query(sql, self.entry_table, id)
		
		sql = "DELETE FROM `%s` WHERE id_entry='%s'"
		self._query(sql, self.field_table, id)
		
		return True
	
	def updateEntry(self, e):
		"""Updates the :class:`bBase.entry` `e` in the database. 
		Should backup the old entry, and create a new one if doesn't already exist.
		Returns ``True`` if the entry was updated and ``False`` if a new entry was created."""
		
		ids, = self._query("SELECT `id_entry` FROM `%s` WHERE `cite_ref`='%s'", self.entry_table, e.cite_ref)
		if len(ids) != 0 :
			
			id = ids[0]
			
			self.backupEntry(id, 'edit')
			
			# Update the original entry and fields
			sql = """UPDATE `%s` SET 
			         `title`='%s', 
			         `author`='%s', 
			         `year`="%s", 
			         `type`='%s' 
			         WHERE `id_entry`=%s """
			args = (self.entry_table, e.title, e.author.to_string(), e.year, e.style, id)
			self._query(sql, *args)
			
			for fn, fv in e.fields.iteritems():
				sql = "SELECT `id_field` FROM `%s` WHERE id_entry=%s AND field_name='%s'"
				res, = self._query(sql, self.field_table, id, fn)
				if len(res) > 0 :
					idf = res[0]
					
					sql = """UPDATE `%s` SET `field_value`='%s' 
					         WHERE `id_field`=%s """
					args = (self.field_table, fv, idf)
					self._query(sql, *args)
				else:
					sql = """INSERT INTO `%s` SET 
					         `id_entry`="%s", 
					         `field_name`='%s', 
					         `field_value`='%s' """
					args = (self.field_table, id, fn, fv)
					self._query(sql, *args)
				
			return True
			
		else:
			self.insertEntry(e, True)
			return False
		
	
	def getEntry(self, x):
		"""Retrieve an entry from the database. `x` can be a database id, a cite_ref
		or a :class:`bBase.entry` object. Returns a filled :class:`bBase.entry` object.
		Returns ``None`` if the entry cannot be found."""
		
		sql = "SELECT * FROM `%s` WHERE id_entry='%s' OR cite_ref='%s'"
		args = (self.entry_table, x, x)
		res = self._queryd(sql, *args)
		if res is None or len(res)==0:
			return None
		res = res[0]
		
		sql = "SELECT * FROM `%s` WHERE id_entry=%s"
		args = (self.field_table, res['id_entry'])
		k, v = self._query(sql, *args)
		res['fields'] = dict(zip(k, v))
		
		e = bBase.entry(res)
		
		return e
	
	def findDuplicates(self, e, strict=True):
		"""Returns a list of :class:`bBase.entry` objects that
		are potential duplicates of `e`. If `strict` is ``True``, a duplicate has the same authors, year and title.
		If ``strict=False``, first author must be the same, year must be the same, and at least 50% of the word of
		the title must be the same."""
		
		if strict:
			author_surnames = "#".join([("%|%| "+x['surname']+" |%") for x in e.author])
			sql = "SELECT id_entry FROM `%s` WHERE author LIKE '%s' AND year=%s AND title='%s'"
			args = (self.entry_table, author_surnames, e.year, e.title)
			id_entry, = self._query(sql, *args)
		else:
			sql = "SELECT id_entry, title FROM `%s` WHERE LOWER(author) REGEXP '^[^|]+\\|[^|]+\\| *%s *\\|.*' AND year=%s"
			args = (self.entry_table, e.author[0]['surname'].lower(), e.year)
			ids, titles = self._query(sql, *args)
			id_entry = list()
			for id, title in zip(ids, titles):
				n, nA, nB = self.wordCorrelation(title, e.title)
				if (n/nA*100.)>=50.:
					id_entry.append(id)
		
		duplicates = list()
		for id in id_entry:
			duplicates.append( self.getEntry(id) )
		
		return duplicates
	
	def makeSearch(self, x):
		"""Creates the easy search string and insert it or update it in the database."""
		
		e = self.getEntry(x)
		if e.fields.has_key('journal'):
			journal = self.getJournal(e.fields['journal'])
			
		sql = "INSERT INTO `%s` SET id_entry=%s, author='%s', year=%s, journal='%s'"
		args = (self.search_table, e.id_entry, e.author, e.year, journal['id_journal'])
	
	def getJournal(self, journal, strict=True):
		"""Returns a ``dict`` with the alternative versions of a journal's title: long, pubmed,
		iso or short. If a version is empty in the database, the key should not be present in the returned ``dict``.
		The `journal` argument must be one of the versions of the journal's title.
		The `strict` flag may allow to get only best matches for journal titles."""
		
		if strict:
			sql = "SELECT * FROM `%s` WHERE `iso`='%s' OR `long`='%s' OR `pubmed`='%s' OR `short`='%s'"
			args = (self.journal_table, journal, journal, journal, journal)
			res = self._queryd(sql, *args)
			if res is None or len(res)==0:
				return None
			else:
				j = res[0]
			
		else:
			pass
		
		journal = dict()
		for k, v in j.iteritems():
			if v is None or len(v.strip())==0:
				continue
			else:
				journal[k] = v
		
		return journal
		
	
	def naturalSearch(self, q, limit=100):
		"""**Abstract** Searches in the database using a :class:`query` object. Must build the corresponding
		query for the specific implementation. This includes converting "*" into the specific query language wildcare.
		The expected behaviour is to return a first list of entries that satisfy all the criterion and a complementary list
		of partial matches sorted by decreasing relevance. The `limit` argument is used to limit the total number of matches."""
		raise NotImplementedError()
	
	def createTables(self):
		"""**Abstract** Create the tables. Wipe them if already exist."""
		raise NotImplementedError()
	
	

