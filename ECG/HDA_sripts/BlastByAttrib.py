def createNodes():
    node = hou.pwd()
    geo = node.geometry()
    attribType = node.parm('attribute_type').eval()
    variableType = node.parm('variable_type').eval()
    attribName = node.parm('attrib_name').eval()
    groupTypeMap = {0: 3,1: 4}
    groupNameMap = {0: "Point",1: "Primitive"}
    
    #check existance
    if not checkAttribExistance(attribType, attribName,variableType,groupNameMap):
        return
    
    
    uniqueAttributes = []
    try:
        uniqueAttributes = getUniqueAttributes(attribType, attribName, variableType)
    except hou.OperationFailed:
        print('Primitive Type or Variable Type missmatch, check input parameters and try again')
        
    #separate geo
    for attrib in uniqueAttributes:
        blast_node = node.parent().createNode('blast', 'blast_'+str(attrib))
        blast_node.setInput(0,node)
        blast_node.parm('group').set('@'+attribName+'='+str(attrib))
        blast_node.parm('grouptype').set(groupTypeMap[attribType])

        
def getUniqueAttributes(attribType, attribName, variableType):
    
    node = hou.pwd()
    geo = node.geometry()
    #float/int
    if variableType == 0:
        #point
        if attribType == 0:
            uniqueAttributes = set(geo.pointFloatAttribValues(attribName))
        #prim
        if attribType == 1:
            uniqueAttributes = set(geo.primFloatAttribValues(attribName))
    
    #string
    if variableType == 1:
        #point
        if attribType == 0:
            uniqueAttributes = set(geo.pointStringAttribValues(attribName))
        #prim
        if attribType == 1:
            uniqueAttributes = set(geo.primStringAttribValues(attribName))

    print(uniqueAttributes)
    return uniqueAttributes
    
def checkAttribExistance(attribType, attribName,variableType,groupNameMap):
    node = hou.pwd()
    geo = node.geometry()
    #point
    if attribType == 0:
        temp = geo.findPointAttrib(attribName)
    #prim
    if attribType == 1:
        temp = geo.findPrimAttrib(attribName)
    
    if temp == None:
        message = "Couldn't find "+groupNameMap[attribType]+ " attribute named:   "+ attribName 
        hou.ui.displayMessage(message,title='OH NO :(((')
        return 0
   
    return 1 