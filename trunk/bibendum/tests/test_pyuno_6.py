#-*- coding: utf-8 -*-

import uno
import re

# To create a pipe on Ubuntu, edit: /usr/bin/ooffice
# #!/bin/sh
# /usr/lib/openoffice/program/soffice -accept="pipe,name=OOo_pipe;urp;" "$@"

localContext = uno.getComponentContext()
resolver = localContext.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", localContext )
ctx = resolver.resolve( "uno:pipe,name=OOo_pipe;urp;StarOffice.ComponentContext" )
#~ ctx = resolver.resolve( "uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext" )
smgr = ctx.ServiceManager

desktop = smgr.createInstanceWithContext( "com.sun.star.frame.Desktop",ctx)
model   = desktop.getCurrentComponent()


def getRealText(obj):
	
	real_txt = ''
	
	attr = dir(obj)
	
	#~ print "===>", obj.ImplementationName
	
	if obj.ImplementationName in ['SwXTextPortion']:
	#~ if 'TextPortionType' in attr:
		#~ print 'TextPortionType'
		if obj.TextPortionType=='Text':
			s = obj.String
		elif obj.TextPortionType=='TextField':
			s = ' '
		else:
			s = ''
		real_txt += s
		#~ print repr(s)
	elif obj.ImplementationName in ['SwXCell', 'SwXParagraph', 'SwXBodyText']:
	#~ elif 'createEnumeration' in attr:
		#~ print 'createEnumeration'
		e = obj.createEnumeration()
		while e.hasMoreElements():
			real_txt += getRealText(e.nextElement())
		if obj.ImplementationName == 'SwXParagraph':
			real_txt += '\n'
			#~ print "-", obj.ImplementationName
		
	elif obj.ImplementationName in ['SwXTextTable']:
	#~ elif 'getCellByPosition' in attr:
		for i in range(obj.Rows.Count):
			for j in range(obj.Columns.Count):
				real_txt += getRealText(obj.getCellByPosition(i,j))
		#~ real_txt += '\n'
	
	
	return real_txt

if model.getImplementationName()=='SwXTextDocument':
	
	#~ lowercase = 'éèçàôêîù';
	#~ uppercase = 'ÉÈÇÀÔÊÎÙ';
	lowercase = '';
	uppercase = '';
	
	author  = '((?:[vV]an |[vV]on |[dD]e |[dD]e la |[dD]el )?(?:Mc)?[A-Z%s][a-z%s-]+)' % (uppercase, lowercase)
	authorI = '((?:[vV]an |[vV]on |[dD]e |[dD]e la |[dD]el )?)((?:Mc)?[A-Z%s][a-z%s-]+)' % (uppercase, lowercase)
	date    = '([1-2][0-9]{3}[a-z]?)'
	
	authorBlock = '%s(?:,? (et al\\.)?|(?:, %s)*,? (?:&|and) %s)?' % (author,author,author)
	dateBlock   = '%s(?:, %s)*' % (date, date)
	dateBlock   = '(?:(?:%s)|(?:\\(%s\\)))' % (dateBlock, dateBlock)
	
	citation = '('+authorBlock+',? '+dateBlock+')'
	
	reCite = re.compile(citation, re.UNICODE)
	reAuthors = re.compile(authorBlock)
	reDate = re.compile(dateBlock)
	reAuthor  = re.compile(authorI)
	
	Txt = model.Text
	
	c = Txt.createTextCursor()
	c.gotoStart(False)
	c.gotoEnd(True)
	c.setPropertyValue('CharColor', 0x00000000)
	
	#~ real_txt = ''
	#~ pars = Txt.createEnumeration()
	#~ while pars.hasMoreElements():
		#~ p = pars.nextElement()
		#~ if p.ImplementationName!='SwXParagraph':
			#~ cnt = p.getRows()
			#~ print dir(p.getCellByPosition(0,0))
			#~ continue
		#~ else:
			#~ cnt = p.createEnumeration()
			#~ while cnt.hasMoreElements():
				#~ w = cnt.nextElement()
				#~ if w.TextPortionType=='Text':
					#~ real_txt += w.String
				#~ elif w.TextPortionType=='TextField':
					#~ real_txt += ' '
				#~ else:
					#~ print w.TextPortionType, repr(w.String)
		#~ real_txt += '\n'
	real_txt = getRealText(Txt)
	print real_txt
	
	for f in reCite.finditer(real_txt):
		
		i1, i2 = f.span()
		
		
		#~ c.goRight(i1-i0, True)
		
		#~ print i0, i1, i2
		
		#~ d = 0
		#~ for f in fields:
			#~ print "  ", f.String
			#~ print "  ", f.Text.compareRegionStarts(c, f), f.Text.compareRegionEnds(c, f)
			#~ if f.Text.compareRegionStarts(c, f)>-1 and f.Text.compareRegionEnds(c, f)<1:
				#~ d += len(f.String)
		#~ print "-------", d
		
		#~ c.goLeft(d, True)
		#~ print c.String
		
		#~ print dir(c.Text)
		
		#~ c.collapseToEnd()
		
		c = Txt.createTextCursor()
		c.setAllPropertiesToDefault()
		c.gotoStart(False)
		c.goRight(i1, False)
		c.goRight(i2-i1, True)
		c.setPropertyValue('CharColor', 0x00FF0000)
		#~ c.collapseToEnd()
		
		
		i0 = i2+1
	
	
	#~ for tf in fields:
		#~ tf.IsFieldDisplayed = True
	