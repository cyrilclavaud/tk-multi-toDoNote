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

class AddButtonDelegate(QtGui.QItemDelegate):
    """
    Displays an "Add..." button on the first column of the table if the
    corresponding row has not been assigned data yet. This is needed when a
    prediction map for a raw data lane needs to be specified for example.
    """
    def __init__(self, parent):
        super(AddButtonDelegate, self).__init__(parent)
  
    def paint(self, painter, option, index):
        # This method will be called every time a particular cell is in
        # view and that view is changed in some way. We ask the delegates
        # parent (in this case a table view) if the index in question (the
        # table cell) corresponds to an empty row (indicated by '<empty>'
        # in the data field), and create a button if there isn't one
        # already associated with the cell.
        parent_view = self.parent()

        """
        button = parent_view.indexWidget(index)
        if index.row() < parent_view.model().rowCount()-1 and parent_view.model().isEmptyRow(index.row()):
            if button is None:
                button = AddFileButton(parent_view)
                button.addFilesRequested.connect(
                        partial(parent_view.handleCellAddFilesEvent, index.row()))
                button.addStackRequested.connect(
                        partial(parent_view.handleCellAddStackEvent, index.row()))
                button.addRemoteVolumeRequested.connect(
                        partial(parent_view.handleCellAddRemoteVolumeEvent, index.row()))
                parent_view.setIndexWidget(index, button)
        elif index.data() != '':
            if button is not None:
                # If this row has data, we must delete the button.
                # Otherwise, it can steal input events (e.g. mouse clicks) from the cell, even if it is hidden!
                # However, we can't remove it yet, because we are currently running in the context of a signal handler for the button itself!
                # Instead, use a QTimer to delete the button as soon as the eventloop is finished with the current event.
                QTimer.singleShot(750, lambda: parent_view.setIndexWidget(index, None) )
            """
        super(AddButtonDelegate, self).paint(painter, option, index)


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

    def __init__(self, task_entriesDictList , parent = None ):
        QtGui.QTreeWidget.__init__(self, parent)
        #self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.task_entriesDictList = task_entriesDictList

        self.pixmap = QtGui.QPixmap( getRessources("note_folded.png") )
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.onCustomContextMenuRequested)

        self.itemDoubleClicked.connect(self.editItem)
        self.itemClicked.connect( self.close_editItem )
        self.setStyleSheet("myQTree{ outline: 0;}")
        #self.grabKeyboard()
        self.lastItem_edited = None

        self.setItemDelegate(NoRectDelegate())
        #self.setItemDelegateForColumn( 1, AddButtonDelegate(self) )

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

    def onCustomContextMenuRequested( self,  pos) :
        item = self.itemAt(pos);
        if ( item ) : 
            self.showContextMenu(item, self.indexAt(pos).column() ,self.viewport().mapToGlobal(pos))
    
    @decorateur_try_except
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
                
                
                menu.addAction(QtGui.QIcon(getRessources("sequence.png")), "Select Shot(s)",  lambda : self.SIGNAL_selectShot.emit( self.selectedItems() )  )
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
       

    def selectNote_from_id(self, idNote, taskName) :

        notes = self.findItems("note_%i"%idNote, QtCore.Qt.MatchRecursive,10) 

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


    def selectShot_slot(self):
        self.SIGNAL_selectShot.emit( self.selectedItems() )

    @decorateur_try_except
    def setNoteStatus_slot(self, status):
        return
        #print status

    @decorateur_try_except
    def drawTree(self, painter, region ) :
        return

    @decorateur_try_except
    def editItem(self, item,  column) :
        
        if column == 0 and str(item.text(10)).startswith("note_") :
            item.setEditableMode(True)
            self.lastItem_edited = item

    @decorateur_try_except
    def close_editItem(self, item,  column) :
        
        if self.lastItem_edited :
            if not item.sgData.has_key('id') :
                self.lastItem_edited.setEditableMode(False)
                self.lastItem_edited = None
            elif not self.lastItem_edited.sgData["id"] == item.sgData['id'] :
                self.lastItem_edited.setEditableMode(False)
                self.lastItem_edited = None


    def drawRow(self, painter,  option,  index) :

        if self.model().hasChildren(index):

            if self.isExpanded(index) : 
                option.displayAlignment    = QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter 
                painter.fillRect( option.rect, QtGui.QColor(115,115,115, 168) )

            else :
                """
                val =  index.sibling(index.row(), 10).data()
                if val :
                    if val.toString() :
                        print str(val.toString())
                        if str(val.toString()).startswith("task_" ) :
                            print "tp"
                            option.displayAlignment = QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter 
                """

                option.displayAlignment = QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter 


                gradient = QtGui.QLinearGradient(option.rect.topLeft(),option.rect.bottomLeft())
                gradient.setColorAt(0,   QtGui.QColor(115,115,115, 168) )
                gradient.setColorAt(0.5, QtGui.QColor(165,165,165, 168) )
                gradient.setColorAt(1,   QtGui.QColor(115,115,115, 168) )
                

                painter.fillRect( option.rect, gradient )

                pen = QtGui.QPen(QtGui.QColor("#000000"))
                painter.setPen(pen)
                painter.drawLine(option.rect.bottomLeft(),option.rect.bottomRight() )


            QtGui.QTreeWidget.drawRow(self, painter, option, index )
            pen = QtGui.QPen(QtGui.QColor(0,0,0,30))
            painter.setPen(pen)
            painter.drawLine(option.rect.bottomLeft(),option.rect.bottomRight() )

        else :
            option.displayAlignment = QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter 
            #option.decorationSize = QtCore.QSize(16,16)

            if index.row() % 2 :
                painter.fillRect( option.rect, QtGui.QColor(0,0,0, 0) )
            else :
                painter.fillRect( option.rect, QtGui.QColor(0,0,0, 80) )




            QtGui.QTreeWidget.drawRow(self, painter, option, index )
            pen = QtGui.QPen(QtGui.QColor(0,0,0,30))
            painter.setPen(pen)
            painter.drawLine(option.rect.bottomLeft(),option.rect.bottomRight() )

       
    def drawBranches(self, painter, rect, index):
        return 




