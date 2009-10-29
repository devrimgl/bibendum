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
	
	fields = list()
	tfs = model.TextFields.createEnumeration()
	while tfs.hasMoreElements():
		tf = tfs.nextElement()
		fields.append(tf.Anchor)
		
	
	
	print "="*50
	
	i0 = 0
	
	real_txt = ''
	c = Txt.createTextCursor()
	c.gotoStart(False)
	while c.goRight(1, True):
		if len(c.String)!=1:
			real_txt += ' '
		else:
			real_txt += c.String
		c.collapseToEnd()
	print real_txt
	#~ exit()
	
	
	
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
		c.IsSkipProtectedText = True
		c.IsSkipHiddenText = False
		c.gotoStart(False)
		c.goRight(i1, False)
		c.goRight(i2-i1, True)
		c.setPropertyValue('CharColor', 0x00FF0000)
		#~ c.collapseToEnd()
		
		
		i0 = i2+1
	
	
	#~ for tf in fields:
		#~ tf.IsFieldDisplayed = True
	