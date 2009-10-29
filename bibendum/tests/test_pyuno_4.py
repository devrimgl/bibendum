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
		
	
	exit()
	
	print "="*50
	
	i0 = 0
	
	c = Txt.createTextCursor()
	c.gotoStart(False)
	
	
	for f in reCite.finditer(Txt.String):
		
		i1, i2 = f.span()
		
		c.collapseToEnd()
		c.setAllPropertiesToDefault()
		
		c.goRight(i1-i0, True)
		
		print i0, i1, i2
		
		d = 0
		for f in fields:
			print "  ", f.String
			print "  ", f.Text.compareRegionStarts(c, f), f.Text.compareRegionEnds(c, f)
			if f.Text.compareRegionStarts(c, f)>-1 and f.Text.compareRegionEnds(c, f)<1:
				d += len(f.String)
		print "-------", d
		
		c.goLeft(d, True)
		print c.String
		
		#~ print dir(c.Text)
		
		c.collapseToEnd()
		c.goRight(i2-i1, True)
		c.setPropertyValue('CharColor', 0x00FF0000)
		
		i0 = i2+1
	
	
	#~ for tf in fields:
		#~ tf.IsFieldDisplayed = True
	