#!/usr/bin/python
# -*- coding: utf-8 -*-

try :
    import sgtk
    from sgtk.platform.qt import QtCore, QtGui
    _signal = QtCore.Signal 
    outFileName = "side"

    

except :
    from PyQt4 import QtGui, QtCore
    _signal = QtCore.pyqtSignal
    outFileName = "cute"


import utils
from utils import *

import ui_widget
from ui_widget import *

import os

class launchBtn(QtGui.QPushButton) :
    
    ## @decorateur_try_except
    def __init__(self, launchApp, values , SGTK_ENGINE, parent = None, version = None):
        QtGui.QPushButton.__init__(self,  parent)
        
        #launchApp = "tk-multi-launchnukeX"

        self.SGTK_ENGINE = SGTK_ENGINE
        self.launchApp = launchApp
        self.version = version
        self.sgTaskDict = parent.sgTaskDict

        
        if not SGTK_ENGINE.apps.has_key( launchApp ) :
            self.setEnabled(False)
            self.setToolTip( launchApp + " hasn't been (properly) declared\nSee configuration files.")
        else :
            self.setToolTip(launchApp + "\nRight click to specifically open a file." )

        self.values = values
        
        self.setIcon(QtGui.QIcon(getRessources(values["icon"]) ))

        self.setFlat(True);
        self.setIconSize(QtCore.QSize(30,30));
        style = 'QPushButton:hover{border: 1px solid rgb(48,226,227)}'
        self.setStyleSheet("QPushButton{outline: none;}"+style);


        self.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.fileMenu = self.createMenu()
        self.setClickAction(None)
        self.setMaximumWidth(32)
        self.setMaximumHeight(32)


    def paintEvent (self, event):  
        QtGui.QPushButton.paintEvent(self, event)  

        if self.version :
            painter = QtGui.QPainter(self) 
            painter.setPen( QtGui.QPen(QtGui.QColor(255,255,255,255))) 
            painter.drawText( self.rect().adjusted(3, 0, 0 , 0), QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter, str(self.version) )




    ## @decorateur_try_except
    def contextMenuEvent(self, e ) :
        self.fileMenu.exec_( e.globalPos() )


    ## @decorateur_try_except
    def setClickAction(self, p = None ):
        if self.values["files"][0]  :
            path = self.values["files"][0][0]
            fct = lambda: self.launchFromPath( path )
        elif self.values["files"][1].keys() :
            keyName = self.values["files"][1].keys()[0]
            path = self.values["files"][1][keyName][0]
            fct = lambda: self.launchFromPath( path )
        else :
            ctx = self.values["files"][2]
            fct = lambda: self.launchFromContext( ctx )

        self.clicked.connect( fct )

    ## @decorateur_try_except
    def createMenu(self ):

        fileMenu =  QtGui.QMenu()
        for a in self.values["files"][0]:
            fct = lambda a = a : self.launchFromPath( a )
            fileMenu.addAction(os.path.basename(a), fct )
        
        for m, files in self.values["files"][1].iteritems() :
            fileNameMenu =  fileMenu.addMenu( m )
            for path in files :
                fct = lambda path = path : self.launchFromPath( path )
                fileNameMenu.addAction(os.path.basename(path), fct )
        
        path = self.values["files"][2]
        fct = lambda path = path  : self.launchFromContext( path )
        fileMenu.addAction("Empty Scene",fct )
        return fileMenu

    ## @decorateur_try_except
    def launchFromContext(self,  entityId):

        appLauncher = self.SGTK_ENGINE.apps[self.launchApp]
        

        tk_i = sgtk.tank_from_entity( "Task" , entityId)
        context = tk_i.context_from_entity("Task" , self.sgTaskDict['id'] )
        print self.launchApp , "launch -> empty ", context
        appLauncher._launch_app(context, version= self.version )
    
    ## @decorateur_try_except
    def launchFromPath(self,  path):
        #path = "//sledge/vol1/Projects/EventTrackingProject/Compositing/Setups/Nuke/EV001/Comp/work/EV001_comp_v004.nk"


        app =self.SGTK_ENGINE.apps[self.launchApp]
 
        
        tk_i = sgtk.tank_from_path( path)
        context = tk_i.context_from_entity("Task" , self.sgTaskDict['id'] )

        print self.launchApp, "launch ->", context , path 

        #app._launch_app(context, version= self.version )
        app._launch_app(   context, file_to_open= path, version=self.version) 






class LaunchApp_widget( QtGui.QWidget ):
 
    ## @decorateur_try_except       
    def paintEvent(self, pe):


        opt = QtGui.QStyleOption()
        opt.initFrom(self)
        p = QtGui.QPainter(self)
        s = self.style()

        s.drawPrimitive(QtGui.QStyle.PE_Widget, opt, p, self)


    ## @decorateur_try_except
    def __init__(self, new_appLauncherDict, shotId, taskName, entityCode, sgTaskDict,  empty = False, SGTK_ENGINE = None, parent = None  ) :



        QtGui.QWidget.__init__(self, parent)
        self.setAutoFillBackground(True)
        self.setStyleSheet("LaunchApp_widget{background-color: qlineargradient( x1: 0.7, y1: 0, x2: 1, y2: 0, stop: 0 #2A2A2A, stop: 1 #425C73 )}")
        
        
        #"background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #9dd53a, stop: .5 #a1d54f, stop: .51 #80c217, stop: 1 #7cbc0a);"

        self.eng = None
        self.shotId = shotId
        self.taskName = taskName
        self.sgTaskDict = sgTaskDict
        self.empty = empty

        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(2)
        self.setLayout(layout)

        
        lab = QtGui.QLabel("<b><font color='#30A6E3'>" + str(taskName) + " "+ str(entityCode)+ "</font></b>")
        lab.setMinimumHeight(32)

        layout.addSpacing(9)
        layout.addWidget(QtGui.QLabel("<b><font color='#425C73'> Launch Bar </font></b>"))
        layout.addStretch()
        layout.addWidget(lab)
        layout.addSpacing(9)

        if empty :
            if shotId != 0 :
                layout.addWidget(loadingWidget(intSize = 32 ))
            return

        if not SGTK_ENGINE :
            print "fail"
            return


        self.launchLayout = QtGui.QHBoxLayout()
        self.launchLayout.setContentsMargins(0,0,0,0)
        self.launchLayout.setSpacing(2)
        
        layout.addLayout(self.launchLayout)

        for task in new_appLauncherDict.keys():

            for appLauncher in new_appLauncherDict[task].keys():
                if new_appLauncherDict[task][appLauncher].has_key("files") :
                    
                    versionList = []
                    if SGTK_ENGINE.apps.has_key( appLauncher ) :
                        versionList = SGTK_ENGINE.apps[appLauncher].get_setting("versions") 

                    if versionList :
                        for  version in versionList :
                            self.launchLayout.addWidget( launchBtn( appLauncher, new_appLauncherDict[task][appLauncher], SGTK_ENGINE ,parent = self, version = version ) )                            
    
                    else :
                        self.launchLayout.addWidget( launchBtn( appLauncher, new_appLauncherDict[task][appLauncher], SGTK_ENGINE ,parent = self , version = None) )
                    





