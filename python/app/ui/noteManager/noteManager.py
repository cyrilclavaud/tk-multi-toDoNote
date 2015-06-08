#!/usr/bin/python
# -*- coding: utf-8 -*-

import _strptime

import random
import time
import os
import re
import sys
import Queue
import gc

from operator import itemgetter

import utils
from utils import *



try :
    import sgtk
    from sgtk.platform.qt import QtCore, QtGui
    _signal = QtCore.Signal 
    QtCore.QCoreApplication.addLibraryPath(  getPathToImagePlugins() )
    outFileName = "side"
except :
    from PyQt4 import QtGui, QtCore
    _signal = QtCore.pyqtSignal
    outFileName = "cute"



import imageDisplay
import imageScribble
import imagePicker

import utils
from utils import *

import shotgunThreading 
from shotgunThreading import *

import treeWidgetItem
from treeWidgetItem import *

import note_reply_widget
from note_reply_widget import *

import launchApp_widget
from launchApp_widget import *

class NoRectDelegate(QtGui.QItemDelegate): 
    def __init__(self , parent = None):
        super(NoRectDelegate, self).__init__( parent )
                      
    def drawFocus (self, painter,option,rect):
        option.state &= ~QtGui.QStyle.State_HasFocus
        QtGui.QItemDelegate.drawFocus (self, painter,option,rect)



class myQTree( QtGui.QTreeWidget ):
    pixmap = None

    SIGNAL_updateNoteContent = _signal(object)


    SIGNAL_selectShot = _signal(object)
    SIGNAL_setNoteStatus = _signal(object)
    SIGNAL_setNoteType = _signal(object)
    SIGNAL_deleteNotes = _signal(object)
    SIGNAL_setNoteTask = _signal(object)
    SIGNAL_setNoteLink = _signal(object)
    SIGNAL_linkToLastVersion = _signal(object)
    SIGNAL_UpdateTreeWithFilter = _signal(object)
    SIGNAL_breakNoteLink = _signal(object)
    SIGNAL_querySingleNoteContent = _signal(object)




    ## @decorateur_try_except 
    def __init__(self, task_entriesDictList , parent = None ):

        QtGui.QTreeWidget.__init__(self, parent)

        self.task_entriesDictList = task_entriesDictList

        self.pixmap = QtGui.QPixmap( getRessources("add_notes.png")    ).scaled( 16,16, QtCore.Qt.KeepAspectRatio)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.onCustomContextMenuRequested)

        self.itemDoubleClicked.connect(self.editItem)
        self.itemClicked.connect( self.close_editItem )

        self.lastItem_edited = None
        self.setItemDelegate(NoRectDelegate(self ))

        style = "*::item:selected { background-color: transparent ; } "  #  rgba(85,105,10,100%); }  "
        style1 = "*::item:selected:active { background-color: transparent ; } "
        style2 = " "

        style3 = "QTreeWidget {  outline: 0;   selection-background-color: transparent; } "
        

        self.setStyleSheet("*{ outline: 0;} "+style + style1 + style3)
        self.horizontalScrollBar().valueChanged.connect(self.refreshDraw)

        #self.setStyleSheet("* { background-color: rgb(50, 50, 50); }");
    def refreshDraw(self, mustBeAValueHere ) :
        self.viewport().repaint()


    ## @decorateur_try_except 
    def columHasMoved(self, i ,j ,k, save = True  ):
        if save == False :

            pathToDataFile =   os.path.join(getUserTempPath(), "columnOrder.dat") 
            if os.path.isfile(pathToDataFile) :

                headerStateFile = QtCore.QFile( pathToDataFile )
                headerStateFile.open(QtCore.QIODevice.ReadOnly)
                fileBuffer = QtCore.QDataStream(headerStateFile) 
                headerState = QtCore.QByteArray()
                fileBuffer >> headerState
                self.header().restoreState(headerState)
                headerStateFile.close()
        
        else :

            pathToDataFile =   os.path.join(getUserTempPath(), "columnOrder.dat") 
            headerStateFile = QtCore.QFile( pathToDataFile )
            headerStateFile.open(QtCore.QIODevice.WriteOnly)
            fileBuffer = QtCore.QDataStream(headerStateFile) 
            fileBuffer << self.header().saveState()
            headerStateFile.close()

    ## @decorateur_try_except 
    def onCustomContextMenuRequested( self,  pos) :
        item = self.itemAt(pos);
        if ( item ) : 
            self.showContextMenu(item, self.indexAt(pos).column() ,self.viewport().mapToGlobal(pos))
    
    ## @decorateur_try_except
    def showContextMenu(self, item, col, globalPos) :


        if str(item.text(10)).startswith("note_") :
            spawnedTaskNoteList = item.getSpawnedTaskNote()
            if col != 1 :

                menu = QtGui.QMenu()
                
                #statusMenu = menu.addMenu("Set Status")
                menu.addAction(QtGui.QIcon(getRessources("status_opn.png") ) , "Open", lambda: self.SIGNAL_setNoteStatus.emit(([self.selectedItems(), "opn"] ) ) )
                menu.addAction(QtGui.QIcon(getRessources("status_ip.png") )  , "In progress", lambda: self.SIGNAL_setNoteStatus.emit(([self.selectedItems(), "ip"]) ) )
                menu.addAction(QtGui.QIcon(getRessources("status_clsd.png") ), "Close to last Version", lambda: self.SIGNAL_linkToLastVersion.emit(( [self.selectedItems(),"clsd"]) ) )
                menu.addAction(QtGui.QIcon(getRessources("versionArrow.png") ) , "To last Version", lambda: self.SIGNAL_linkToLastVersion.emit(([self.selectedItems(), None] ) ) )
                menu.addSeparator()


                typeMenu = menu.addMenu("Set Type")
                typeMenu.addAction(QtGui.QIcon(getRessources("type_toDo.png") ), "To-do", lambda: self.SIGNAL_setNoteType.emit(( [self.selectedItems(),"To-do"]) ) )
                typeMenu.addAction(QtGui.QIcon(getRessources("type_client.png") ), "Client", lambda: self.SIGNAL_setNoteType.emit(( [self.selectedItems(),"Client"]) ) )
                typeMenu.addAction(QtGui.QIcon(getRessources("type_internal.png") )  , "Internal", lambda: self.SIGNAL_setNoteType.emit(([self.selectedItems(), "Internal"]) ) )
                typeMenu.addAction(QtGui.QIcon(getRessources("type_assetUpdated.png") ) , "Asset Update", lambda: self.SIGNAL_setNoteType.emit(([self.selectedItems(), "Asset Update"] ) ) )
                typeMenu.addAction(QtGui.QIcon(getRessources("type.png") ), "NoType", lambda: self.SIGNAL_setNoteType.emit(( [self.selectedItems(),None]) ) )
                
                
                menu.addAction(QtGui.QIcon(getRessources("sequence.png")), "Select Shot/Asset(s)",  lambda : self.SIGNAL_selectShot.emit( self.selectedItems() )  )
                menu.addSeparator()
                deleteMenu = menu.addAction(QtGui.QIcon(getRessources("TrashRed.png")),"Delete note(s)",  lambda : self.SIGNAL_deleteNotes.emit( [self.selectedItems()] )  )

                menu.exec_(globalPos)
            
            elif col == 1 :

                menu = QtGui.QMenu()

                taskMenu = menu.addMenu("Change Task")
                if len( self.selectedItems() ) != 1 :
                    taskMenu.setEnabled(False)
                for entries in self.task_entriesDictList[1:] :
      
                    actionFct = lambda taskValues=entries["values"] : self.SIGNAL_setNoteTask.emit( [ self.selectedItems(), taskValues ] ) 
                    taskEntry = taskMenu.addAction(QtGui.QIcon(getRessources(entries["icon"]) ), entries["text"], actionFct )
                    currentTask = "NoTask"
                    if item.sgData["tasks"] :
                        currentTask = item.sgData["tasks"][0]["name"]

                    if currentTask in entries["values"] or spawnedTaskNoteList.keys() : 
                        taskEntry.setEnabled(False)



                spawnMenu = menu.addMenu(QtGui.QIcon(getRessources("link.png")),"Spawn Note to")
                
                                    
                for entries in self.task_entriesDictList[1:] :
                    currentTask = "NoTask"
                    if item.sgData["tasks"] :
                        currentTask = item.sgData["tasks"][0]["name"]



                    actionFct = lambda taskValues=entries["values"], spawnedFrom = item.getSpawnedFrom() : self.SIGNAL_setNoteLink.emit( [ self.selectedItems(), taskValues, spawnedFrom ] ) 
                    linkEntry = spawnMenu.addAction(QtGui.QIcon(getRessources(entries["icon"]) ), entries["text"], actionFct )

                    if currentTask in entries["values"] : 
                        linkEntry.setEnabled(False)
                    for taskName in spawnedTaskNoteList.keys() :
                        if taskName in entries["values"] :
                            linkEntry.setEnabled(False)

                menu.addSeparator()
                deleteMenu = menu.addAction( QtGui.QIcon(getRessources("break_link_16.png")), "Break link",  lambda: self.SIGNAL_breakNoteLink.emit(( self.selectedItems()) ) )
                if not spawnedTaskNoteList.keys() :
                    deleteMenu.setEnabled(False)

                if len( self.selectedItems() ) != 1 :
                    spawnMenu.setEnabled(False)
                    deleteMenu.setEnabled(False)

                menu.exec_(globalPos)
       
    ## @decorateur_try_except 
    def selectNote_from_id(self, idNote, taskName) :

        notes = self.findItems("note_%i"%idNote, QtCore.Qt.MatchRecursive,10) 
        self.SIGNAL_querySingleNoteContent.emit([ idNote, taskName ])

        return
        if notes :
            self.clearSelection()
            #self.SIGNAL_UpdateTreeWithFilter.emit(0)
            for note in notes :
                if note.isHidden() : 
                    note.setHidden(False)
                    note.setSelected(True)
                    note.setHidden(True)
                else :
                    note.setSelected(True)
                note.setSelected(False)
        else :
            self.SIGNAL_querySingleNoteContent.emit([ idNote, taskName ])

    ## @decorateur_try_except 
    def selectShot_slot(self):
        self.SIGNAL_selectShot.emit( self.selectedItems() )

    ## @decorateur_try_except
    def setNoteStatus_slot(self, status):
        return


    ## @decorateur_try_except
    def drawTree(self, painter, region ) :
        return

    ## @decorateur_try_except
    def editItem(self, item,  column) :
        
        if column == 0 and str(item.text(10)).startswith("note_") :
            item.setEditableMode(True)
            self.lastItem_edited = item

    ## @decorateur_try_except
    def close_editItem(self, item,  column) :
        
        if self.lastItem_edited :
            if not item.sgData.has_key('id') :
                self.lastItem_edited.setEditableMode(False)
                self.lastItem_edited = None
            elif not self.lastItem_edited.sgData["id"] == item.sgData['id'] :
                self.lastItem_edited.setEditableMode(False)
                self.lastItem_edited = None

    
    def drawRow(self, painter,  option,  index) :
        option.state &= ~QtGui.QStyle.State_HasFocus
        painter.save()
        


        if self.model().hasChildren(index):       
            pass

        elif self.itemFromIndex(index).sgData == None :
            xOff = 0 ; #self.horizontalScrollBar().value()
            #xOff = (option.rect.topLeft().x()-option.rect.topRight().x())/2.0
            testRect = option.rect.adjusted(xOff*-1, 0,0,0 )

            itemFrom = self.itemFromIndex(index)

            if itemFrom.isSelected() :

                painter.fillRect( option.rect, QtGui.QColor(48,166,227, 255) )

                font = painter.font()
                
                font.setPixelSize(12)
                font.setBold(True)
                painter.setFont( font )
                painter.setBrush(QtGui.QBrush(QtCore.Qt.white))
                painter.setPen( QtGui.QPen(QtGui.QColor(255,255,255,255)))
                
                textRect = testRect.adjusted(41, 0, 0 , 0);
                painter.drawText( textRect, QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter, "Create Note")
            else :

                painter.fillRect( option.rect, QtGui.QColor(30,30,30, 255) )

                font = painter.font()
                
                font.setPixelSize(12)
                font.setBold(True)
                painter.setFont( font )
                painter.setBrush(QtGui.QBrush(QtCore.Qt.white))
                painter.setPen( QtGui.QPen(QtGui.QColor(205,205,205,255)))
                textRect = testRect.adjusted(41, 0, 0 , 0);
                painter.drawText( textRect, QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter, "Create Note")
                
            painter.drawPixmap( testRect.topLeft()  , self.pixmap)
            pen = QtGui.QPen(QtGui.QColor(0,0,0,70))
            painter.setPen(pen)
            painter.drawLine(option.rect.bottomLeft(),option.rect.bottomRight() )

        else :
            xOff = 0 ; #self.horizontalScrollBar().value()
            testRect = option.rect.adjusted(xOff*-1, 0,0,0 )

            itemFrom = self.itemFromIndex(index)
            if itemFrom.isSelected() :
                
                gradient = QtGui.QLinearGradient(testRect.topLeft(),testRect.topRight())
                #gradient.setColorAt(0.0, itemFrom.statusColor )
                
                if not index.row() % 2 :
                    painter.fillRect( testRect , QtGui.QColor(0,0,0, 80) )
                    gradient.setColorAt(0.0,   QtGui.QColor(43,149, 204, 255) )
                    gradient.setColorAt(0.7,   QtGui.QColor(43,149, 204, 255) )
                else :
                    painter.fillRect( testRect, QtGui.QColor(0,0,0, 0) )
                    gradient.setColorAt(0.0,   QtGui.QColor(48,166,227, 255) )
                    gradient.setColorAt(0.7,   QtGui.QColor(48,166,227, 255) )

                gradient.setColorAt(0.9, itemFrom.statusColor )
                
                painter.fillRect( testRect, gradient )
                pen = QtGui.QPen(QtGui.QColor(0,0,0,35))
                painter.setPen(pen)
                painter.drawLine(testRect.bottomLeft(),testRect.bottomRight() )

                pen = QtGui.QPen(QtGui.QColor(190,190,190,250))
                painter.setPen(pen)
                
                gradient = QtGui.QLinearGradient(testRect.topLeft(),testRect.topRight())
                gradient.setColorAt(0.0,   QtGui.QColor(230,230, 230, 255) )
                gradient.setColorAt(0.7,   QtGui.QColor(210,210, 210, 255) )
                gradient.setColorAt(0.9,   QtGui.QColor(190,190, 190, 0) )
                

                #( const QPoint & topLeft, const QPoint & bottomRight )

                lineRect =  QtCore.QRect( QtCore.QPoint( testRect.topLeft().x(), testRect.bottomRight().y() ) , testRect.bottomRight()   )
                painter.fillRect( lineRect, gradient )

                

                
                QtGui.QTreeWidget.drawRow(self, painter, option, index )
                

            else :
                if index.row() % 2 :
                    painter.fillRect( testRect, QtGui.QColor(0,0,0, 0) )
                else :
                    painter.fillRect( testRect , QtGui.QColor(0,0,0, 80) )


                QtGui.QTreeWidget.drawRow(self, painter, option, index )
                pen = QtGui.QPen(QtGui.QColor(0,0,0,35))
                painter.setPen(pen)
                painter.drawLine(testRect.bottomLeft(),testRect.bottomRight() )

        painter.restore()
       
    def drawBranches(self, painter, rect, index):
        return 




