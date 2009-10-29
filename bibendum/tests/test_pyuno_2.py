import uno
import time

localContext = uno.getComponentContext()
resolver = localContext.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", localContext )
ctx = resolver.resolve( "uno:pipe,name=OOo_pipe;urp;StarOffice.ComponentContext" )
smgr = ctx.ServiceManager

desktop = smgr.createInstanceWithContext( "com.sun.star.frame.Desktop",ctx)
model   = desktop.getCurrentComponent()

def createCustomField(name, content):
	
	masterNames = model.TextFieldMasters.ElementNames
	masterUserNames = list()
	for m in masterNames:
		if m[0:35] == 'com.sun.star.text.fieldmaster.User.':
			masterUserNames.append(m)
			print m
			print model.TextFieldMasters.getByName(m).DependentTextFields
	
	tfmsU = [model.TextFieldMasters.getByName(x) for x in masterUserNames]
	masterUserNames = [x[35:] for x in masterUserNames]
	
	print masterUserNames
	
	if name in masterUserNames:
		print '%s already exists...' % name
		return None
	
	xMaster = model.createInstance("com.sun.star.text.fieldmaster.User")
	xMaster.Name = name
	xMaster.Content = content
	
	xUserField = model.createInstance("com.sun.star.text.textfield.User")
	xUserField.attachTextFieldMaster(xMaster)
	
	return xUserField

def updateField(name, content):
	tfm = model.TextFieldMasters.getByName('com.sun.star.text.fieldmaster.User.%s' % name)
	tfm.setPropertyValue("Content", content)
	for f in tfm.DependentTextFields:
		f.update()

def getFieldContent(name):
	tfm = model.TextFieldMasters.getByName('com.sun.star.text.fieldmaster.User.%s' % name)
	return tfm.Content

if model.getImplementationName()=='SwXTextDocument':
	
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
	
	n = int( time.clock()*1000)
	
	f = createCustomField("MyField %d" % n, "".join([x[0] for x in t]))
	
	if f is not None:
		
		model.Text.insertTextContent(model.Text.getEnd(), f, False)
		
		cur = model.Text.getEnd()
		cur.setAllPropertiesToDefault()
		cur.goLeft(4, False)
		
		cur.setPropertyValue('CharWeight', 150.)
		
		print dir(cur)
		
	#~ updateField("MyField1", "Modified")
	#~ print getFieldContent("MyField2")



ctx.ServiceManager
