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
    
    def onParmChangeEvent(self, kwargs):
        print(kwargs)

    def createMenuParm(self, name, label, parent, items, labels, default):
        kernel_menu_parm = hou.MenuParmTemplate(name, label, items, labels, default_value = default)
        g = parent.parmTemplateGroup()
        g.append(kernel_menu_parm)
        parent.setParmTemplateGroup(g)

    def quickSetup(self):
        OctaneROP_node = hou.node('/out').createNode("Octane_ROP","Octane_ROP"+self.lineEdit.text())
        OctaneVOPNET = hou.node('/mat').createNode("octane_vopnet", 'renderTarget'+self.lineEdit.text())
        
        
        
        group = OctaneVOPNET.parmTemplateGroup()
        l = group.entries()
        for i in l:
            print(i)
        
        
        group.hideFolder('OpenGL',True)
        OctaneVOPNET.setParmTemplateGroup(group)
        
        vopnet_children = OctaneVOPNET.children()
        for child in vopnet_children:
            child.destroy()
        
        
        #setup custom kernel menu param
        menuName = "kernel"
        menu_labels = ['DirectLighting','PathTracing','PMC','PhotonTracing']
        menu_items = ("dl","pt","pmc","pht")
        kernelMenuSelection = self.comboBox_kernel.currentIndex()
        self.createMenuParm(menuName, "Kernel", OctaneVOPNET, menu_items, menu_labels, kernelMenuSelection)

        cam_menu_name = "camera"
        menu_labels = ['ThinLens','Universal','Panoramic','Baking']
        menu_items = ("thl","uni","pan","bak")
        cam_menu_selection = self.comboBox_camera.currentIndex()
        self.createMenuParm(cam_menu_name, "Camera", OctaneVOPNET, menu_items, menu_labels, cam_menu_selection)

        #menu driven kernel selector
        kernelSelector = OctaneVOPNET.createNode("octane::NodeSelector")
        kernelSelector.parm('nodeSelected').setExpression('ch("../'+menuName+'")', language=hou.exprLanguage.Hscript)
        
        #menu driven camera selector
        camSelector = OctaneVOPNET.createNode("octane::NodeSelector")
        camSelector.parm('nodeSelected').setExpression('ch("../'+cam_menu_name+'")', language=hou.exprLanguage.Hscript)
        
        #create render target input nodes
        cameraTL = OctaneVOPNET.createNode("octane::NT_CAM_THINLENS")
        cameraUNI = OctaneVOPNET.createNode("octane::NT_CAM_UNIVERSAL")
        cameraPAN = OctaneVOPNET.createNode("octane::NT_CAM_PANORAMIC")
        cameraBAK = OctaneVOPNET.createNode("octane::NT_CAM_BAKING")
        environment = OctaneVOPNET.createNode("octane::NT_ENV_TEXTURE")
        imager = OctaneVOPNET.createNode("octane::NT_IMAGER_CAMERA")
        kernelDL = OctaneVOPNET.createNode("octane::NT_KERN_DIRECTLIGHTING")
        kernelPMC = OctaneVOPNET.createNode("octane::NT_KERN_PMC")
        kernelPT = OctaneVOPNET.createNode("octane::NT_KERN_PATHTRACING")
        kernelPHT = OctaneVOPNET.createNode("octane::NT_KERN_PHOTONTRACING")
        postprocess = OctaneVOPNET.createNode("octane::NT_POSTPROCESSING")
        cameraEnvironment = OctaneVOPNET.createNode("octane::NT_ENV_TEXTURE")
        
        #setup inputs
        OctaneRenderTarget = OctaneVOPNET.createNode("octane_render_target")
        OctaneRenderTarget.setInput(0,camSelector)
        OctaneRenderTarget.setInput(1,environment)
        OctaneRenderTarget.setInput(2,imager)
        OctaneRenderTarget.setInput(3,kernelSelector)
        OctaneRenderTarget.setInput(4,postprocess)
        OctaneRenderTarget.setInput(6,cameraEnvironment)
        
        camSelector.setInput(0, cameraTL)
        camSelector.setInput(1, cameraUNI)
        camSelector.setInput(2, cameraPAN)
        camSelector.setInput(3, cameraBAK)

        kernelSelector.setInput(0, kernelDL)
        kernelSelector.setInput(1, kernelPT)
        kernelSelector.setInput(2, kernelPMC)
        kernelSelector.setInput(3, kernelPHT)

        #set OCTANE ROP params
        OctaneROP_node.parm('HO_renderTarget').set(OctaneVOPNET.path())
        
        minimizeNodes(OctaneVOPNET.children())
        OctaneVOPNET.layoutChildren() 

           


def show():
    dialog = OctaneQuickSetup()
    hou.session.mainWindow = hou.qt.mainWindow()
    dialog.setParent(hou.session.mainWindow, QtCore.Qt.Window)
    dialog.show()
    
    

