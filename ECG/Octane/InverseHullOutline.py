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
        
        #layout
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.ui)
        mainLayout.setContentsMargins(0,0,0,0)
        mainLayout.setSpacing(0)
        self.setLayout(mainLayout)
        
        self.button_setup.clicked.connect(self.create_octane_material)
        
    
    
    

    def create_octane_material(self,press):
      OutlineShader = hou.node('/mat').createNode("octane_vopnet", 'outline_shader')
      standard = OutlineShader.glob('Standard_Surface')
      print(standard[0].name())
      standard[0].destroy()
      #print(standard)
      #defaultNode = OutlineShader.nodeType('octane::NT_MAT_STANDARD_SURFACE').instances()
      #print(defaultNode) 
      #defaultNode.destroy()

       
           


def show():
    dialog = InverseHull()
    hou.session.mainWindow = hou.qt.mainWindow()
    dialog.setParent(hou.session.mainWindow, QtCore.Qt.Window)
    dialog.show()
    

