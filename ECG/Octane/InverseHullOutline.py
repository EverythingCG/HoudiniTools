#from xml.dom import ValidationErr
from hutil.Qt import QtCore, QtWidgets, QtUiTools
 
import os
import hou


scriptpath = os.path.dirname(__file__)

class InverseHull(QtWidgets.QWidget):

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.textureList = []
        self.textureDir = ''
        #load UI file
        ui_path = scriptpath + '/InverseHullOutline.ui'
        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(ui_path)
        
        #get UI widgets
        self.button_setup = self.ui.findChild(QtWidgets.QPushButton, 'setup') 
        self.button_select = self.ui.findChild(QtWidgets.QPushButton, 'selectgeo') 
        self.geo_label = self.ui.findChild(QtWidgets.QLabel, 'geolabel') 

        #layout
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.ui)
        mainLayout.setContentsMargins(0,0,0,0)
        mainLayout.setSpacing(0)
        self.setLayout(mainLayout)
        
        self.button_setup.clicked.connect(self.create_octane_material)
        self.button_select.clicked.connect(self.select_outline_geo)
        self.button_setup.clicked.connect(self.close)

        self.button_setup.setEnabled(False)
        self.operatorPath = None
        self.selectionName = ''
        self.validSelection = False
        self.OutlineShader = None
        
    
    def select_outline_geo(self):
        self.operatorPath = hou.ui.selectNode()
        selectedNode = hou.node(self.operatorPath)
        if selectedNode.parent().type().name() == 'geo':
            self.selectionName = selectedNode.parent().name()
            self.validSelection = True
            self.button_setup.setEnabled(True)
            self.geo_label.setText("Selected Geo: "+self.operatorPath)
        else:
            print("invalid selection: select a node in geo context")
        

    def create_outline_geo(self):
        OutlineGeo = hou.node('/obj').createNode('geo', self.selectionName+'_OUTLINE')
        OutlineGeo.parm('octane_objprop_shadowVis').set(False)
        ObjectMerge = OutlineGeo.createNode('object_merge')
        ObjectMerge.parm('objpath1').set(self.operatorPath)

        #temporary outline geo setup, to be replaced with an outline HDA
        poly_extrude = OutlineGeo.createNode('polyextrude::2.0')
        outline_mat = OutlineGeo.createNode('material')

        poly_extrude.setInput(0, ObjectMerge)
        outline_mat.setInput(0,poly_extrude)

        poly_extrude.parm('dist').set(0.04)
        outline_mat.parm('shop_materialpath1').set(self.OutlineShader.path())

        outline_mat.setGenericFlag(hou.nodeFlag.Display,True)
        outline_mat.setGenericFlag(hou.nodeFlag.Render,True)
        OutlineGeo.layoutChildren()
        


    def create_octane_material(self,press):
        self.OutlineShader = hou.node('/mat').createNode("octane_vopnet", self.selectionName+'outline_shader')
        standard = self.OutlineShader.glob('Standard_Surface')
        standard[0].destroy()
    
        #node ref
        material_output_node = self.OutlineShader.children()[0]
        ToonMat = self.OutlineShader.createNode("octane::NT_MAT_TOON")
        Tool_PolySide = self.OutlineShader.createNode("octane::NT_TEX_SIDE")
        Tool_MultiplyTexture = self.OutlineShader.createNode("octane::NT_TEX_MULTIPLY")
        ColorRGB_n = self.OutlineShader.createNode("octane::NT_TEX_RGB")
        Tool_Ray_Switch = self.OutlineShader.createNode("octane::NT_TEX_RAY_SWITCH")
        
        #setup inputs
        material_output_node.setInput(0, ToonMat)
        ToonMat.setInput(0, Tool_MultiplyTexture)
        ToonMat.setInput(9, Tool_MultiplyTexture)
        ToonMat.setInput(11, Tool_PolySide)
        Tool_MultiplyTexture.setInput(0, ColorRGB_n)
        Tool_MultiplyTexture.setInput(1, Tool_Ray_Switch)

        #set params
        Tool_PolySide.parm('invert').set(True)
        Tool_Ray_Switch.parm('texture1').set(0)
        Tool_Ray_Switch.parm('texture2').set(0)
        Tool_Ray_Switch.parm('texture3').set(0)
        Tool_Ray_Switch.parm('texture4').set(0)
        Tool_Ray_Switch.parm('texture5').set(0)
        Tool_Ray_Switch.parm('texture6').set(0)

        self.OutlineShader.layoutChildren()
        self.create_outline_geo()
            
       
def show():
    dialog = InverseHull()
    hou.session.mainWindow = hou.qt.mainWindow()
    dialog.setParent(hou.session.mainWindow, QtCore.Qt.Window)
    dialog.show()

def closeWindow():
    print('closeWindow') 

    

