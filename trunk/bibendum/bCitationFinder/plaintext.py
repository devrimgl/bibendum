# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------
#    Bibendum's Plain Text Citation Finder
#    
#    bCitationFinder/plaintext.py,
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

"""The `plaintext` implementation of the :mod:`bCitationFinder` module is meant to detect 
citations in plain text (surprising isn't it?). Only citations in the author-year format can be
found. The finder recognises "et al.", "and" and "&", and tries to determine the type of citation.

I also parses the citation to build a search string for the :mod:`bDatabase` search function.
"""

class finder(bCitationFinder._generic.finder):
	
	implementedMethods = ['findCitations']
	
	def __init__(self, textProcessor):
		bCitationFinder._generic.finder.__init__(self, textProcessor)
		
		lowercase = bBase.LOWERCASE
		uppercase = bBase.UPPERCASE
		
		author  = '((?:[vV]an |[vV]on |[dD]e |[dD]e la |[dD]el |[dD]ella )?(?:Mc)?[A-Z%s][a-z%s-]+)' % (uppercase, lowercase)
		authorI = '((?:[vV]an |[vV]on |[dD]e |[dD]e la |[dD]el |[dD]ella )?)((?:Mc)?[A-Z%s][a-z%s-]+)' % (uppercase, lowercase)
		date    = '([1-3][0-9]{3}[a-z]?)'
		dateI   = '([1-3][0-9]{3})[a-z]?'
		
		authorBlock = '%s(?:,? +(et al\.?)?|(?:, +%s)*,? +(?:&|and) +%s)?' % (author,author,author)
		dateBlock   = '%s(?:, +%s)*' % (date, date)
		dateBlock   = '(?:(?:%s)|(?:\\(%s\\)))' % (dateBlock, dateBlock)
		
		citation = '(\\(?'+authorBlock+',? '+dateBlock+'\\)?)'
		
		self.reCitation = re.compile(citation)
		self.reDateI    = re.compile(dateI)
		self.reDate     = re.compile(date)
		#~ self.reAuthorI  = re.compile(authorI)
	
	def findCitations(self):
		"""Search for citations in plain text. For each candidate, defines a search string and
		tries to guess the type of citation.
		
		Returns a list of ``(citation, range)`` where ``citation`` is a :class:`bBase.citation` object and
		``range`` is tuple of cursor indices.
		"""
		
		ls = self.textProcessor.findRegexp(self.reCitation)
		
		# For each citation candidate, determine the type, authors and year
		citations = list()
		for c in ls:
			txt, span = c
			
			cite = bBase.citation()
			
			cite.text = bBase.text(txt)
			
			# Type
			if txt.startswith('(') and txt.endswith(')'):
				type = 'p'
				if len(txt.split(','))-1>1:
					type += '*'
			else:
				if txt.find('(')!=-1 and txt.find(')')!=-1:
					type = 't'
					if len(txt.split(','))-1>0:
						type += '*'
				else:
					type = 'i'
					if len(txt.split(','))-1>1:
						type += '*'
			txt = txt.strip('()')
			
			for x in ['Van', 'De', 'Von', 'Del', 'Della']:
				if txt.startswith(x+' '):
					type = type.capitalize()
			
			# Search string
			cite.search = dict()
			cite.search['search_type'] = 'string'
			
			m = reDateI.search(txt)
			year = m.group(0)
			m = reDate.search(txt)
			txt = txt.replace(m.group(0), '')
			
			for x in '()':
				txt = txt.replace(x, '')
			txt = txt.strip(',. ')
			
			if txt.endswith('et al'):
				txt = txt.replace('et al', '')
				cite.etal = True
			txt = txt.strip(',. ')
			
			txt = txt.replace(' and ', ', ')
			txt = txt.replace(' & ', ', ')
			txt = txt.replace(', , ', ', ')
			
			cite.search['search_string'] = txt+", "+year
			
			citations.append((cite, span))
		
		return citations
	
