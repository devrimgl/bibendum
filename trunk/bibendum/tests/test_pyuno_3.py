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
	
	print citation
	
	sd = model.createSearchDescriptor()
	sd.setSearchString(citation)
	sd.SearchRegularExpression = True
	
	f = model.findAll(sd)
	print f.Count
	for i in range(f.Count):
		print f.getByIndex(i).String