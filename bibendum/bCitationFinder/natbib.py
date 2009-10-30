# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------
#    Bibendum's Natbib-like Citation Finder
#    
#    bCitationFinder/natbib.py,
#    this file is part of the Bibendum Reference Manager project
#    
#    Etienne Gaudrain <egaudrain@gmail.com>, 2009-10-29
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

class finder(bCitationFinder._generic.finder):
	
	"""
	Implements the conversion from natbib notation and back.
	
	The current version has the limitation that optionnal arguments for
	LaTeX commands in are not allowed. For example ``\citep[e.g.]{smith:2005}``
	will **not** be recognized. You should use the ``\citealp`` method instead.
	
	You can find more info on natbib `here <http://www.ctan.org/tex-archive/help/Catalogue/entries/natbib.html>`_ 
	and a quick reference `there <http://merkel.zoneo.net/Latex/natbib.php>`_.
	"""
	
	implementedMethods = ['findCitations', 'findReflist', 'findStyleDefinition', 'revertCitations', 'revertReflist', 'revertStyleDefinition']
	
	def __init__(self, textProcessor):
		bCitationFinder._generic.finder.__init__(self, textProcessor)
		
		self.cite = re.compile("\\\\([cC])ite((?:al)?)([tp])(\\*?)\\{(.*?)\\}")
		self.citeauthor = re.compile("\\\\([cC])iteauthor(\\*?)\\{(.*?)\\}")
		self.citeyear   = re.compile("\\\\citeyear\\{(.*?)\\}")
		
		self.bibliographystyle = re.compile("\\\\bibliographystyle\\{(.*?)\\}")
		self.referencelist     = re.compile("\\\\bibliography((?:\\{(.*?)\\})?)")
	
	def findCitations(self):
		"""Returns a list of tuples ``(citation, range)`` where ``citation`` is a :class:`bBase.citation`
		object, and ``range`` is a range returned by a :mod:`bTextProcessor` implementation.
		
		Unlike natbib, the two commands ``\\citealt`` and ``\\citealt`` both produce the same result and
		are mapped on the 'i' citation type (see :attr:`citation.type` in :mod:`bBase`).
		
		The use of ``\\citetalias`` and ``\\citepalias`` is not supported.
		"""
		
		ls = self.textProcessor.findRegexp(self.cite)
		citations = list()
		for c in ls:
			txt, span, grps = c
			
			cite = bBase.citation()
			
			cite.cite_ref = [x.strip() for x in grps[4].split(',')]
			
			if grps[1]=='':
				if grps[2]=='t' or grps[2]=='p':
					cite.type = grps[2]
			else:
				cite.type = 'i'
			
			if grps[0].isupper():
				cite.type = cite.type.capitalize()
			
			if grps[3]=='*':
				cite.type += '*'
			
			cite.search = {'search_type': 'ref'}
			
			citations.append((cite, span))
		
		ls = self.textProcessor.findRegexp(self.citeauthor)
		for c in ls:
			txt, span, grps = c
			
			cite = bBase.citation()
			
			cite.cite_ref = [x.strip() for x in grps[4].split(',')]
			cite.type = 'a'
			
			if grps[0].isupper():
				cite.type = cite.type.capitalize()
			
			if grps[3]=='*':
				cite.type += '*'
			
			cite.search = {'search_type': 'ref'}
			
			citations.append((cite, span))
		
		ls = self.textProcessor.findRegexp(self.citeyear)
		for c in ls:
			txt, span, grps = c
			
			cite = bBase.citation()
			
			cite.cite_ref = [x.strip() for x in grps[4].split(',')]
			cite.type = 'y'
			
			cite.search = {'search_type': 'ref'}
			
			citations.append((cite, span))
		
		return citations
	
	def findReflist(self):
		"""Returns a list of tuples ``(reflist_options, range)`` where ``reflist_options`` is ``dict`` with
		options for the reference list.
		
		The natbib commande doesn't normally support options for the ``\\bibliography`` command. In the 
		Bibendum version, you can pass options using this syntax::
		
		   \\bibliography{option1=value1, option2=value2}
		
		Note: the spaces for option names and values are trimmed."""
		
		ls = self.textProcessor.findRegexp(self.referencelist)
		reflists = list()
		for c in ls:
			txt, span, grps = c
			
			options = dict()
			if grps[1] is not None:
				optionsL = [x.split('=') for x in grps[1].split(',')]
				
				for x in optionsL:
					if len(x)>1:
						options[x[0].strip()] = x[1].strip()
					else:
						options[x[0].strip()] = None
			
			reflists.append((options, span))
		
		return reflists
	
	def findStyleDefinition(self):
		"""``\\bibliographystyle{style_name}``
		
		Also returns a list, so what to do with multiple styles is not decided here."""
		
		ls = self.textProcessor.findRegexp(self.bibliographystyle)
		styledefs = list()
		
		for c in ls:
			txt, span, grps = c
			
			style_name, = grps
			
			styledefs.append((style_name, span))
		
		return styledefs
	
	def revertCitations(self, citation):
		raise NotImplementedError()
	
	def revertReflist(self, reflist_options):
		raise NotImplementedError()
	
	def revertStyleDefinition(self, style):
		raise NotImplementedError()
	

#========================================================================

def test_find_citations():
	txt = r"""
	\citet{jon90}       -->    Jones et al. (1990)
	\Citet{jon90}       -->    Jones et al. (1990)
	\citep{jon90}       -->    (Jones et al., 1990)
	\Citep{jon90}       -->    (Jones et al., 1990)
	\citet*{jon90}      -->    Jones, Baker, and Williams (1990)
	\Citet*{jon90}      -->    Jones, Baker, and Williams (1990)
	\citep*{jon90}      -->    (Jones, Baker, and Williams, 1990)
	\citealt{jon90}     -->    Jones et al. 1990
	\Citealt{jon90}     -->    Jones et al. 1990
	\citealt*{jon90}    -->    Jones, Baker, and Williams 1990
	\citealp{jon90}     -->    Jones et al., 1990
	\citealp*{jon90}    -->    Jones, Baker, and Williams, 1990
	\citeauthor{jon90}  -->    Jones et al.
	\Citeauthor{jon90}  -->    Jones et al.
	\citeauthor*{jon90} -->    Jones, Baker, and Williams
	\citeyear{jon90}    -->    1990
	\Citeyear{jon90}    -->    1990
	
	\bibliography
	
	\bibliography{toto}
	"""
	
	f = finder(None)
	for x in f.referencelist.finditer(txt):
		print x.group(0)
		print x.groups()
		print "-"*50

