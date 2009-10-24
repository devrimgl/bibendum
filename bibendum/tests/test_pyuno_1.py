
import uno

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
	
	model.Text.setString('')
	print dir(model.Text.getEnd())
	t = [("Here is a test for formatting capabilities. Let's make that ", {}),
	     ("bold", {'CharWeight': 150.}),
	     (" and this ", {}),
	     ("italics", {'CharPosture': 2}),
	     (", and this ", {}),
	     ("both", {'CharPosture': 2, 'CharWeight': 150.}),
	     (", ", {}),
	     ("underlined", {"CharUnderline": 1}),
	     (", ", {}),
	     ("and various types of CaseMaps", {"CharCaseMap": 4}),
	     (".", {})]
	for ti in t:
		c, s = ti
		cur = model.Text.createTextCursor()
		cur.gotoEnd(False)
		cur.setAllPropertiesToDefault()
		cur.setString(c)
		for k in s.keys():
			cur.setPropertyValue(k, s[k])
		