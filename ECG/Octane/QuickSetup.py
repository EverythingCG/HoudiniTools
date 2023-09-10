from hutil.Qt import QtCore, QtWidgets, QtUiTools
 
import os
import hou
scriptpath = os.path.dirname(__file__)

def minimizeNodes(nodeList):
    for node in nodeList:
        node.setDetailLowFlag(True)

class OctaneQuickSetup(QtWidgets.QWidget):
    button_load_textures = None

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.textureList = []
        self.textureDir = ''
        #load UI file
        ui_path = scriptpath + '/OctaneQuickSetup.ui'
        
        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(ui_path)
        
        #get UI widgets
        self.button_setup = self.ui.findChild(QtWidgets.QPushButton, 'setup') 
        self.lineEdit = self.ui.findChild(QtWidgets.QLineEdit, 'suffix')
        self.comboBox_kernel = self.ui.findChild(QtWidgets.QComboBox,'kernel')
        self.comboBox_camera = self.ui.findChild(QtWidgets.QComboBox, 'camera')
        #layout
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.ui)
        mainLayout.setContentsMargins(0,0,0,0)
        mainLayout.setSpacing(0)
        self.setLayout(mainLayout)

        self.button_setup.clicked.connect(self.quickSetup)
    


    def quickSetup(self):
        octane_ROP = hou.node('/out').createNode("Octane_ROP","Octane_ROP"+self.lineEdit.text())
        octane_render_target = hou.node('/mat').createNode("octane_mat_renderTarget", "RT_"+self.lineEdit.text())
        
        octane_render_target.parm('parmKernel').set(self.comboBox_kernel.currentIndex())
        octane_render_target.parm('parmCamera').set(self.comboBox_camera.currentIndex())
        
        #camera handling
        OctaneCam = None
        cameras = hou.objNodeTypeCategory().nodeType('cam').instances() 
        if len(cameras) == 0:
            OctaneCam = hou.node('/obj').createNode("cam", 'cam'+self.lineEdit.text())
        else:
            OctaneCam = cameras[0]
        
        #set OCTANE ROP params
        octane_ROP.parm('HO_renderTarget').set(octane_render_target.path())
        octane_ROP.parm('HO_renderCamera').set(OctaneCam.path())
        octane_ROP.parm('HO_iprCamera').set(OctaneCam.path())

        

           


def show():
    dialog = OctaneQuickSetup()
    hou.session.mainWindow = hou.qt.mainWindow()
    dialog.setParent(hou.session.mainWindow, QtCore.Qt.Window)
    dialog.show()
    
    

