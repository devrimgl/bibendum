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
		except Exception, e:
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
		except Exception, e:
			self.last_query_exception = e
			return False
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
		except Exception, e:
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
	
	def backupEntry(self, id, reason):
		"""Save an entry in the database by serializing an entry object as ``dict``."""
		
		e = self.getEntry(id)
		serialized_entry, serialization_type = self.serializeEntry(e, method="python_repr")
		
		sql = """
		  INSERT INTO `%s` SET
		    `entry_data`='%s',
		    `serialization`='%s',
		    `reason`='%s',
		    backup_date=NOW()
		    """
		args = (self.backup_table, serialized_entry, serialization_type)
		self._query(sql, *args)
		
	
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
			journal_all = list()
			for k in ['short', 'pubmed', 'long']:
				if journal.has_key(k):
					journal_all.append(journal[k])
			journal_all = ", ".join(journal_all)
			
		sql = "INSERT INTO `%s` SET id_entry=%s, author='%s', n_author=%s, year=%s, journal='%s' ON DUPLICATE KEY UPDATE"
		args = (self.search_table, e.id_entry, e.author, len(e.author), e.year, journal_all)
		self._query(sql, *args)
	
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
		"""Searches in the database using a :class:`query` object. Builds the corresponding
		query for the specific implementation and returns a list of entries sorted by relevance.
		
		The "*" in the query strings are replaced by "%".
		"""
		
		#-- Get a list of complete matches
		
		sql = "SELECT id_entry FROM `%s` WHERE 1" % self._protect(self.search_table)
		
		if q.author_names is not None and len(q.author_names)!=0:
			sql += " AND author LIKE '%s'" % self._protect("%".join(q.author_names))
		
		if q.year is not None:
			sql += " AND year=%d" % q.year
		
		if q.journal is not None:
			sql += " AND journal LIKE '%%%s%%'" % self._protect(q.journal)
		
		sql += " LIMIT %d" % limit
		
		ids_main, = self._query(sql)
		limit = limit-len(ids_main)
		
		if limit<=0:
			return [self.getEntry(x) for x in ids_main], []
		
		#-- Get a list of partial matches
		
		sql = list()
		
		for i, a in enumerate(q.author_names):
			
			a = a.replace("*", "%")
			
			if i==0:
				rank = q.RANK['firstauthor']
			else:
				rank = q.RANK['author']
			sql.append("SELECT id_entry, %f AS `rank` FROM `%s` WHERE author LIKE '%s'" %
			           (rank, self._protect(self.search_table), self._protect(a)))
		
		if q.n_authors<0:
			sql.append("SELECT id_entry, %f AS `rank` FROM `%s` WHERE n_authors>=%d" % (q.RANK['number_of_authors'], self._protect(self.search_table), -q.n_authors))
		else:
			sql.append("SELECT id_entry, %f AS `rank` FROM `%s` WHERE n_authors=%d" % (q.RANK['number_of_authors'], self._protect(self.search_table), q.n_authors))
		
		if q.year is not None:
			sql.append("SELECT id_entry, %f AS `rank` FROM `%s` WHERE year=%d" % (q.RANK['year'], self._protect(self.search_table), q.year))
		
		if q.journal is not None:
			sql.append("SELECT id_entry, %f AS `rank` FROM `%s` WHERE journal LIKE '%%%s%%'" % (q.RANK['journal'], self._protect(self.search_table), q.year))
		
		sql = "\n\nUNION ALL\n\n".join(sql)
		
		sql = "SELECT id_entry, SUM(rank) AS rank FROM (\n%s\n) AS t WHERE id_entry NOT IN(%s) GROUP BY id_entry ORDER BY rank DESC LIMIT %d" % (sql, ", ".join([str(x) for x in ids_main]), limit)
		
		ids_cmpl, ranks = self._query(sql)
		
		return [self.getEntry(x) for x in ids_main], [self.getEntry(x) for x in ids_cmpl]
	
	def createTables(self, wipe=False):
		"""Create the tables. Wipe them if already exists and `wipe`=``True``. Returns ``True, None, None`` in case
		of success, or ``False``, the faulty query and exception otherwise."""
		
		if wipe:
			if self._query("DROP TABLE IF EXISTS `%s`" % self._protect(self.entry_table))==False:
				return False, self.last_query, self.last_query_exception
		sql = """
		  CREATE TABLE IF NOT EXISTS `%s` (
		    `id_entry` INT NOT NULL AUTO_INCREMENT,
		    `cite_ref` VARCHAR( 256 ) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
		    `type` VARCHAR( 256 ) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
		    `title` TEXT NOT NULL ,
		    `author` TEXT NOT NULL ,
		    `year` INT NOT NULL ,
		    `creation_date` DATETIME NOT NULL ,
		    UNIQUE KEY (`id_entry`),
		    UNIQUE KEY (`cite_ref`(32))
		  ) ENGINE = MYISAM CHARACTER SET utf8 COLLATE utf8_general_ci 
		  """ % self._protect(self.entry_table)
		if self._query(sql)==False:
			return False, self.last_query, self.last_query_exception
		
		if wipe:
			if self._query("DROP TABLE IF EXISTS `%s`" % self._protect(self.field_table))==False:
				return False, self.last_query, self.last_query_exception
		sql = """
		  CREATE TABLE IF NOT EXISTS `%s` (
		    `id_field` INT NOT NULL AUTO_INCREMENT,
		    `id_entry` INT NOT NULL, `field_name` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
		    `field_value` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
		    UNIQUE KEY (`id_field`)
		  ) ENGINE = MyISAM CHARACTER SET utf8 COLLATE utf8_general_ci
		  """ % self._protect(self.field_table)
		if self._query(sql)==False:
			return False, self.last_query, self.last_query_exception
		
		if wipe:
			if self._query("DROP TABLE IF EXISTS `%s`" % self._protect(self.journal_table))==False:
				return False, self.last_query, self.last_query_exception
		sql = """
		  CREATE TABLE IF NOT EXISTS `%s` (
		    `id_journal` INT NOT NULL AUTO_INCREMENT ,
		    `iso` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
		    `long` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
		    `pubmed` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
		    `short` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
		    UNIQUE KEY ( `id_journal` ),
		    INDEX ( `iso` ( 128 ) )
		  ) ENGINE = MYISAM CHARACTER SET utf8 COLLATE utf8_general_ci
		  """ % self._protect(self.journal_table)
		if self._query(sql)==False:
			return False, self.last_query, self.last_query_exception
		
		if wipe:
			if self._query("DROP TABLE IF EXISTS `%s`" % self._protect(self.search_table))==False:
				return False, self.last_query, self.last_query_exception
		sql = """
		  CREATE TABLE IF NOT EXISTS `%s` (
		    `id_search` INT NOT NULL AUTO_INCREMENT ,
		    `id_entry` INT NOT NULL,
		    `author` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
		    `n_author` INT NULL,
		    `year` INT NULL,
		    `journal` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
		    UNIQUE KEY ( `id_search` ),
		    INDEX (`id_entry`)
		  ) ENGINE = MYISAM CHARACTER SET utf8 COLLATE utf8_general_ci
		  """ % self._protect(self.search_table)
		if self._query(sql)==False:
			return False, self.last_query, self.last_query_exception
		
		if wipe:
			if self._query("DROP TABLE IF EXISTS `%s`" % self._protect(self.backup_table))==False:
				return False, self.last_query, self.last_query_exception
		sql = """
		  CREATE TABLE IF NOT EXISTS `%s`
		  (
		    `id_update` INT NOT NULL AUTO_INCREMENT,
		    `entry_data` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
		    `field_data` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
		    `backup_date` DATETIME NOT NULL,
		    `reason` VARCHAR( 16 ) NOT NULL,
		    UNIQUE (`id_field`)
		  ) ENGINE = MYISAM CHARACTER SET utf8 COLLATE utf8_general_ci
		  """ % self._protect(self.backup_table)
		if self._query(sql)==False:
			return False, self.last_query, self.last_query_exception
		
		return True, None, None
	