class joinQueue( Queue.PriorityQueue ) :
    def __init__(self):
        Queue.PriorityQueue.__init__(self)
        self.count = 0

    ## @decorateur_try_except 
    def put(self, args):
        Queue.PriorityQueue.put(self, args)
        self.count += 1
        self.join() 

    ## @decorateur_try_except 
    def task_done(self):
        Queue.PriorityQueue.task_done(self)
        self.count -= 1
        return len(self.queue)

    ## @decorateur_try_except 
    def getCount(self):
        return len(self.queue)

class myQueue( Queue.PriorityQueue ) :
    def __init__(self):
        Queue.PriorityQueue.__init__(self)
        self.count = 0

    ## @decorateur_try_except 
    def put(self,args):
        Queue.PriorityQueue.put(self, args)
        self.count += 1

    ## @decorateur_try_except 
    def getCount(self):
        return self.count

    ## @decorateur_try_except 
    def task_done(self):
        Queue.PriorityQueue.task_done(self)
        self.count -= 1
        return self.count



class Example(QtGui.QWidget):



    def __del__(self):
        print "kill Qthread"
                           
                           

    def __initStyle(self):
        return

    ## @decorateur_try_except 
    def __init__(self ):
        self.__initStyle()

        perr("",True)
        plog("",True)
        pprint("",True)

        QtGui.QWidget.__init__(self)     

        self.queue = None
        self.sgtkQueue = None
        self.SGTK_ENGINE = None
        self.engineName = None
        self._app = None
        self.sg = None
       

        try :
            import sgtk
            self.SGTK_ENGINE = sgtk.platform.current_engine()
            self.engineName = self.SGTK_ENGINE.instance_name
            print "getting engine ok ", self.engineName
        except :
            pass

        if "USE THREADING" :
            self.queue = myQueue() #Queue.PriorityQueue()
            self.sgtkQueue = myQueue()
        else :
            self.queue = joinQueue()
            self.sgtkQueue = joinQueue()

        projectId =  191 
        userDict = None
        self.InitOnShotName = {"id":0}
        self.InitFilterOnTaskName = None
        
       
        try :
            self._app = sgtk.platform.current_bundle()

            projectDict = self._app.context.project
            print "Project :" + str( projectDict ) 
            projectId = projectDict["id"]
            
            userDict = self._app.context.user
            print "User :" + str( userDict ) 


            if self._app.context.task :
                self.InitFilterOnTaskName = self._app.context.task["name"]
            elif self._app.context.step :
                self.InitFilterOnTaskName = self._app.context.step["name"]

            entityDict = self._app.context.entity
            print "Entity : " +  str( entityDict ) 
            
            if entityDict :
                if entityDict["type"] == "Shot" :

                    self.InitOnShotName= entityDict
                    print "Init not manager on shot "+ str(self.InitOnShotName) 
                elif entityDict["type"] == "Asset" :

                    self.InitOnShotName= entityDict
                    print "Init not manager on asset "+ str(self.InitOnShotName) 

        except :
            print "Cant get context entity"





        self.appLauncherDict = { 
                        "layout" : { "tk-multi-launchmaya" :  { "template" : "maya_shot_work" ,  "icon" : "MayaApp.png" } },
                        "Anim"  :  { "tk-multi-launchmaya" :  { "template" : "maya_shot_work" ,  "icon" : "MayaApp.png" } } ,
                        "Compo" :  { "tk-multi-launchnuke"  : { "template" : "nuke_shot_work" ,  "icon" : "NukeApp.png" },
                                     "tk-multi-launchnukeX" : { "template" : "nuke_shot_work" ,  "icon" : "NukeXApp.png" }
                                   },
                        "lighting" : { "tk-multi-launchmaya" :  { "template" : "maya_shot_work" ,  "icon" : "MayaApp.png" } } ,
                        
                        "Fur" : { "tk-multi-launchmaya" :  { "template" : "maya_shot_work" ,  "icon" : "MayaApp.png" },
                                       "tk-multi-launchhoudini" : {"template" : "houdini_shot_work" ,  "icon" : "HoudiniApp.png" }
                                    },
                        "Fx" : { "tk-multi-launchmaya" :  { "template" : "maya_shot_work" ,  "icon" : "MayaApp.png" },
                                       "tk-multi-launchhoudini" : {"template" : "houdini_shot_work" ,  "icon" : "HoudiniApp.png" }
                                    },
                        "modeling" : { "tk-multi-launchmaya" :  { "template" : "maya_asset_work" ,  "icon" : "MayaApp.png" },
                                       "tk-multi-launchhoudini" : {"template" : "houdini_asset_work" ,  "icon" : "HoudiniApp.png" }
                                    },

                        "rigging" : { "tk-multi-launchmaya" :  { "template" : "maya_asset_work" ,  "icon" : "MayaApp.png" },
                                       "tk-multi-launchhoudini" : {"template" : "houdini_asset_work" ,  "icon" : "HoudiniApp.png" }
                                    },
                        "Surface" : { "tk-multi-launchmaya" :  { "template" : "maya_asset_work" ,  "icon" : "MayaApp.png" },
                                       "tk-multi-launchhoudini" : {"template" : "houdini_asset_work" ,  "icon" : "HoudiniApp.png" }
                                    }
                       }
                      

        ############# TASK
        task_entriesDictList = [ {"text" : "All", "icon" : None, "values": []  },
                            {"text" : "Compo", "icon" : "task_compo.png", "values": ["Compositing", "Comp", "Compo"] },
                            {"text" : "lighting", "icon" : "task_lit.png" , "values": ["Lighting", "lighting"]  },
                            {"text" : "Anim", "icon" : "task_animation.png", "values": ["Animation","animation","anim", "Anim"]  },
                            {"text" : "layout", "icon" : "task_layout.png" , "values": ["Layout", "layout"] },
                            {"text" : "Fur", "icon" : "task_fur.png" , "values": ["fur","Fur"] },
                            {"text" : "Fx",  "icon" : "task_fx.png" , "values": [ "fx", "FX", "Fx", "fX" ] },
                            {"text" : "Surface", "icon" : "task_surfacing.png" , "values": ["Surface"] },             
                            {"text" : "modeling", "icon" : "task_modelisation.png" , "values": ["Modeling", "Model" ,"modeling", "retopo"] },
                            {"text" : "rigging", "icon" : "task_rig.png" , "values": ["Rig", "rig", "rigging"] },
                            {"text" : "Art", "icon" : "task_art.png" , "values": ["Art","art"] },  
                            {"text" : "NoTask", "icon" : "task.png" , "values": ["NoTask"] }
                          ]
        
        ############# TYPE

        type_entriesDictList = [ {"text" : "All", "icon" : None , "values":[], "checked" : False},
                            {"text" : "To Do", "icon" : "type_toDo.png", "values":["To-do", "To Do"], "checked" : True },
                            {"text" : "Client", "icon" : "type_client.png", "values":["Client"] , "checked" : False},
                            {"text" : "Internal", "icon" : "type_internal.png" , "values": ["Internal"], "checked" : False},
                            {"text" : "Asset Update", "icon" : "type_assetUpdated.png", "values":["Asset Update"] ,"checked" : False },
                            {"text" : "NoType", "icon" : "type.png" , "values": ["NoType"] , "checked" : False},
                          ]
        ############# STATUS

        status_entriesDictList = [ {"text" : "All", "icon" : None, "values":[]} ,
                            {"text" : "Open", "icon" : "status_opn.png", "values":["opn","Open"], "checked":True} ,
                            {"text" : "In Progress", "icon" : "status_ip.png", "values":["ip","In Progress"]} ,
                            {"text" : "Closed", "icon" : "status_clsd", "values":["clsd", "Closed"] } ,
                          ]


        maskList = self.serialize_comboFilterWidget(False)   
        task_mask = None
        type_mask = None
        status_mask = None

        if maskList :
            task_mask = maskList[0]
            type_mask = maskList[1]
            status_mask = maskList[2]


        if type_mask and len(type_mask) == len(type_entriesDictList) :
            type_entriesDictList = self.setCheckedFromCheckedList(type_entriesDictList, type_mask )   
        else :
            type_entriesDictList = self.setCheckedFromValue(type_entriesDictList, ["To Do", "NoType"] )
        self.typeFilterWidget = comboFilterWidget2( {"name":"Type" , "icon": "type.png"}, type_entriesDictList, multiCheckable = True ) 

        print "creating threads" 
        for i in range(9) :

            sg = sg_query( self._app  )            
            print i,

            if i == 0 :
                self.sg = sg
                sg.setProjectId(projectId, useSGTK = False )
                sg.setTempPath()
                sg.setAppLauncher(self.appLauncherDict)
                sg.setTypeFilterWidget(self.typeFilterWidget)
                task_entriesDictList = sg.get_projectTaskList( task_entriesDictList )

            elif i == 2 and self.engineName in ["tk-shotgun", "tk-desktop", "tk-shell"] :
                self.sg = sg
                sg.setProjectId(projectId, useSGTK = True )
                sg.setTempPath()
                sg.setAppLauncher(self.appLauncherDict)
                sg.setTypeFilterWidget(self.typeFilterWidget)

                sg.queue=self.sgtkQueue
                sg.th_id = i                
                
                sg.SIGNAL_updateLaunchAppWidget.connect(self.updateLauncherWidget)

                sg.start()
                
            else :
                self.sg = sg
                sg.setProjectId(projectId, useSGTK = False )
                sg.setTempPath()
                sg.setAppLauncher(self.appLauncherDict)
                sg.setTypeFilterWidget(self.typeFilterWidget)

                sg.queue=self.queue
                sg.th_id = i                


                sg.SIGNAL_setThumbnail.connect(self.setTreeThumbNail )
                sg.SIGNAL_setNoteList.connect(self.setNoteList )               
                sg.SIGNAL_queryAllShot.connect(self.fillSeqShotTree )
                sg.SIGNAL_queryAllAsset.connect(self.fillAssetTree )
                sg.SIGNAL_clearTree.connect( self.clearTree )
                sg.SIGNAL_queryNoteContent.connect( self.queryNoteContent )
                sg.SIGNAL_replyNote.connect( self.noteTreeUpdated)
                sg.SIGNAL_queryNoteVersion.connect(self.queryNoteVersion)
                sg.SIGNAL_queryVersion.connect(self.updateDrawNote_versions)
                sg.SIGNAL_addNote.connect( self.addNote )
                sg.SIGNAL_refreshNote.connect( self.refreshNote)
                sg.SIGNAL_queryNoteTaskAssigned.connect(self.queryNoteTaskAssigned )
                sg.SIGNAL_setShotAsset_taskAssigned.connect( self.setShotAsset_taskAssigned)
                sg.SIGNAL_getAvailableTasks.connect(self.updateTree1_withFilter )

                sg.SIGNAL_updateLaunchAppWidget.connect(self.updateLauncherWidget)

                sg.SIGNAL_pbar.connect(self.updateProgressBar)

                sg.start()
    

        print "\ncreating threads done\n" 


        if self.InitFilterOnTaskName  :
            task_entriesDictList = self.setCheckedFromValue(task_entriesDictList, [self.InitFilterOnTaskName] + ["NoTask"] )
        elif task_mask and len(task_mask) == len(task_entriesDictList) :
            task_entriesDictList = self.setCheckedFromCheckedList(task_entriesDictList, task_mask )   
        else :
            task_entriesDictList = self.setCheckedFromValue(task_entriesDictList, [None] )

        self.taskFilterWidget =  comboFilterWidget2( {"name":"Task" , "icon": "task.png"}, task_entriesDictList, multiCheckable = True )




        if status_mask :
            status_entriesDictList = self.setCheckedFromCheckedList(status_entriesDictList, status_mask )   
        else :
            status_entriesDictList = self.setCheckedFromValue(status_entriesDictList, ["Open", "ip"] )
        
        self.statusFilterWidget = comboFilterWidget2( {"name":"Status" , "icon": "status.png"}, status_entriesDictList, multiCheckable = True  )







        self.initUI()
     
        self.queue.put( [ 3,u"deleteEmptySpawnLink"  , None , None ]  )
        self.queue.put( [ 3,u"fillSeqShotTree"  , None , None ] )

        self.shotTreeSelection_id_List = []


    @staticmethod
    def setCheckedFromCheckedList(entriesDictList, boolList) :

        idx = 0
        for boolState in boolList :
            entriesDictList[idx]["checked"] = boolState

            idx+=1
        return entriesDictList


    @staticmethod
    def setCheckedFromValue(entriesDictList, valueList ):
        

        for entriesDict  in  entriesDictList :
            if None in valueList :
                entriesDict["checked"] = True
                continue
            for value in valueList :
                if value in entriesDict["values"] :
                    entriesDict["checked"] = True
        return entriesDictList


    ## @decorateur_try_except 
    def serialize_comboFilterWidget(self, save = True) :

        if self.InitFilterOnTaskName :
            return

        
        if save == False :
            
            pathToDataFile =   os.path.join(getUserTempPath(), "noteAppUi_filters.dat") 
            if os.path.isfile(pathToDataFile) :



                taskFilterStates = None
                typeFilterStates = None
                statusFilterStates = None
                try :
                    with open(pathToDataFile) as f :
                        exec( f.read() )
                except :
                    "print cant restore widget state "

                return taskFilterStates, typeFilterStates, statusFilterStates
            
        
        else :


            pathToDataFile =   os.path.join(getUserTempPath(), "noteAppUi_filters.dat") 
            comboFilterStateFile = open( pathToDataFile, "w" )
            comboFilterStateFile.write("# ToDoNote_App comboFilter state \n")
            comboFilterStateFile.write("taskFilterStates = " + str( self.taskFilterWidget.getCheckedBoolList() ) + "\n" )
            comboFilterStateFile.write("typeFilterStates = " + str( self.typeFilterWidget.getCheckedBoolList() ) + "\n" )
            comboFilterStateFile.write("statusFilterStates = " + str( self.statusFilterWidget.getCheckedBoolList() ) + "\n" )

            comboFilterStateFile.close()




    ## @decorateur_try_except 
    def initUI(self):
        self.mainLayout = QtGui.QVBoxLayout() 
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.mainLayout.setSpacing(0)
        self.setLayout(self.mainLayout)
        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)


        self.filteringLayout = QtGui.QHBoxLayout()
        self.filteringLayout.setContentsMargins(0,0,0,0)
        self.refreshUI_Btn =  toggleBtn("")
        self.refreshUI_Btn.setToolTip("- Flush pending operations\n- Refresh current notes if any shot&Asset is selected\nor refresh the shot&asset list otherwise")


        

        self.shotAssetFilterWidget = lineEditFilterWidget( {"name":"Shot/Asset" , "icon": None} )

        self.shotAssetFilterWidget.setToolTip("Ctrl+Enter to select filtered entities ")
        self.userNameFilterWidget  = lineEditFilterWidget( {"name":"Writer" , "icon": "user.png"} )
        self.contentFilterWidget   = lineEditFilterWidget( {"name":"Contains" , "icon": "text.png"} )
        self.entityAssignedFilterWidget  = lineEditFilterWidget( {"name":"Assigned To" , "icon": "thunder-32.png"} )
        self.entityAssignedFilterWidget.setToolTip("Ctrl+Enter to select filtered entities ")
        #### grouping options
        self.groupByTypeBox = QtGui.QCheckBox("Group by Type")
        self.groupByTypeBox.setCheckState(QtCore.Qt.Unchecked)
        self.groupByTypeBox.setTristate(False)

        self.spacerItem =  QtGui.QSpacerItem(1,1)


        self.filteringLayout.setSpacing(10)
        self.filteringLayout.addWidget( self.refreshUI_Btn)

        self.filteringLayout.addWidget( self.shotAssetFilterWidget )
        self.filteringLayout.addWidget( self.taskFilterWidget )
        self.filteringLayout.addWidget( self.entityAssignedFilterWidget )

        self.filteringLayout.addSpacing(20)
        self.filteringLayout.addWidget( self.typeFilterWidget )
        self.filteringLayout.addWidget( self.statusFilterWidget )
        self.filteringLayout.addWidget( self.userNameFilterWidget  )
        self.filteringLayout.addWidget( self.contentFilterWidget )

        #filteringLayout.addWidget(self.groupByTypeBox )
        self.filteringLayout.addStretch()


        leftLayout = QtGui.QVBoxLayout()
        leftLayout.setContentsMargins(2,2,2,2)


        midLayout  = QtGui.QVBoxLayout()

        self.test = midLayout        

        midLayout.setContentsMargins(2,2,2,2)
        self.rightLayout = QtGui.QHBoxLayout()
        self.rightLayout.setContentsMargins(2,2,2,2)
 
        self.myTree = QtGui.QTreeWidget() 
        self.myTree.setIconSize(QtCore.QSize(128,128))
        self.myTree.setColumnCount(11)
        self.myTree.setHeaderLabels(["Shots/Assets","Note count"])
        self.myTree.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.myTree.setFocusPolicy(QtCore.Qt.NoFocus)
        self.myTree.setSortingEnabled(True)

        self.myTree2 = myQTree( self.taskFilterWidget.entriesDictList )# QtGui.QTreeWidget() 
        self.myTree2.setIconSize(QtCore.QSize(128,128))
        self.myTree2.setColumnCount(11)
        self.myTree2.setHeaderLabels(["Note Content","Tasks", "Type","Created_at", "Writer", "v---", "Shot/Asset", "Replies", "Assignement", "Created_at"])
        self.myTree2.setSortingEnabled(True)
        self.myTree2.setExpandsOnDoubleClick(False)

        self.myTree2.setAlternatingRowColors(0);
        self.myTree2.setIndentation(0)
        self.myTree2.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        p = QtGui.QPalette()
        p.setColor( QtGui.QPalette.AlternateBase, QtGui.QColor(0, 0, 0, 18) );
        self.myTree2.setPalette(p)

        
        header = self.myTree.header()
        for column in range(1, self.myTree.columnCount()):
            header.hideSection(header.logicalIndex(header.visualIndex(column)))
            
        
        header = self.myTree2.header()
        header.setResizeMode(0, QtGui.QHeaderView.Interactive)
        header.setResizeMode(1, QtGui.QHeaderView.ResizeToContents)
        header.setResizeMode(2, QtGui.QHeaderView.ResizeToContents)
        header.setResizeMode(3, QtGui.QHeaderView.ResizeToContents)
        header.setResizeMode(6, QtGui.QHeaderView.ResizeToContents)
        header.setResizeMode(7, QtGui.QHeaderView.ResizeToContents)
        header.setResizeMode(8, QtGui.QHeaderView.ResizeToContents)
        header.setResizeMode(9, QtGui.QHeaderView.ResizeToContents)
        for column in range(10, self.myTree2.columnCount()):
            header.hideSection(header.logicalIndex(header.visualIndex(column)))
        
        header.hideSection(header.logicalIndex(3))

        header.swapSections(6,7)

        
        for column in range( self.myTree2.columnCount() ):
            self.myTree2.resizeColumnToContents( column )
        

        leftLayout.addWidget(self.myTree)
        midLayout.addWidget(self.myTree2)


        self.rightLayout.addWidget( noteLayoutWidget( None,  [ self.getShotItemList() , self.taskFilterWidget, self.typeFilterWidget, self.statusFilterWidget, self.shotAssetFilterWidget, self.entityAssignedFilterWidget  ], threadQueue = self.queue, sgtkQueue = self.sgtkQueue ) )
        

        wFiltering = QtGui.QWidget()
        wFiltering.setLayout(self.filteringLayout)
        horizontalSplitter = QtGui.QSplitter() 
        horizontalSplitter.addWidget(wFiltering)
        horizontalSplitter.setOrientation(QtCore.Qt.Vertical)

        horizontalSplitter.setObjectName("verti")

        self.mainLayout.addWidget(horizontalSplitter)


        self.progressBar = QtGui.QProgressBar()
        self.progressBar.setFixedHeight(5)
        self.progressBar.setValue(50)
        self.progressBar.setTextVisible(False)
        style = """QProgressBar {
                     border: 0px solid grey;
                     border-radius: 0px;
                 }

                 QProgressBar::chunk {
                     background-color: #30A6E3;
                     width: 20px;
                 }"""

        self.progressBar.setStyleSheet(style)

        self.mainLayout.addWidget(self.progressBar)

        self.splitter = QtGui.QSplitter()
        self.splitter.setObjectName("hori")
  

        style = "QSplitter::handle:vertical#verti {  background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(255, 120, 150, 0% ),stop:0.5 rgba(140, 140, 140, 100% ), stop:1 rgba(120, 120, 150, 0% ) );border: 1px solid rgba(120, 120, 150, 0% ) ; width : 1px ; height : 1px ;margin-right: 2px;margin-left: 2px;border-radius: 4px;}\n"
        style += "QSplitter::handle:horizontal#hori {background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(255, 120, 150, 0% ),stop:0.5 rgba(140, 140, 140, 100% ), stop:1 rgba(120, 120, 150, 0% ) );border: 1px solid rgba(120, 120, 150, 0% ) ;width: 13px;margin-top: 2px;margin-bottom: 2px;border-radius: 4px;}"
        

        self.splitter.setStyleSheet(style )
        horizontalSplitter.setStyleSheet(style )

       

        ok = QtGui.QWidget()
        ok.setLayout(leftLayout)      
        
        ok2 = QtGui.QWidget()
        ok2.setLayout(midLayout)

        ok3 = QtGui.QWidget()
        ok3.setLayout(self.rightLayout)



        

        self.splitter.addWidget(ok)
        self.splitter.addWidget(ok2)
        self.splitter.addWidget(ok3)

        
        splitSize = self.splitter.size().width()
        
        col1 = int(splitSize/3)
        col2 = int(splitSize/5)
        if self.InitOnShotName["id"] :
            col1 = 0.0
        else :
            col1= 280.0
        self.splitter.setSizes([ col1,col2, splitSize-(col1+col2)])



        layout.addWidget(self.splitter)
        horizontalSplitter.addWidget(self.splitter)
        horizontalSplitter.setStretchFactor( 0, 0 )
        horizontalSplitter.setStretchFactor( 1, 1 )

        self.splitter.setStretchFactor( 0, 0 )
        self.splitter.setStretchFactor( 1, 1 )
        self.splitter.setStretchFactor( 2, 0 )



        self.updateLauncherWidget( [{"clear":True}, 0 , "", "", [] ]) 



        self.serialize_comboFilterWidget(False)



        #self.splitter.splitterMoved.connect(self.resizeFilterLayout  )

        self.myTree.itemSelectionChanged.connect(self.shotTreeClicked )
        self.refreshUI_Btn.clicked.connect(   self.flush  ) 

        self.taskFilterWidget.widget.currentIndexChanged.connect( self.updateTree2_withFilter )
        self.typeFilterWidget.widget.currentIndexChanged.connect( lambda : self.shotTreeClicked( True ) )
        self.statusFilterWidget.widget.currentIndexChanged.connect( self.updateTree2_withFilter )
        self.userNameFilterWidget.widget.textChanged.connect(self.updateTree2_withFilter)
        self.contentFilterWidget.widget.textChanged.connect(self.updateTree2_withFilter)
        self.entityAssignedFilterWidget.widget.textChanged.connect(self.updateTree2_withFilter)
        self.shotAssetFilterWidget.widget.textChanged.connect(self.updateTree2_withFilter)

        self.shotAssetFilterWidget.widget.textChanged.connect(self.updateTree1_withFilter)
        self.entityAssignedFilterWidget.widget.textChanged.connect(self.updateTree1_withFilter)
        self.taskFilterWidget.widget.currentIndexChanged.connect(self.updateTree1_withFilter)

        self.shotAssetFilterWidget.widget.returnPressed.connect(self.selectFrom_ReturnPressed )
        self.entityAssignedFilterWidget.widget.returnPressed.connect(self.selectFrom_ReturnPressed )

        self.myTree2.itemSelectionChanged.connect(self.noteTreeClicked )

        self.myTree2.SIGNAL_breakNoteLink.connect(self.breakNoteLink)
        self.myTree2.SIGNAL_setNoteStatus.connect(self.setNoteStatus)
        self.myTree2.SIGNAL_setNoteType.connect(self.setNoteType)
        self.myTree2.SIGNAL_selectShot.connect(self.selectShotMyTree)
        self.myTree2.SIGNAL_deleteNotes.connect(self.deleteNotes)
        self.myTree2.SIGNAL_updateNoteContent.connect(self.updateNoteContent)
        self.myTree2.SIGNAL_setNoteTask.connect(self.setNoteTask)
        self.myTree2.SIGNAL_setNoteLink.connect(self.setNoteLink)
        self.myTree2.SIGNAL_linkToLastVersion.connect(self.linkToLastVersion)
        self.myTree2.SIGNAL_UpdateTreeWithFilter.connect(self.updateTree2_withFilter)
        self.myTree2.SIGNAL_querySingleNoteContent.connect(self.querySingleNoteContent)



        self.myTree2.header().sectionMoved.connect(self.myTree2.columHasMoved)
        self.myTree2.header().sectionResized.connect(self.myTree2.columHasMoved)
        self.myTree2.header().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.myTree2.header().customContextMenuRequested.connect(self.myTree2headerMenu)

        self.groupByTypeBox.stateChanged.connect(self.refreh_myTree2)


        self.taskFilterWidget.widget.currentIndexChanged.connect(lambda : self.serialize_comboFilterWidget( True ) )
        self.typeFilterWidget.widget.currentIndexChanged.connect(lambda : self.serialize_comboFilterWidget( True ) )
        self.statusFilterWidget.widget.currentIndexChanged.connect(lambda : self.serialize_comboFilterWidget( True ) )


        self.spacerItem.changeSize(col1-14, 1)
        self.filteringLayout.invalidate()

        self.myTree2.columHasMoved(0,0,0, False)


        header.setResizeMode(0, QtGui.QHeaderView.Interactive)

        self.show()


    ## @decorateur_try_except
    def resizeFilterLayout(self, pos, idx):

        if idx == 1 :
             
            self.spacerItem.changeSize(pos-14, 1)
            self.filteringLayout.invalidate()


    ## @decorateur_try_except
    def findInTree(self, sg_id, parent = None):
        root = self.myTree
        if parent :
            root = parent
        
        #return root.findItems( sg_id, QtCore.Qt.MatchExactly, 10 ) 
        return root.findItems( sg_id, QtCore.Qt.MatchRecursive,10 )


    ## @decorateur_try_except
    def getNoteTaskNameList(self, noteDict ) :
        taskList = []
        if  noteDict["tasks"] :
            return [ self.taskFilterWidget.retrieveNameFromValue(noteDict["tasks"][0]["name"] ) ]

        if not taskList :
            return ["NoTask"]

        return  taskList


    ## @decorateur_try_except
    def clearRightLayout(self) :
        for i in reversed(range(self.rightLayout.count())):   
            wid =  self.rightLayout.itemAt(i).widget()
            wid.setParent(None)
            wid.deleteLater()






    #############################################
    #########
    #########
    #########
    #########      SLOTS CONNECTED TO THE UI
    #####
    ##### every method below are call on UI events
    ##### They mainly send job to the threading class 
    #########
    #########
    #########
    #############################################


    ## @decorateur_try_except
    def breakNoteLink(self, itemList ) :
        self.queue.put( [ 0 , u"breakSpawnLink" ,  [ itemList[0].sgData["spawnLinkId"],  itemList[0].sgData["shotId"],  itemList[0].sgData["shotCode"],  itemList[0].sgData["shotType"]  ]  , None ] )

    ## @decorateur_try_except
    def querySingleNoteContent(self, noteId_taskName ) :
        noteId = noteId_taskName[0]
        taskName = noteId_taskName[1]

        taskValues = self.taskFilterWidget.retrieveValueFromName(taskName)

        self.queue.put( [ 0 , u"queryNoteContent"  , [{"id":noteId,"taskValues": taskValues, 'mustDisplay':True }] , None ] )

    ## @decorateur_try_except
    def updateNoteContent(self, obj ):
        #[0] note content
        #[1] note id
        
        self.queue.put( [ 0 , u"editNoteContent" ,  obj , None ] )
        #
    
    ## @decorateur_try_except
    def refreh_myTree2(self, state) :
        return

    ## @decorateur_try_except
    def setNoteStatus(self, itemListAndStatus_list):
        for item in itemListAndStatus_list[0]:
            noteId = 0 
            if item.sgData.has_key('id') :
                noteState = {"new_sg_status_list":itemListAndStatus_list[1], "id" : item.sgData['id']}
                self.queue.put( [ 0 , u"setNoteStatus" , [noteState, item.sgData] , None ] )

    
    ## @decorateur_try_except
    def setNoteType(self, itemListAndType_list):
        for item in itemListAndType_list[0]:
            noteId = 0 
            if item.sgData.has_key('id') :
                noteType = {"new_sg_note_type":itemListAndType_list[1], "id" : item.sgData['id']}
                self.queue.put( [ 0 , u"setNoteType" , [noteType] , None ] )
    
    ## @decorateur_try_except
    def linkToLastVersion(self, selectedNoteList) :
        for item in selectedNoteList[0]:
            noteId = 0
            if item.sgData.has_key('id') :

                taskValuesList = []
                if item.sgData["tasks"] :
                    taskValuesList = self.taskFilterWidget.retrieveValueFromName(item.sgData["tasks"][0]["name"])
                self.queue.put( [ 0 , u"linkToLastVersion" , [  item.sgData['shotId'],  taskValuesList , item.sgData['id'], item.sgData['shotType'], item.sgData['shotCode'] , selectedNoteList[1]  ] , None ] )           

    ## @decorateur_try_except
    def setNoteLink(self, itemListAndTaskValues_list) :
        for item in itemListAndTaskValues_list[0] :
            if item.sgData.has_key('id') :

                self.queue.put( [ 0 , u"setNoteLink" , [item.sgData, itemListAndTaskValues_list[1], itemListAndTaskValues_list[2] ] , None ] )

    ## @decorateur_try_except
    def setNoteTask(self, itemListAndTaskValues_list) :

        for item in itemListAndTaskValues_list[0] :
            if item.sgData.has_key('id') :


                self.queue.put( [ 0 , u"setNoteTask" , [item.sgData, itemListAndTaskValues_list[1] ] , None ] )
    
    ## @decorateur_try_except
    def deleteNotes(self, itemList ) :
        for item in itemList[0]:
            if not item.sgData.has_key("spawnLinkId") :
                if item.sgData.has_key('id') :
                    #noteType = {"new_sg_note_type":itemListAndType_list[1], "id" : item.sgData['id']}
                    self.queue.put( [ 0 , u"deleteNote" , [item.sgData['id']] , None ] )

    ## @decorateur_try_except
    def multiReplyNoteSlot(self, obj):
        self.queue.put( [ 0 , u"multyReplyNote" , obj , None ] )
        #self.queue.join()

    ## @decorateur_try_except
    def replyNoteSlot(self, obj) :
        self.queue.put( [ 0 , u"replyNote" , obj , None ] )
        #

    ## @decorateur_try_except
    def litNoteWidgetItem(self) :
        for noteItemWidget in self.myTree2.findItems("note_", QtCore.Qt.MatchStartsWith | QtCore.Qt.MatchRecursive,10) :
            noteItemWidget.litTaskLink()

    ## @decorateur_try_except
    def noteTreeClicked(self) :

        """
        while not self.queue.empty() :
            self.queue.get()

            self.queue.task_done()
        self.queue.join()
        """


        selectedItemList = self.myTree2.selectedItems()
        
        taskList = []
        noteData = []
        for itemW in selectedItemList :

            if str(itemW.text(10)).startswith("note") :
                if itemW.sgData["tasks"] :
                    taskValues = self.taskFilterWidget.retrieveValueFromName(itemW.sgData["tasks"][0]['name'])
                    itemW.sgData["taskValues"] = taskValues
                else :
                    itemW.sgData["taskValues"] = []
                
                noteData.append( itemW.sgData )
    

            elif str(itemW.text(10)).startswith("task") :
                taskList.append(str( itemW.text(0) ) )



        self.litNoteWidgetItem()

        if noteData :
            if len(noteData) == 1 :

                taskValues = [] 
                taskName = ""
                if noteData[0]["tasks"] :
                    taskValues = self.taskFilterWidget.retrieveValueFromName( noteData[0]["tasks"][0]["name"] )
                    taskName =   self.taskFilterWidget.retrieveNameFromValue( noteData[0]["tasks"][0]["name"] )
    
                if not taskValues :
                    taskName = "NoTask"
                    taskValues = [ "NoTask" ]

                # flushSgtkQueue
                while not self.sgtkQueue.empty():
                    try:
                        self.sgtkQueue.get(False)
                    except Empty:
                        continue
                    self.sgtkQueue.task_done()

                self.sgtkQueue.put([-5, u"getExecutable",   [noteData[0]["shotId"], taskValues, taskName , noteData[0]["shotCode"], noteData[0]["shotType"] ] , None ] )

            self.queue.put( [ 0 , u"queryNoteContent"  , noteData , None ] )

        else : # selectedItemList :
            self.drawNote(taskList)

    ## @decorateur_try_except
    def drawNote(self, taskList = []):
        

        QtGui.QApplication.processEvents()
        my_noteLayoutWidget = noteLayoutWidget( None,  [ self.getShotItemList(), self.taskFilterWidget, self.typeFilterWidget, self.statusFilterWidget, self.shotAssetFilterWidget, self.entityAssignedFilterWidget ],  threadQueue = self.queue, sgtkQueue = self.sgtkQueue )
        self.clearRightLayout()
        self.rightLayout.addWidget(  my_noteLayoutWidget  )
        my_noteLayoutWidget.SIGNAL_send_NoteContent.connect( self.createNewNote )
        my_noteLayoutWidget.updateTaskFilterWidget([])
        my_noteLayoutWidget.SIGNAL_createReply.connect( self.replyNoteSlot )
        my_noteLayoutWidget.SIGNAL_createMultiReply.connect( self.multiReplyNoteSlot )
        
        
        if my_noteLayoutWidget.receiveFocusWidget :
            if not self.shotAssetFilterWidget.widget.hasFocus() :
                my_noteLayoutWidget.receiveFocusWidget.setFocus()
        
        QtGui.QApplication.processEvents()

    ## @decorateur_try_except
    def createNewNote(self, obj) :
        
        self.queue.put( [ 0 , u"createNote"  , [ obj ] , None ] )
        #

    ## @decorateur_try_except
    def flush(self) :
        while not self.queue.empty():
            try:
                self.queue.get(False)
            except Empty:
                continue
            self.queue.task_done()


        if not self.myTree.selectedItems() :
            self.myTree.clear()
            self.myTree2.clear()
            self.queue.put( [ 3,u"deleteEmptySpawnLink"  , None , None ]  )
            self.queue.put( [ 3,u"fillSeqShotTree"  , None , None ] )


        self.shotTreeClicked(True) 


    def selectFrom_ReturnPressed(self) :
        if self.shotAssetFilterWidget.widget.text() == "" and self.entityAssignedFilterWidget.widget.text() == "":
            return
        else :
            QtGui.QApplication.processEvents()
            self.myTree.clearSelection()


            root = self.myTree.invisibleRootItem()
        
            child_count = root.childCount()
            for i in range(child_count):
                item = root.child(i)
                for j in range(item.childCount() ) :
                    shotAssetItem = item.child(j) 
                    if not shotAssetItem.isHidden() :
                        shotAssetItem.setSelected(True)

            self.shotTreeClicked(True) 
    ## @decorateur_try_except
    def shotTreeClicked(self, forceRedraw = False) :
        QtGui.QApplication.processEvents()

        if not self.myTree.selectedItems() :
            self.updateLauncherWidget( [{"clear":True}, 0 , "", "" ,[] ]) 


        if not forceRedraw :
            redrawTreeNote = False
            newItems = []
            temp_shotTreeSelection_id_List = []
            for itemW in self.myTree.selectedItems() :
                temp_shotTreeSelection_id_List.append( itemW.text(10) )
                if not itemW.isHidden() and itemW.text(10) not in self.shotTreeSelection_id_List:
                    newItems.append(itemW)

            for prevSelId in self.shotTreeSelection_id_List :
                if not prevSelId in temp_shotTreeSelection_id_List :
                    newItems = self.myTree.selectedItems()
                    redrawTreeNote = True # si un item a été deselectionner j'efface tout

            self.shotTreeSelection_id_List = temp_shotTreeSelection_id_List
        else :
            redrawTreeNote = True
            newItems = self.myTree.selectedItems()


        if redrawTreeNote  :
            #self.queue.put( [-10000 ,u"clearTree" , self.myTree2, None]  )
            self.clearTree( [self.myTree2] )
            """
            self.myTree2.clear()
            self.myTree2.lastItem_edited = None
            """

        selectedItemList = newItems 

        shotItemList = []
        for itemW in selectedItemList :
            if str(itemW.text(10)).startswith("shotAsset") :

                if not itemW.sgData in shotItemList and not itemW.isHidden() :
                    shotItemList.append(itemW.sgData )

            if str(itemW.text(10)).startswith("sequence") or str(itemW.text(10)).startswith("assetType")  :


                for shotWItem in itemW.getShotWidgetList() :
                    if not shotWItem.sgData in shotItemList and not shotWItem.isHidden() :
                        shotItemList.append(shotWItem.sgData )
        
        for sgData in shotItemList :
            self.queue.put( [1, u"queryNotes"  , sgData, None ] )
            #

        self.drawNote() 

    ## @decorateur_try_except
    def getShotItemList(self, opt = None):
        shotItemList = []
        for itemW in self.myTree.selectedItems() :
            if str(itemW.text(10)).startswith("shotAsset") :
                if not itemW.sgData in shotItemList :
                    shotItemList.append(itemW.sgData )

            if str(itemW.text(10)).startswith("sequence") :
                for shotWItem in itemW.getShotWidgetList() :
                    if not shotWItem.sgData in shotItemList :
                        shotItemList.append(shotWItem.sgData )

            if str(itemW.text(10)).startswith("assetType") :
                for shotWItem in itemW.getShotWidgetList() :
                    if not shotWItem.sgData in shotItemList :
                        shotItemList.append(shotWItem.sgData )                

        if QtCore.Qt.AscendingOrder == self.myTree.header().sortIndicatorOrder() :        
            return  sorted(shotItemList, key=itemgetter('code'))
        else :
            return  sorted(shotItemList, key=itemgetter('code'), reverse = True)

    ## @decorateur_try_except   
    def updateTree2_withFilter(self, idx = None):

        self.iterateTree2()
        self.iterateTree2_HideEmptyBranch()

    ## @decorateur_try_except 
    def iterateTree2(self, root = None ) :
        if not root : 
            root = self.myTree2.invisibleRootItem()
        
        child_count = root.childCount()
        for i in range(child_count):
            item = root.child(i)
            if hasattr(item, "do_hidding") :
                if not item.do_hidding() :
                    self.iterateTree2(item)


    def updateTree1_withFilter(self, udx= None, root = None ) :



        if not root : 
            root = self.myTree.invisibleRootItem()
        filterText = self.shotAssetFilterWidget.getText()
        assigneesText = self.entityAssignedFilterWidget.getText()
        taskFilterList = self.taskFilterWidget.getfilterList()
        


        child_count = root.childCount()
        for i in range(child_count):
            item = root.child(i)
            if hasattr(item, "do_hidding") :
                if not item.do_hidding( filterText, assigneesText, taskFilterList ) : 
                    self.updateTree1_withFilter(root = item) 
  
            else :
                self.updateTree1_withFilter(root = item) 

        child_count = self.myTree.invisibleRootItem().childCount()
        for i in range(child_count):
            group_shotAssetCount = self.myTree.invisibleRootItem().child(i).childCount()
            numHiddenItem = 0
            for j in range(group_shotAssetCount): 
                numHiddenItem += int( self.myTree.invisibleRootItem().child(i).child(j).isHidden() )

            self.myTree.invisibleRootItem().child(i).setHidden( numHiddenItem == group_shotAssetCount )
            if udx or assigneesText :
                self.myTree.invisibleRootItem().child(i).setExpanded( not numHiddenItem == group_shotAssetCount )

    ## @decorateur_try_except
    def iterateTree2_HideEmptyBranch(self, root = None ) :

        for item in self.myTree2.findItems("type_", QtCore.Qt.MatchStartsWith | QtCore.Qt.MatchRecursive, 10) :
            numHiddenItem = 0
            
            child_count = item.childCount()
            for i in range(child_count):
                numHiddenItem += int( item.child(i).isHidden() )

            if numHiddenItem == child_count :
                item.setHidden(True)

        for item in self.myTree2.findItems("task_", QtCore.Qt.MatchStartsWith, 10) :
            numHiddenItem = 0
            
            child_count = item.childCount()
            for i in range(child_count):
                numHiddenItem += int( item.child(i).isHidden() )

            if numHiddenItem == child_count :
                item.setHidden(True)

    ## @decorateur_try_except
    def selectShotMyTree(self, shotItemList) :
        seqList = []
        assetList = []

        self.myTree.clearSelection()
        for item in shotItemList :

            for myTreeItem in  self.myTree.findItems( item.sgData["shotCode"] , QtCore.Qt.MatchRecursive, 0 ) :
                
                if myTreeItem.sgData.has_key("sg_sequence") :
                    seqItem = myTreeItem.sgData["sg_sequence"]
                    if not seqItem :
                        seqItem={"name" : "No Sequence"}
                    if not seqItem["name"] in seqList :
                        seqList.append(seqItem["name"])

                    myTreeItem.setSelected(True)
                
                elif myTreeItem.sgData.has_key("sg_asset_type") :
                    assetItem = myTreeItem.sgData["sg_asset_type"]
                    
                    if not assetItem :
                        assetItem={"name" : "No Asset Type"}
                    else :
                        assetItem={"name" : assetItem }
                    if not assetItem["name"] in assetList :
                        assetList.append(assetItem["name"])

                    myTreeItem.setSelected(True)

        for i in range(self.myTree.topLevelItemCount()) :
            item = self.myTree.topLevelItem(i)
            if item.sgData["name"] in seqList+assetList:
                item.setExpanded(True)
            else :
                item.setExpanded(False)

        self.drawNote()


    ## @decorateur_try_except 
    def toggleColumnDisplay(self, test ,index ) :
        header = self.myTree2.header() 


        if header.isSectionHidden(header.logicalIndex(header.visualIndex(index)) )  :
            header.showSection(header.logicalIndex(header.visualIndex(index))) 
        else :
            header.hideSection(header.logicalIndex(header.visualIndex(index))) 

        self.myTree2.columHasMoved(0,0,0, save=True)


    ## @decorateur_try_except
    def myTree2headerMenu(self ,  pos) :


        globalPos = self.myTree2.mapToGlobal(pos);


        menu = QtGui.QMenu()
        
        header = self.myTree2.header() 
        fct = lambda test, index = 0 : self.toggleColumnDisplay(test, index)
        act =  QtGui.QAction("Content", menu, checkable=True, checked= not self.myTree2.header().isSectionHidden( header.logicalIndex(header.visualIndex(0)) ) )
        act.triggered.connect(fct)
        menu.addAction( act )


        fct = lambda test, index = 1 : self.toggleColumnDisplay(index, index)
        act =  QtGui.QAction("Tasks"  , menu, checkable=True, checked= not self.myTree2.header().isSectionHidden( header.logicalIndex(header.visualIndex(1)) ) )
        act.triggered.connect(fct)
        menu.addAction( act )

        fct = lambda test, index = 2 : self.toggleColumnDisplay(index, index)
        act =  QtGui.QAction("Type"  , menu, checkable=True, checked= not self.myTree2.header().isSectionHidden( header.logicalIndex(header.visualIndex(2)) ) )
        act.triggered.connect(fct)
        menu.addAction( act )

        fct = lambda test, index = 9 : self.toggleColumnDisplay(index, index)
        act =  QtGui.QAction("Created_at" , menu, checkable=True, checked= not self.myTree2.header().isSectionHidden( header.logicalIndex(header.visualIndex(9)) ) )
        act.triggered.connect(fct)
        menu.addAction( act )

        fct = lambda test, index = 4 : self.toggleColumnDisplay(index, index)
        act =  QtGui.QAction("user"  , menu, checkable=True, checked= not self.myTree2.header().isSectionHidden( header.logicalIndex(header.visualIndex(4)) ) )
        act.triggered.connect(fct)
        menu.addAction( act )

        fct = lambda test, index = 5 : self.toggleColumnDisplay(index, index)
        act =  QtGui.QAction("Version Number (v---)"  , menu, checkable=True, checked= not self.myTree2.header().isSectionHidden( header.logicalIndex(header.visualIndex(5)) ) )
        act.triggered.connect(fct)
        menu.addAction( act )

        fct = lambda test, index = 6 : self.toggleColumnDisplay(index, index)
        act =  QtGui.QAction("Shot/Asset" , menu, checkable=True, checked= not self.myTree2.header().isSectionHidden( header.logicalIndex(header.visualIndex(6)) ) )
        act.triggered.connect(fct)
        menu.addAction( act )

        fct = lambda test, index = 7 : self.toggleColumnDisplay(index, index)
        act =  QtGui.QAction("Replies" , menu, checkable=True, checked= not self.myTree2.header().isSectionHidden( header.logicalIndex(header.visualIndex(7)) ) )
        act.triggered.connect(fct)
        menu.addAction( act )

        fct = lambda test, index = 8 : self.toggleColumnDisplay(index, index)
        act =  QtGui.QAction("Assignement" , menu, checkable=True, checked= not self.myTree2.header().isSectionHidden( header.logicalIndex(header.visualIndex(8)) ) )
        act.triggered.connect(fct)
        menu.addAction( act )


        menu.exec_(globalPos)




















    ############################################
    #####
    #####       SLOTS CONNECTED TO THE THREADING CLASS
    #####
    ##### every method below will be call after a thread'complete  
    ##### they update the UI with data computed by the threading class. 
    #####
    #####
    ############################################

    def setShotAsset_taskAssigned(self, obj):
        print "********* ", obj
        # obj[0] entity type
        # obj[1] entity id
        # obj[2] taskAssgined List

        #self.myTree.findItems( )
        return

    ## @decorateur_try_except
    def updateLauncherWidget(self, obj) :


        if not self.engineName in ["tk-shotgun", "tk-desktop", "tk-shell"] :
            return 
        if not self.SGTK_ENGINE :
            return


        QtGui.QApplication.processEvents()
        w = self.mainLayout.itemAt(2)
        if w :
            bar = w.widget()
            if obj[1] == 0 :
                bar.setParent(None)
                bar.deleteLater()            
                self.mainLayout.addWidget( LaunchApp_widget( obj[0], obj[1], obj[2], obj[3], obj[4]   ,empty = True,  SGTK_ENGINE=self.SGTK_ENGINE ,parent = self ) )
                QtGui.QApplication.processEvents()
                return 
            
            if bar.shotId == obj[1] and bar.taskName == obj[2] :

                if obj[0].has_key("clear"):
                    return
                else :
                    if bar.empty :

                        bar.setParent(None)
                        bar.deleteLater()
                        self.mainLayout.addWidget( LaunchApp_widget( obj[0], obj[1], obj[2], obj[3], obj[4]   , SGTK_ENGINE=self.SGTK_ENGINE, parent = self)  )
                        QtGui.QApplication.processEvents()
                    #QtGui.QApplication.processEvents()
                    return
            else :

                if obj[0].has_key("clear") :
                    bar.setParent(None)
                    bar.deleteLater()
                    self.mainLayout.addWidget(  LaunchApp_widget( obj[0], obj[1], obj[2], obj[3], obj[4]   , empty = True , SGTK_ENGINE=self.SGTK_ENGINE,  parent = self )  )
                    QtGui.QApplication.processEvents()
                else :
                    return
                    
        else :
            self.mainLayout.addWidget( LaunchApp_widget( obj[0], obj[1], obj[2], obj[3], obj[4]   , empty = True ,  SGTK_ENGINE=self.SGTK_ENGINE , parent = self )   )


        if not obj[0].has_key("clear") :
            self.mainLayout.addWidget( LaunchApp_widget( obj[0], obj[1], obj[2], obj[3], obj[4]   ,  SGTK_ENGINE=self.SGTK_ENGINE, parent = self )  )



    ## @decorateur_try_except
    def updateProgressBar(self, value) :
        self.progressBar.setValue(value)
 
    ## @decorateur_try_except
    def refreshNote(self, obj):
        for noteItemWidget in self.myTree2.findItems( "note_%i"%obj[0]['id'], QtCore.Qt.MatchRecursive, 10 ) :

            noteDict = None
            if not obj[1] : 
                noteDict = noteItemWidget.sgData
                if obj[0].has_key("new_sg_note_type") :
                    noteDict["sg_note_type"] = obj[0]["new_sg_note_type"]
            else :
                noteDict = obj[0]

            noteItemWidget.parent().removeChild(noteItemWidget)
            

            if not obj[1] == u"Delete" :
                self.addNote([noteDict])
        self.updateTree2_withFilter()
  
    ## @decorateur_try_except
    def addNote(self, obj ) :

        for noteDict in obj : # boucler chaques notes

            #it can have more than one task per note in shotgun   
            taskList = self.getNoteTaskNameList(noteDict) 

            for taskName in taskList : # trouver le task tree widget, peut y'en a voir plusieurs. une note peut etre linker a pluseiurs tasks  

                taskWidgetItem = None
                taskWidgetItemList = self.myTree2.findItems( "task_%s"%"dontCarre" , QtCore.Qt.MatchExactly, 10 )
                if not taskWidgetItemList :
                    taskWidgetItem = taskWidget(self.myTree2, {"name": "dontCarre"}, self.taskFilterWidget )
                else :
                    taskWidgetItem = taskWidgetItemList[0]


                noteWidget( taskWidgetItem, noteDict, self.taskFilterWidget, self.statusFilterWidget, self.typeFilterWidget, self.userNameFilterWidget, self.contentFilterWidget,  self.entityAssignedFilterWidget, self.shotAssetFilterWidget  )
                taskWidgetItem.setHidden(False)


                taskValuesList = self.taskFilterWidget.retrieveValueFromName( taskName )
                self.queue.put( [ 2 , u"queryNoteVersion"  , [ noteDict["shotId"] ,taskValuesList  ,noteDict["id"], noteDict["shotType"] ] , None ] )
                
                self.queue.put( [ 2 , u"queryTaskAssigned"  , [{'id' : noteDict["shotId"],'type' : noteDict["shotType"]}, taskValuesList,  noteDict["id"]]   , None ] )
                        #

    ## @decorateur_try_except           
    def updateDrawNote_versions(self, obj) :

        noteLayoutQItem = self.rightLayout.itemAt(0)
        if noteLayoutQItem :
            noteLayoutWidget= noteLayoutQItem.widget()
            if noteLayoutWidget.data == None:
                noteLayoutWidget.fill_versionWidgetCombo(obj)
    
    #
    ## @decorateur_try_except
    def setTreeThumbNail(self, obj) :
        treeWidgetItemList =  self.findInTree(obj[0])

        for  treeWidgetItem in treeWidgetItemList :
            treeWidgetItem.setIcon(0, QtGui.QIcon(obj[1]))

                
    ## @decorateur_try_except
    def getShotIds(self, opt = None):
        shotItemList = []
        for itemW in self.myTree.selectedItems() :
            if str(itemW.text(10)).startswith("shotAsset") :
                if not itemW.text(10) in shotItemList :
                    shotItemList.append(itemW.text(10) )

            if str(itemW.text(10)).startswith("sequence") or str(itemW.text(10)).startswith("assetType")  :
                for shotWItem in itemW.getShotWidgetList() :
                    if not str(shotWItem.text(10) ) in shotItemList :
                        shotItemList.append( str(shotWItem.text(10) ) )

        return shotItemList
    ##
    ## @decorateur_try_except
    def setNoteList(self, obj) : # by shot

        # obj[0][0] : shot/Asset treeWidget name... ( item.text(10) ) 
        # obj[0][1] : shot/Asset code ...   ( the shotgun real one ) 
        # obj[0][2] : shot/Asset Id   ...   ( the shotgun real one )
        # obj[0][3] : shot/Asset Type ...   ( the shotgun real one )

        # obj[1][] : List of notes 

        # obj[2][] : a True boulean when notes has been : re-quiered / quiered as a spawned note for creation   
        if not self.myTree2.findItems( "EMPTYNOTE" , QtCore.Qt.MatchExactly, 10 ) :
            emptyWidget(self.myTree2 )

        if not obj[0][0] in self.getShotIds() :
            # if the shot_name relative to the incoming note(s) isnt anymore in the current shot selection ,
            return


        # if there's no task Widget holder, create one... 
        # I (re)name it dontCarre, because i had created one per task before
        taskWidgetItem = None
        taskWidgetItemList = self.myTree2.findItems( "task_%s"%"dontCarre" , QtCore.Qt.MatchExactly, 10 )
        if not taskWidgetItemList :
            taskWidgetItem = taskWidget(self.myTree2, {"name": "dontCarre"}, self.taskFilterWidget )
        else :
            taskWidgetItem = taskWidgetItemList[0]

        existing_id_NoteList = taskWidgetItem.find_all_notesId()


        for noteDict in obj[1] : # boucler chaques notes
            if noteDict["id"] in existing_id_NoteList :
                if obj[2] :
                    noteItemWidgetList = self.myTree2.findItems("note_%i"%noteDict["id"], QtCore.Qt.MatchRecursive, 10 )
                    for noteItemWidget in noteItemWidgetList :
                        noteItemWidget.parent().removeChild(noteItemWidget)
                else :
                    continue
            taskList = self.getNoteTaskNameList(noteDict) 
            # it can have multi task link to a note in shotgun
            for taskName in taskList : 

                for taskWidgetItem in self.myTree2.findItems( "task_%s"% "dontCarre", QtCore.Qt.MatchExactly, 10 )  : 
     
                    
                    noteDict["shotCode"] = obj[0][1]
                    noteDict["shotId"] = obj[0][2]
                    noteDict["shotType"] = obj[0][3]


                    noteWidget( taskWidgetItem, noteDict, self.taskFilterWidget, self.statusFilterWidget, self.typeFilterWidget, self.userNameFilterWidget, self.contentFilterWidget,  self.entityAssignedFilterWidget, self.shotAssetFilterWidget )
                    taskValuesList = self.taskFilterWidget.retrieveValueFromName( taskName )

                    self.queue.put( [ 2 , u"queryNoteVersion"  , [ noteDict["shotId"] ,taskValuesList  ,noteDict["id"], noteDict["shotType"] ] , None ] )
                    self.queue.put( [ 2 , u"queryTaskAssigned"  , [{'id' : noteDict["shotId"],'type' : noteDict["shotType"]  }, taskValuesList,  noteDict["id"]]   , None ] )


        self.updateTree2_withFilter()


    ## @decorateur_try_except
    def fillSeqShotTree(self, data ):
        typeEntity = "shot"
        shotDictList = data

        root = self.myTree
        seqList=[]
        for shot_sgData in   shotDictList :

            if not shot_sgData["sg_sequence"] :
                nullSequenceList = self.findInTree( "sequence_0",  None)
                seqItem = None

                if not nullSequenceList :
                    seqItem = sequenceWidget(root, {"name": u"No Sequence", "id": 0,   "type" : "Sequence" } )
                    shotItem = shotAssetWidget(seqItem, shot_sgData, typeEntity)
                else :
                    shotItem = shotAssetWidget(nullSequenceList[0], shot_sgData, typeEntity)

            elif not shot_sgData["sg_sequence"] in seqList :
                seqItem = sequenceWidget(root, shot_sgData["sg_sequence"])
                shotItem = shotAssetWidget(seqItem, shot_sgData, typeEntity)
                seqList.append( shot_sgData["sg_sequence"])

            else :
                for seqItem in self.findInTree( "sequence_%i"%shot_sgData["sg_sequence"]["id"],  None) :
                    shotItem = shotAssetWidget(seqItem, shot_sgData, typeEntity)

            if shot_sgData["id"] == self.InitOnShotName["id"] :

                self.sg.getAvailableTasks( [shot_sgData, shotItem] , None  )
                shotItem.setSelected(True)
                
            else :
                self.queue.put( [ 30 , u"getAvailableTasks"  , [shot_sgData, shotItem] , self.updateTree1_withFilter  ] )
                
            self.updateTree1_withFilter()


        

        self.queue.put( [ 150 , u"downloadThumbnail"  , shotDictList , self.findInTree ] )


    ## @decorateur_try_except
    def fillAssetTree(self, data ):
        typeEntity = "asset"
        shotDictList = data


        root = self.myTree

        seqList=[]

        for shot_sgData in   shotDictList :
            if not shot_sgData["sg_asset_type"] :
                nullSequenceList = self.findInTree( "assetType_0",  None)
                seqItem = None

                if not nullSequenceList :
                    seqItem = assetWidget(root, {"name" : "No Asset Type",  "type" : "Asset" } )
                    shotItem = shotAssetWidget(seqItem, shot_sgData, typeEntity)
                else :
                    shotItem = shotAssetWidget(nullSequenceList[0], shot_sgData, typeEntity)

            elif not shot_sgData["sg_asset_type"] in seqList :
                seqItem = assetWidget(root, {"name" : shot_sgData["sg_asset_type"], "type" : "Asset" } )
                shotItem = shotAssetWidget(seqItem, shot_sgData, typeEntity)
                seqList.append( shot_sgData["sg_asset_type"])

            else :
                for seqItem in self.findInTree( "assetType_%s"%shot_sgData["sg_asset_type"],  None) :
                    shotItem = shotAssetWidget(seqItem, shot_sgData, typeEntity)

            if shot_sgData["id"] == self.InitOnShotName["id"] :
                shotItem.setSelected(True)
                self.queue.join()
            else :
                self.queue.put( [ 30 , u"getAvailableTasks"  , [shot_sgData, shotItem] , self.updateTree1_withFilter ] )

            self.updateTree1_withFilter()

        self.queue.put( [ 150 , u"downloadThumbnail"  , shotDictList , self.findInTree ] )

    ####
    ## @decorateur_try_except
    def clearTree(self, obj) :
        for note in obj[0].findItems("note_", QtCore.Qt.MatchStartsWith  | QtCore.Qt.MatchRecursive ,10) :
            note.setHidden(True) 


        obj[0].clear()
        obj[0].lastItem_edited = None

    #####
    ## @decorateur_try_except
    def queryNoteContent(self, obj) :

        sg_noteContentList = obj[0]
        selectedNoteList = self.myTree2.selectedItems()
        

        if not obj[1] :
            if len(sg_noteContentList) == 0  :
                return


            if len(selectedNoteList) != len(sg_noteContentList)  :
                return

            matchSelection = 0
            for selectedNote in selectedNoteList :
                for sg_noteContent in sg_noteContentList :
                    if not selectedNote.sgData == None :
                        if selectedNote.sgData['id'] == sg_noteContent['id'] :
                            matchSelection +=1

            if matchSelection != len(selectedNoteList)  :
                return



        QtGui.QApplication.processEvents()
        if len(sg_noteContentList) == 1 :
            my_noteLayoutWidget = noteLayoutWidget( sg_noteContentList, [ None , self.taskFilterWidget, None, None, None ] )
            self.clearRightLayout()
            self.rightLayout.addWidget(  my_noteLayoutWidget  )
            my_noteLayoutWidget.SIGNAL_createReply.connect( self.replyNoteSlot)
            if my_noteLayoutWidget.receiveFocusWidget :
                if not self.shotAssetFilterWidget.widget.hasFocus() :
                    my_noteLayoutWidget.receiveFocusWidget.setFocus()

        else :
            my_noteLayoutWidget = noteLayoutWidget( sg_noteContentList )
            self.clearRightLayout()
            self.rightLayout.addWidget(  my_noteLayoutWidget  ) 
            my_noteLayoutWidget.SIGNAL_createMultiReply.connect( self.multiReplyNoteSlot)

        QtGui.QApplication.processEvents()
             
    ######
    ## @decorateur_try_except
    def noteTreeUpdated(self, obj) :
        
        int_noteId = obj[0]["id"]

        selectedItemList = self.myTree2.selectedItems()
        
        noteData = []
        for itemW in selectedItemList :
            if itemW.text(10) == "note_%i"%int_noteId :
                noteData.append( itemW.sgData )

        if obj[0].has_key("new_sg_status_list") :
            for treeNoteItem in self.myTree2.findItems("note_%i"%int_noteId , QtCore.Qt.MatchRecursive,10 ) :
                treeNoteItem.updateData({ "sg_status_list" : obj[0]["new_sg_status_list"] })

        noteByIdList = self.myTree2.findItems("note_%i"%int_noteId, QtCore.Qt.MatchRecursive,10) 
        if noteByIdList == 1 :
            self.queue.put( [ -1 , u"queryNoteVersion"  , [ 0 , [],  int_noteId,noteByIdList[0].sgData["shotType"]  ] , None ] )



        if obj[1]:   
            self.queue.put( [ -1 , u"queryNoteContent"  , noteData , None ] )


    ## @decorateur_try_except   
    def queryNoteVersion(self, obj) :
        for noteWidget in self.myTree2.findItems("note_%i"%obj[0], QtCore.Qt.MatchRecursive,10) :
            
            noteWidget.setText(5, obj[1])
            noteWidget.setText(7, str(obj[2]) )
            noteWidget.setText(11, str(obj[3]))
            noteWidget.set_my_bacgroundColor()

    ## @decorateur_try_except
    def queryNoteTaskAssigned(self, obj) :
        for noteWidget in self.myTree2.findItems("note_%i"%obj[0], QtCore.Qt.MatchRecursive,10) :
            noteWidget.setText(8, str("\n".join(obj[1]) ) )
            self.updateTree2_withFilter()


def main():        

    QtGui.QApplication.setStyle("plastique")

    palette_file = getStyle("dark_palette.qpalette")
    fh = QtCore.QFile(palette_file)
    fh.open(QtCore.QIODevice.ReadOnly);
    file_in = QtCore.QDataStream(fh)

    # deserialize the palette
    # (store it for GC purposes)
    _dark_palette = QtGui.QPalette()
    file_in.__rshift__(_dark_palette)
    fh.close()

    # set the std selection bg color to be 'shotgun blue'
    _dark_palette.setBrush(QtGui.QPalette.Highlight, QtGui.QBrush(QtGui.QColor("#30A7E3")))
    _dark_palette.setBrush(QtGui.QPalette.HighlightedText, QtGui.QBrush(QtGui.QColor("#FFFFFF")))

    # and associate it with the qapplication
    QtGui.QApplication.setPalette(_dark_palette)


    app = QtGui.QApplication(sys.argv)
    
    
    
    ex = Example()
    

    sys.exit(app.exec_())



if __name__ == '__main__':
    import os
    from PyQt4 import QtGui, QtCore

    main()