class joinQueue( Queue.PriorityQueue ) :
    def __init__(self):
        Queue.PriorityQueue.__init__(self)
        self.count = 0


    def put(self, args):
        Queue.PriorityQueue.put(self, args)
        self.count += 1
        self.join() 

    def task_done(self):
        Queue.PriorityQueue.task_done(self)
        self.count -= 1
        return self.count

    def getCount(self):
        return self.count

class myQueue( Queue.PriorityQueue ) :
    def __init__(self):
        Queue.PriorityQueue.__init__(self)
        self.count = 0


    def put(self,args):
        
        Queue.PriorityQueue.put(self, args)
        
        self.count += 1

    def getCount(self):
        return self.count

    def task_done(self):
        Queue.PriorityQueue.task_done(self)
        self.count -= 1
        return self.count



class Example(QtGui.QWidget):
    appLauncherDict = { 
                        "layout" : { "tk-multi-launchmaya" :  { "template" : "maya_shot_work" ,  "icon" : "MayaApp.png" } },
                        "Anim"  :  { "tk-multi-launchmaya" :  { "template" : "maya_shot_work" ,  "icon" : "MayaApp.png" } } ,
                        "Compo" :  { "tk-multi-launchnuke"  : { "template" : "nuke_shot_work" ,  "icon" : "NukeApp.png" },
                                     "tk-multi-launchnukeX" : { "template" : "nuke_shot_work" ,  "icon" : "NukeXApp.png" }
                                   },
                        "lighting" : { "tk-multi-launchmaya" :  { "template" : "maya_shot_work" ,  "icon" : "MayaApp.png" } }
                      }

    def __init__(self ):



        perr("",True)
        plog("",True)
        pprint("",True)


        QtGui.QWidget.__init__(self)
        #self.setWindowFlags(QtCore.Qt.WindowMaximizeButtonHint)

        
        self.queue = None

        if "USE THREADING" :
            self.queue = myQueue() #Queue.PriorityQueue()
        else :
            pprint("don't use threading")
            self.queue = joinQueue()
        
        projectId = 191
        userDict = None

        self.InitOnShotName = {"id":0}
        self.InitFilterOnTaskName = None
        self.engineName = None

        self._app = None
        try :
            self._app = sgtk.platform.current_bundle()



            projectDict = self._app.context.project
            pprint("Project :" + str( projectDict ) + "\n")
            projectId = projectDict["id"]
            
            userDict = self._app.context.user
            pprint("User :" + str( userDict ) + "\n")


            if self._app.context.task :
                self.InitFilterOnTaskName = self._app.context.task["name"]
            elif self._app.context.step :
                self.InitFilterOnTaskName = self._app.context.step["name"]

            entityDict = self._app.context.entity
            pprint("Entity : " +  str( entityDict ) + "\n")
            
            if entityDict :
                if entityDict["type"] == "Shot" :

                    self.InitOnShotName= entityDict
                    pprint("init not manager on shot "+ str(self.InitOnShotName) + "\n")

            self.eng = sgtk.platform.current_engine()

            if self.eng :
                self.engineName = self.eng.instance_name



        except :
            pprint(str( "cant get context entity") + "\n")

       

        ############# TASK


        task_entriesDictList = [ {"text" : "All", "icon" : None, "values": []  },
                            {"text" : "Compo", "icon" : "task_compo.png", "values": ["Compositing", "Comp", "Compo"] },
                            {"text" : "Anim", "icon" : "task_animation.png", "values": ["Animation","animation","anim", "Anim"]  },
                            {"text" : "lighting", "icon" : "task_lit.png" , "values": ["Lighting", "lighting"]  },
                            {"text" : "Fur", "icon" : "task_fur.png" , "values": ["fur","Fur"] },
                            {"text" : "modeling", "icon" : "task_modelisation.png" , "values": ["Modeling", "modeling"] },
                            {"text" : "rigging", "icon" : "task_rig.png" , "values": ["Rig", "rig", "rigging"] },
                            {"text" : "layout", "icon" : "task_layout.png" , "values": ["Layout", "layout"] },
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


        if self.InitFilterOnTaskName  :
            task_entriesDictList = self.setCheckedFromValue(task_entriesDictList, [self.InitFilterOnTaskName] + ["NoTask"] )
        elif task_mask :
            task_entriesDictList = self.setCheckedFromCheckedList(task_entriesDictList, task_mask )   
        else :
            task_entriesDictList = self.setCheckedFromValue(task_entriesDictList, [None] )

        self.taskFilterWidget =  comboFilterWidget2( {"name":"Task" , "icon": "task.png"}, task_entriesDictList, multiCheckable = True )


        if type_mask :
            type_entriesDictList = self.setCheckedFromCheckedList(type_entriesDictList, type_mask )   
        else :
            type_entriesDictList = self.setCheckedFromValue(type_entriesDictList, ["To Do", "NoType"] )

        self.typeFilterWidget = comboFilterWidget2( {"name":"Type" , "icon": "type.png"}, type_entriesDictList, multiCheckable = True ) 


        if status_mask :
            status_entriesDictList = self.setCheckedFromCheckedList(status_entriesDictList, status_mask )   
        else :
            status_entriesDictList = self.setCheckedFromValue(status_entriesDictList, ["Open", "ip"] )
        
        self.statusFilterWidget = comboFilterWidget2( {"name":"Status" , "icon": "status.png"}, status_entriesDictList, multiCheckable = True  )



        for i in range(10) :
            sg = sg_query( self._app  )            

            sg.setProjectId(projectId)
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

            sg.SIGNAL_updateLaunchAppWidget.connect(self.updateLauncherWidget)

            sg.SIGNAL_pbar.connect(self.updateProgressBar)

            sg.start()

            pprint("thread init " +str(sg.th_id ) +"\n" )

        self.initUI()
     

        self.queue.put( [ 3,u"fillSeqShotTree"  , None , None ] )
        #

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





    def initUI(self):
        self.mainLayout = QtGui.QVBoxLayout() 
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.mainLayout.setSpacing(0)
        self.setLayout(self.mainLayout)
        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)


        self.filteringLayout = QtGui.QHBoxLayout()
        self.filteringLayout.setContentsMargins(0,0,0,0)
        self.refreshUI_Btn =  toggleBtn("PAF")



        


        self.userNameFilterWidget = lineEditFilterWidget( {"name":"User" , "icon": "user.png"} )
        self.contentFilterWidget  = lineEditFilterWidget( {"name":"Contains" , "icon": "text.png"} )
        self.entityAssignedFilterWidget  = lineEditFilterWidget( {"name":"Shot Assigned To" , "icon": "thunder-32.png"} )

        #### grouping options
        self.groupByTypeBox = QtGui.QCheckBox("Group by Type")
        self.groupByTypeBox.setCheckState(QtCore.Qt.Unchecked)
        self.groupByTypeBox.setTristate(False)

        self.spacerItem =  QtGui.QSpacerItem(1,1)


        self.filteringLayout.setSpacing(10)
        self.filteringLayout.addWidget( self.refreshUI_Btn)
        self.filteringLayout.addSpacerItem(self.spacerItem)
        self.filteringLayout.addWidget( self.taskFilterWidget )
        self.filteringLayout.addWidget( self.typeFilterWidget )
        self.filteringLayout.addWidget( self.statusFilterWidget )
        self.filteringLayout.addWidget( self.userNameFilterWidget  )
        self.filteringLayout.addWidget( self.contentFilterWidget )
        self.filteringLayout.addWidget( self.entityAssignedFilterWidget )
        self.filteringLayout.addSpacing(10)

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
        self.myTree.setHeaderLabels(["Shots","Note count"])
        self.myTree.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.myTree.setFocusPolicy(QtCore.Qt.NoFocus)


        self.myTree2 = myQTree( self.taskFilterWidget.entriesDictList )# QtGui.QTreeWidget() 
        self.myTree2.setIconSize(QtCore.QSize(128,128))
        self.myTree2.setColumnCount(11)
        self.myTree2.setHeaderLabels(["Note Content","Tasks", "Type","Created_at", "User", "v---", "Shot", "Replies", "Shot Assignement", "Created_at"])
        self.myTree2.setSortingEnabled(True)

        self.myTree2.setAlternatingRowColors(0);
        self.myTree2.setIndentation(0)
        self.myTree2.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        p = QtGui.QPalette()
        p.setColor( QtGui.QPalette.AlternateBase, QtGui.QColor(0, 0, 0, 18) );
        self.myTree2.setPalette(p)

        
        header = self.myTree.header()

        #header.setDefaultAlignment(QtCore.Qt.AlignHCenter)

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


        self.rightLayout.addWidget( noteLayoutWidget( None,  [ self.getShotItemList() , self.taskFilterWidget, self.typeFilterWidget, self.statusFilterWidget,[] ], self.queue ) )
        

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

        style = "QSplitter::handle:vertical#verti {background: qlineargradient(x1:0, y1:1, x2:0, y2:1, stop:0 rgba(120, 120, 150, 40% ), stop:1 rgba(120, 120, 150, 40% ) );border: 1px solid rgba(120, 120, 150, 40% ); width : 1px ; height : 1px ;margin-right: 2px;margin-left: 2px;border-radius: 4px;}\n"
        style += "QSplitter::handle:horizontal#hori {background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(120, 120, 150, 40% ), stop:1 rgba(120, 120, 150, 40% ));border: 1px solid rgba(120, 120, 150, 40% ) ;width: 13px;margin-top: 2px;margin-bottom: 2px;border-radius: 4px;}"
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

        self.splitter.setSizes([ col1,col2, splitSize-(col1+col2)])



        layout.addWidget(self.splitter)
        horizontalSplitter.addWidget(self.splitter)
        horizontalSplitter.setStretchFactor( 0, 0 )
        horizontalSplitter.setStretchFactor( 1, 1 )

        self.splitter.setStretchFactor( 0, 0 )
        self.splitter.setStretchFactor( 1, 1 )
        self.splitter.setStretchFactor( 2, 0 )



        self.updateLauncherWidget( [{"clear":True}, 0 , "", "" ]) 
         #w = LaunchApp_widget( obj[0], obj[1], obj[2], obj[3] ) 


        self.serialize_comboFilterWidget(False)



        self.splitter.splitterMoved.connect(self.resizeFilterLayout  )

        self.myTree.itemSelectionChanged.connect(self.shotTreeClicked )
        self.refreshUI_Btn.clicked.connect(  lambda : self.shotTreeClicked( True )  ) 

        self.taskFilterWidget.widget.currentIndexChanged.connect( self.updateTree2_withFilter )
        #self.typeFilterWidget.widget.currentIndexChanged.connect( self.updateTree2_withFilter )

        self.typeFilterWidget.widget.currentIndexChanged.connect( lambda : self.shotTreeClicked( True ) )
        self.statusFilterWidget.widget.currentIndexChanged.connect( self.updateTree2_withFilter )
        self.userNameFilterWidget.widget.textChanged.connect(self.updateTree2_withFilter)
        self.contentFilterWidget.widget.textChanged.connect(self.updateTree2_withFilter)
        self.entityAssignedFilterWidget.widget.textChanged.connect(self.updateTree2_withFilter)


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


        self.myTree2.itemSelectionChanged.connect(self.noteTreeClicked )
        self.myTree2.header().sectionMoved.connect(self.myTree2.columHasMoved)
        self.myTree2.header().sectionResized.connect(self.myTree2.columHasMoved)

        self.groupByTypeBox.stateChanged.connect(self.refreh_myTree2)


        self.taskFilterWidget.widget.currentIndexChanged.connect(lambda : self.serialize_comboFilterWidget( True ) )
        self.typeFilterWidget.widget.currentIndexChanged.connect(lambda : self.serialize_comboFilterWidget( True ) )
        self.statusFilterWidget.widget.currentIndexChanged.connect(lambda : self.serialize_comboFilterWidget( True ) )


        self.spacerItem.changeSize(col1-14, 1)
        self.filteringLayout.invalidate()

        #self.myTree2.columHasMoved(0,0,0, False)


        header.setResizeMode(0, QtGui.QHeaderView.Interactive)

        self.show()



    def resizeFilterLayout(self, pos, idx):

        if idx == 1 :
             
            self.spacerItem.changeSize(pos-14, 1)
            self.filteringLayout.invalidate()


 
    def findInTree(self, sg_id, parent = None):
        root = self.myTree
        if parent :
            root = parent
        
        #return root.findItems( sg_id, QtCore.Qt.MatchExactly, 10 ) 
        return root.findItems( sg_id, QtCore.Qt.MatchRecursive,10 )


    @decorateur_try_except
    def getNoteTaskNameList(self, noteDict ) :
        taskList = []
        if  noteDict["tasks"] :
            return [ self.taskFilterWidget.retrieveNameFromValue(noteDict["tasks"][0]["name"] ) ]

        if not taskList :
            return ["NoTask"]

        return  taskList


    @decorateur_try_except
    def clearRightLayout(self) :
        for i in reversed(range(self.rightLayout.count())):   
            wid =  self.rightLayout.itemAt(i).widget()
            wid.setParent(None)






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
  
    #OBSO
    def fill_TaskAssigned(self, idx) :
        soloCheckedTask = self.taskFilterWidget.getSoloChecked() 
        if soloCheckedTask :
            for shotAssetItem in self.myTree.findItems("shotAsset_", QtCore.Qt.MatchStartsWith  | QtCore.Qt.MatchRecursive,  10) : 
                
                self.queue.put( [ 0 , u"queryTaskAssigned" ,  [shotAssetItem.sgData, soloCheckedTask] , None ] )


    def breakNoteLink(self, itemList ) :
        self.queue.put( [ 0 , u"breakSpawnLink" ,  [ itemList[0].sgData["spawnLinkId"],  itemList[0].sgData["shotId"],  itemList[0].sgData["shotCode"] ]  , None ] )

    def querySingleNoteContent(self, noteId_taskName ) :
        noteId = noteId_taskName[0]
        taskName = noteId_taskName[1]

        taskValues = self.taskFilterWidget.retrieveValueFromName(taskName)

        self.queue.put( [ 0 , u"queryNoteContent"  , [{"id":noteId,"taskValues": taskValues}] , None ] )
    @decorateur_try_except
    def updateNoteContent(self, obj ):
        #[0] note content
        #[1] note id
        
        self.queue.put( [ 0 , u"editNoteContent" ,  obj , None ] )
        #
    
    @decorateur_try_except
    def refreh_myTree2(self, state) :

        header = self.myTree2.header()
        if state :
            header.hideSection(header.logicalIndex(header.visualIndex(2)))
        else :
            header.showSection(header.logicalIndex(header.visualIndex(2)))
        self.shotTreeClicked(forceRedraw = True)





    @decorateur_try_except
    def setNoteStatus(self, itemListAndStatus_list):
        for item in itemListAndStatus_list[0]:
            noteId = 0 
            if item.sgData.has_key('id') :
                noteState = {"new_sg_status_list":itemListAndStatus_list[1], "id" : item.sgData['id']}
                self.queue.put( [ 0 , u"setNoteStatus" , [noteState] , None ] )

    
    @decorateur_try_except
    def setNoteType(self, itemListAndType_list):
        for item in itemListAndType_list[0]:
            noteId = 0 
            if item.sgData.has_key('id') :
                noteType = {"new_sg_note_type":itemListAndType_list[1], "id" : item.sgData['id']}
                self.queue.put( [ 0 , u"setNoteType" , [noteType] , None ] )
    
    @decorateur_try_except
    def linkToLastVersion(self, selectedNoteList) :
        for item in selectedNoteList[0]:
            noteId = 0
            if item.sgData.has_key('id') :

                if item.sgData["tasks"] :
                    taskValuesList = self.taskFilterWidget.retrieveValueFromName(item.sgData["tasks"][0]["name"])
                    if taskValuesList :
                        self.queue.put( [ 0 , u"linkToLastVersion" , [  item.sgData['shotId'],  taskValuesList , item.sgData['id'] ] , None ] )
                if selectedNoteList[1] :
                    noteState = {"new_sg_status_list":selectedNoteList[1], "id" : item.sgData['id']}
                    self.queue.put( [ 0 , u"setNoteStatus" , [noteState] , None ] )


    def setNoteLink(self, itemListAndTaskValues_list) :
        for item in itemListAndTaskValues_list[0] :
            if item.sgData.has_key('id') :

                self.queue.put( [ 0 , u"setNoteLink" , [item.sgData, itemListAndTaskValues_list[1], itemListAndTaskValues_list[2] ] , None ] )


    @decorateur_try_except
    def setNoteTask(self, itemListAndTaskValues_list) :

        for item in itemListAndTaskValues_list[0] :
            if item.sgData.has_key('id') :


                self.queue.put( [ 0 , u"setNoteTask" , [item.sgData, itemListAndTaskValues_list[1] ] , None ] )
    
    @decorateur_try_except
    def deleteNotes(self, itemList ) :
        for item in itemList[0]:
            if not item.sgData.has_key("spawnLinkId") :
                if item.sgData.has_key('id') :
                    #noteType = {"new_sg_note_type":itemListAndType_list[1], "id" : item.sgData['id']}
                    self.queue.put( [ 0 , u"deleteNote" , [item.sgData['id']] , None ] )

    @decorateur_try_except
    def multiReplyNoteSlot(self, obj):
        self.queue.put( [ 0 , u"multyReplyNote" , obj , None ] )
        #self.queue.join()

    @decorateur_try_except
    def replyNoteSlot(self, obj) :
        self.queue.put( [ 0 , u"replyNote" , obj , None ] )
        #

    @decorateur_try_except
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


        if noteData :
            if len(noteData) == 1 :

                taskValues = [] 
                taskName = ""
                if noteData[0]["tasks"] :
                    taskValues = self.taskFilterWidget.retrieveValueFromName( noteData[0]["tasks"][0]["name"] )
                    taskName =   self.taskFilterWidget.retrieveNameFromValue( noteData[0]["tasks"][0]["name"] )
    
                self.queue.put([-5, u"getExecutable",   [noteData[0]["shotId"], taskValues, taskName , noteData[0]["shotCode"] ] , None ] )

            self.queue.put( [ 0 , u"queryNoteContent"  , noteData , None ] )

        elif selectedItemList :
            self.drawNote(taskList)

    @decorateur_try_except
    def drawNote(self, taskList = []):


        my_noteLayoutWidget = noteLayoutWidget( None,  [ self.getShotItemList(), self.taskFilterWidget, self.typeFilterWidget, self.statusFilterWidget, taskList ], self.queue )



        my_noteLayoutWidget.SIGNAL_send_NoteContent.connect( self.createNewNote )

        my_noteLayoutWidget.updateTaskFilterWidget([])


        my_noteLayoutWidget.SIGNAL_createReply.connect( self.replyNoteSlot )
        my_noteLayoutWidget.SIGNAL_createMultiReply.connect( self.multiReplyNoteSlot )

        self.clearRightLayout()
        self.rightLayout.addWidget(  my_noteLayoutWidget  )

    @decorateur_try_except
    def createNewNote(self, obj) :
        
        self.queue.put( [ 0 , u"createNote"  , [ obj ] , None ] )
        #


    @decorateur_try_except
    def shotTreeClicked(self, forceRedraw = False) :
        
        if not self.myTree.selectedItems() :
            self.updateLauncherWidget( [{"clear":True}, 0 , "", "" ]) 


        if not forceRedraw :
            redrawTreeNote = False
            newItems = []
            temp_shotTreeSelection_id_List = []
            for itemW in self.myTree.selectedItems() :
                temp_shotTreeSelection_id_List.append( itemW.text(10) )
                if itemW.text(10) not in self.shotTreeSelection_id_List:
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
            self.queue.put( [-10000 ,u"clearTree" , self.myTree2, None]  )

        selectedItemList = newItems 

        shotItemList = []
        for itemW in selectedItemList :
            if str(itemW.text(10)).startswith("shotAsset") :

                if not itemW.sgData in shotItemList :
                    shotItemList.append(itemW.sgData )

            if str(itemW.text(10)).startswith("sequence") or str(itemW.text(10)).startswith("assetType")  :


                for shotWItem in itemW.getShotWidgetList() :
                    if not shotWItem.sgData in shotItemList :
                        shotItemList.append(shotWItem.sgData )
        
        for sgData in shotItemList :
            self.queue.put( [1, u"queryNotes"  , sgData, None ] )
            #

        self.drawNote() 


    @decorateur_try_except
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

        return shotItemList

    @decorateur_try_except   
    def updateTree2_withFilter(self, idx = None):

        self.iterateTree2()
        self.iterateTree2_HideEmptyBranch()


    def iterateTree2(self, root = None ) :
        if not root : 
            root = self.myTree2.invisibleRootItem()
        
        child_count = root.childCount()
        for i in range(child_count):
            item = root.child(i)
            if hasattr(item, "do_hidding") :
                if not item.do_hidding() :
                    self.iterateTree2(item)

    @decorateur_try_except
    def iterateTree2_HideEmptyBranch(self, root = None ) :

        for item in self.myTree2.findItems("type_", QtCore.Qt.MatchStartsWith | QtCore.Qt.MatchRecursive, 10) :
            numHiddenItem = 0
            
            child_count = item.childCount()
            for i in range(child_count):
                numHiddenItem += int( item.child(i).isHidden() )

            #print numHiddenItem == child_count, ( numHiddenItem , child_count )
            if numHiddenItem == child_count :
                item.setHidden(True)

        for item in self.myTree2.findItems("task_", QtCore.Qt.MatchStartsWith, 10) :
            numHiddenItem = 0
            
            child_count = item.childCount()
            for i in range(child_count):
                numHiddenItem += int( item.child(i).isHidden() )

            #print numHiddenItem == child_count, ( numHiddenItem , child_count )
            if numHiddenItem == child_count :
                item.setHidden(True)

    @decorateur_try_except
    def selectShotMyTree(self, shotItemList) :
        seqList = []

        self.myTree.clearSelection()
        for item in shotItemList :
            #print item.sgData["shotCode"]
            for myTreeItem in  self.myTree.findItems( item.sgData["shotCode"] , QtCore.Qt.MatchRecursive, 0 ) :
                seqItem = myTreeItem.sgData["sg_sequence"]
                if not seqItem :
                    seqItem={"name" : "No Sequence"}
                if not seqItem["name"] in seqList :
                    seqList.append(seqItem["name"])
                myTreeItem.setSelected(True)


        for i in range(self.myTree.topLevelItemCount()) :
            item = self.myTree.topLevelItem(i)
            if item.sgData["name"] in seqList:
                item.setExpanded(True)
            else :
                item.setExpanded(False)

        self.drawNote()





    ############################################
    #####
    #####       SLOTS CONNECTED TO THE THREADING CLASS
    #####
    ##### every method below will be call after a thread'complete  
    ##### they update the UI with data computed by the threading class. 
    #####
    #####
    ############################################

    @decorateur_try_except
    def updateLauncherWidget(self, obj) :
        if not self.engineName in ["tk-shotgun", "tk-desktop", "tk-shell"] :
            return 
            
        w = self.mainLayout.itemAt(2)
        if w :
            w = w.widget()
            if obj[1] == 0 :
                w.setParent(None)
                w = LaunchApp_widget( obj[0], obj[1], obj[2], obj[3], empty = True ) 
                w.setStyleSheet("LaunchApp_widget{background-color: qlineargradient( x1: 0.7, y1: 0, x2: 1, y2: 0, stop: 0 #2A2A2A, stop: 1 #425C73 )}")                    
                self.mainLayout.addWidget(w)
                return 
            
            if w.shotId == obj[1] and w.taskName == obj[2] :
                if obj[0].has_key("clear"):
                    return
                else :
                    if w.empty :
                        w.setParent(None)
                        w = LaunchApp_widget( obj[0], obj[1], obj[2], obj[3] ) 
                        w.setStyleSheet("LaunchApp_widget{background-color: qlineargradient( x1: 0.7, y1: 0, x2: 1, y2: 0, stop: 0 #2A2A2A, stop: 1 #425C73 )}")

                        self.mainLayout.addWidget(w)

                    return
            else :
                if obj[0].has_key("clear") :
                    w.setParent(None)
                    w = LaunchApp_widget( obj[0], obj[1], obj[2], obj[3], empty = True ) 
                    w.setStyleSheet("LaunchApp_widget{background-color: qlineargradient( x1: 0.7, y1: 0, x2: 1, y2: 0, stop: 0 #2A2A2A, stop: 1 #425C73 )}")
                    self.mainLayout.addWidget(w)
                else :
                    return
                    w.setParent(None)
                    w = LaunchApp_widget( obj[0], obj[1], obj[2], obj[3], empty = True ) 
                    w.setStyleSheet("LaunchApp_widget{background-color: qlineargradient( x1: 0.7, y1: 0, x2: 1, y2: 0, stop: 0 #2A2A2A, stop: 1 #425C73 )}")                    
                    self.mainLayout.addWidget(w)
        else :
            w = LaunchApp_widget( obj[0], obj[1], obj[2], obj[3], empty = True ) 
            w.setStyleSheet("LaunchApp_widget{background-color: qlineargradient( x1: 0.7, y1: 0, x2: 1, y2: 0, stop: 0 #2A2A2A, stop: 1 #425C73 )}")                    
            self.mainLayout.addWidget(w)


        if not obj[0].has_key("clear") :
            w = LaunchApp_widget( obj[0], obj[1], obj[2], obj[3] ) 
            w.setStyleSheet("LaunchApp_widget{background-color: qlineargradient( x1: 0.7, y1: 0, x2: 1, y2: 0, stop: 0 #2A2A2A, stop: 1 #425C73 )}")
            self.mainLayout.addWidget(w)

    @decorateur_try_except
    def updateProgressBar(self, value) :
        self.progressBar.setValue(value)
 
    @decorateur_try_except
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
  
    @decorateur_try_except
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


                noteWidget( taskWidgetItem, noteDict, self.taskFilterWidget, self.statusFilterWidget, self.typeFilterWidget, self.userNameFilterWidget, self.contentFilterWidget,  self.entityAssignedFilterWidget  )
                taskWidgetItem.setHidden(False)


                taskValuesList = self.taskFilterWidget.retrieveValueFromName( taskName )
                self.queue.put( [ 2 , u"queryNoteVersion"  , [ noteDict["shotId"] ,taskValuesList  ,noteDict["id"] ] , None ] )
                
                self.queue.put( [ 2 , u"queryTaskAssigned"  , [{'id' : noteDict["shotId"],'type' : 'Shot'}, taskValuesList,  noteDict["id"]]   , None ] )
                        #

    @decorateur_try_except           
    def updateDrawNote_versions(self, obj) :
        noteLayoutQItem = self.rightLayout.itemAt(0)
        noteLayoutWidget= noteLayoutQItem.widget()
        if noteLayoutWidget.data == None:
            noteLayoutWidget.fill_versionWidgetCombo(obj)
    
    #
    @decorateur_try_except
    def setTreeThumbNail(self, obj) :
        treeWidgetItemList =  self.findInTree(obj[0])

        for  treeWidgetItem in treeWidgetItemList :
            treeWidgetItem.setIcon(0, QtGui.QIcon(obj[1]))

                
    @decorateur_try_except
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
    @decorateur_try_except
    def setNoteList(self, obj) : # by shot
        # obj[0][0] : shot/Asset treeWidget name... ( item.text(10) ) 
        # obj[0][1] : shot/Asset code ... ( the shotgun real one ) 
        # obj[0][2] : shot/Asset Id ...   ( the shotgun real one )
        # obj[1][] : List of notes 

        # obj[2][] : a True boulean when notes has been : re-quiered / quiered as a spawned note for creation   

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
                    

                    noteWidget( taskWidgetItem, noteDict, self.taskFilterWidget, self.statusFilterWidget, self.typeFilterWidget, self.userNameFilterWidget, self.contentFilterWidget,  self.entityAssignedFilterWidget )
                    
                    taskValuesList = self.taskFilterWidget.retrieveValueFromName( taskName )
                    self.queue.put( [ 2 , u"queryNoteVersion"  , [ noteDict["shotId"] ,taskValuesList  ,noteDict["id"] ] , None ] )
                    self.queue.put( [ 2 , u"queryTaskAssigned"  , [{'id' : noteDict["shotId"],'type' : 'Shot'}, taskValuesList,  noteDict["id"]]   , None ] )
                        #
    ###
        self.updateTree2_withFilter()


    @decorateur_try_except
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
                    seqItem = sequenceWidget(root, {"name": u"No Sequence", "id": 0 })
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
                shotItem.setSelected(True)

        self.queue.put( [ 150 , u"downloadThumbnail"  , shotDictList , self.findInTree ] )


    @decorateur_try_except
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
                    seqItem = assetWidget(root, "No Asset Type")
                    shotItem = shotAssetWidget(seqItem, shot_sgData, typeEntity)
                else :
                    shotItem = shotAssetWidget(nullSequenceList[0], shot_sgData, typeEntity)

            elif not shot_sgData["sg_asset_type"] in seqList :
                seqItem = assetWidget(root, shot_sgData["sg_asset_type"])
                shotItem = shotAssetWidget(seqItem, shot_sgData, typeEntity)
                seqList.append( shot_sgData["sg_asset_type"])

            else :
                for seqItem in self.findInTree( "assetType_%s"%shot_sgData["sg_asset_type"],  None) :
                    shotItem = shotAssetWidget(seqItem, shot_sgData, typeEntity)

            if shot_sgData["id"] == self.InitOnShotName["id"] :
                shotItem.setSelected(True)

        self.queue.put( [ 150 , u"downloadThumbnail"  , shotDictList , self.findInTree ] )


 
    ####
    @decorateur_try_except
    def clearTree(self, obj) :
        obj[0].clear()
        obj[0].lastItem_edited = None

    #####
    @decorateur_try_except
    def queryNoteContent(self, obj) :

        sg_noteContentList = obj[0]
        if len(sg_noteContentList) == 0 :
            pass
        elif len(sg_noteContentList) == 1 :

            my_noteLayoutWidget = noteLayoutWidget( sg_noteContentList )
            my_noteLayoutWidget.SIGNAL_createReply.connect( self.replyNoteSlot)

            self.clearRightLayout()
            self.rightLayout.addWidget(  my_noteLayoutWidget  )
            
        else :

            my_noteLayoutWidget = noteLayoutWidget( sg_noteContentList )
            my_noteLayoutWidget.SIGNAL_createMultiReply.connect( self.multiReplyNoteSlot)

            self.clearRightLayout()
            self.rightLayout.addWidget(  my_noteLayoutWidget  ) 

    ######
    @decorateur_try_except
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



        self.queue.put( [ -1 , u"queryNoteVersion"  , [ 0 , [],  int_noteId  ] , None ] )



        if obj[1]:   
            self.queue.put( [ -1 , u"queryNoteContent"  , noteData , None ] )


    
    @decorateur_try_except   
    def queryNoteVersion(self, obj) :
        for noteWidget in self.myTree2.findItems("note_%i"%obj[0], QtCore.Qt.MatchRecursive,10) :
            
            noteWidget.setText(5, obj[1])
            noteWidget.setText(7, str(obj[2]) )
            noteWidget.setText(11, str(obj[3]))
            noteWidget.set_my_bacgroundColor()

    @decorateur_try_except
    def queryNoteTaskAssigned(self, obj) :
        for noteWidget in self.myTree2.findItems("note_%i"%obj[0], QtCore.Qt.MatchRecursive,10) :
            noteWidget.setText(8, str("\n".join(obj[1]) ) )
            self.updateTree2_withFilter()

def main():
    


    app = QtGui.QApplication(sys.argv)
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

    ex = Example()
    

    sys.exit(app.exec_())



if __name__ == '__main__':
    import os
    from PyQt4 import QtGui, QtCore

    main()








