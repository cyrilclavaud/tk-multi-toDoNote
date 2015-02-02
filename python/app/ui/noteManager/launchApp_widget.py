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

import os

class launchBtn(QtGui.QPushButton) :
    
    @decorateur_try_except
    def __init__(self, launchApp, values , parent = None):
        QtGui.QPushButton.__init__(self,  parent)
        
        self.launchApp = launchApp
        self.values = values
        

        self.setIcon(QtGui.QIcon(getRessources(values["icon"]) ))
        self.setFlat(True);
        self.setIconSize(QtCore.QSize(32,32));
        self.setStyleSheet("QPushButton{outline: none;}");

        self.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.fileMenu = self.createMenu()
        self.setClickAction(None)
        self.setMaximumWidth(32)
        self.setMaximumHeight(32)

    @decorateur_try_except
    def contextMenuEvent(self, e ) :
        self.fileMenu.exec_( e.globalPos() )


    @decorateur_try_except
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

    @decorateur_try_except
    def createMenu(self ):

        fileMenu =  QtGui.QMenu()
        for a in self.values["files"][0]:
            fct = lambda: self.launchFromPath( a )
            fileMenu.addAction(os.path.basename(a), fct )
        
        for m, files in self.values["files"][1].iteritems() :
            fileNameMenu =  fileMenu.addMenu( m )
            for path in files :
                fct = lambda: self.launchFromPath( path )
                fileNameMenu.addAction(os.path.basename(path), fct )
        

        fct = lambda: self.launchFromContext( self.values["files"][2] )
        fileMenu.addAction("Empty Scene",fct )
        return fileMenu

    @decorateur_try_except
    def launchFromContext(self,  entityId):
        eng = sgtk.platform.current_engine()
        appLauncher = eng.apps.get(self.launchApp)

        tk_i = sgtk.tank_from_entity( "Task" , entityId)
        context = tk_i.context_from_entity("Task" ,entityId )
        appLauncher._launch_app(context, version=None)

    def launchFromPath(self,  path):
        eng = sgtk.platform.current_engine()
        appLauncher = eng.apps.get(self.launchApp)

        tk_i = sgtk.tank_from_path( path)
            
        context = tk_i.context_from_path(path)
        appLauncher._launch_app( context, path )





class LaunchApp_widget( QtGui.QWidget ):
    @decorateur_try_except
    def __init__(self, new_appLauncherDict, shotId, taskName, empty = False  ) :

        QtGui.QWidget.__init__(self)
        self.eng = None
        self.shotId = shotId
        self.taskName = taskName
        self.empty = empty

        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(2)
        self.setLayout(layout)

        if empty :
            lab = QtGui.QLabel()
            lab.setMaximumWidth(32)
            lab.setMaximumHeight(32)
            layout.addWidget(lab)
            return

        try :
            self.eng = sgtk.platform.current_engine()
        except :
            self.eng = None 
            return

        self.launchLayout = QtGui.QVBoxLayout()
        self.launchLayout.setContentsMargins(0,0,0,0)
        self.launchLayout.setSpacing(2)
        layout.addStretch()
        layout.addLayout(self.launchLayout)
        for task in new_appLauncherDict.keys():
            for appLauncher in new_appLauncherDict[task].keys():
                if new_appLauncherDict[task][appLauncher].has_key("files") :
                    self.launchLayout.addWidget( launchBtn( appLauncher, new_appLauncherDict[task][appLauncher], parent = self ) )




    @decorateur_try_except
    def updateLauncherList(self, new_appLauncherDict):

        if not self.eng :
            return

        for i in reversed(range(self.launchLayout.count())):   
            wid =  self.launchLayout.itemAt(i).widget()
            wid.setParent(None)
            try :
                del wid
            except :
                pass


        for task in new_appLauncherDict.keys():
            for appLauncher in new_appLauncherDict[task].keys():
                if new_appLauncherDict[task][appLauncher].has_key("files") :
                    self.launchLayout.addWidget( launchBtn( appLauncher, new_appLauncherDict[task][appLauncher], parent = self ) )









