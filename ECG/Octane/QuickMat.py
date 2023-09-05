from hutil.Qt import QtCore, QtWidgets, QtUiTools
 
import os
import hou
scriptpath = os.path.dirname(__file__)

class TextureLoader(QtWidgets.QWidget):
    button_load_textures = None

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.textureList = []
        self.textureDir = ''
        #load UI file
        ui_path = scriptpath + '/QuickMat.ui'
        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(ui_path)
        
        #get UI widgets
        self.button_create_mat = self.ui.findChild(QtWidgets.QPushButton, 'createm') 
        self.button_load_textures = self.ui.findChild(QtWidgets.QPushButton, 'loadtextures') 
        self.check_box = self.ui.findChild(QtWidgets.QCheckBox, 'checkBox') 
        self.button_load_textures.setEnabled(False)
        self.temp = 5
        
        #layout
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.ui)
        mainLayout.setContentsMargins(0,0,0,0)
        mainLayout.setSpacing(0)
        self.setLayout(mainLayout)
        
    
        self.button_create_mat.clicked.connect(self.create_octane_material)
        self.button_load_textures.clicked.connect(self.select_texture_directory)
        self.check_box.stateChanged.connect(lambda b: self.state_changed(self.check_box))
    def state_changed(self,a):
      if a.isChecked():
         self.button_load_textures.setEnabled(True)
      else:
         self.button_load_textures.setEnabled(False)
    
             #callbacks
    
    def select_texture_directory(self):
      dir = hou.ui.selectFile(title="Select Directory",file_type=hou.fileType.Directory)
      self.textureDir = hou.text.expandString(dir)
      self.textureList = os.listdir(self.textureDir)
      self.check_box_state = False

    def create_octane_material(self,press):
      
      mat = hou.node('/mat')
      octane_vopnet = mat.createNode('octane_vopnet')

      #no path selected
      if self.textureDir == '':
         return

      projectionNode = octane_vopnet.createNode('octane::NT_PROJ_BOX')
      transformNode = octane_vopnet.createNode('octane::NT_TRANSFORM_2D')

      childrenList = octane_vopnet.children()
      standardSurface = childrenList[1]

      thisdict = {'albedo': 1, 'roughness':6, 'bump': 43, 'normal':44 }
      textureInput = -1

      bMatch = False
      for f in self.textureList:
        for key in thisdict:
          if f.find(key) > -1:
            textureInput = thisdict[key]
            RGBTexture = octane_vopnet.createNode('octane::NT_TEX_IMAGE')
            standardSurface.setInput(textureInput,RGBTexture)
            RGBTexture.parm('A_FILENAME').set(self.textureDir+"/"+f)
            RGBTexture.setInput(6,projectionNode)
            RGBTexture.setInput(5,transformNode)
            bMatch = True
            break
      
      if not bMatch:
         projectionNode.destroy()
         transformNode.destroy()

      octane_vopnet.layoutChildren() 
           


def show():
    dialog = TextureLoader()
    hou.session.mainWindow = hou.qt.mainWindow()
    dialog.setParent(hou.session.mainWindow, QtCore.Qt.Window)
    dialog.show()
    

