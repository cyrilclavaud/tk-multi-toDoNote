#!/usr/bin/python
# -*- coding: utf-8 -*-

import _strptime

import random
import time
import os
import re
import sys
import Queue

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




class myQTree( QtGui.QTreeWidget ):
    pixmap = None

    SIGNAL_updateNoteContent = _signal(object)

    SIGNAL_selectShot = _signal(object)
    SIGNAL_setNoteStatus = _signal(object)
    SIGNAL_setNoteType = _signal(object)
    SIGNAL_deleteNotes = _signal(object)
    SIGNAL_setNoteTask = _signal(object)


    def __init__(self, task_entriesDictList ):
        QtGui.QTreeWidget.__init__(self)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.task_entriesDictList = task_entriesDictList

        self.pixmap = QtGui.QPixmap( getRessources("note_folded.png") )
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.onCustomContextMenuRequested)

        self.itemDoubleClicked.connect(self.editItem)
        self.itemClicked.connect( self.close_editItem )

        self.lastItem_edited = None

    def onCustomContextMenuRequested( self, pos) :
        item = self.itemAt(pos);
        if ( item ) : 
            self.showContextMenu(item, self.viewport().mapToGlobal(pos))
    
    @decorateur_try_except
    def showContextMenu(self, item,  globalPos) :
        import functools

        if str(item.text(10)).startswith("note_") :
            menu = QtGui.QMenu()
            menu.addAction("Select Shot(s)",  lambda : self.SIGNAL_selectShot.emit( self.selectedItems() )  )
            statusMenu = menu.addMenu("Set Status")
            statusMenu.addAction(QtGui.QIcon(getRessources("status_opn.png") ) , "Open", lambda: self.SIGNAL_setNoteStatus.emit(([self.selectedItems(), "opn"] ) ) )
            statusMenu.addAction(QtGui.QIcon(getRessources("status_ip.png") )  , "In progress", lambda: self.SIGNAL_setNoteStatus.emit(([self.selectedItems(), "ip"]) ) )
            statusMenu.addAction(QtGui.QIcon(getRessources("status_clsd.png") ), "Closed", lambda: self.SIGNAL_setNoteStatus.emit(( [self.selectedItems(),"clsd"]) ) )
            
            typeMenu = menu.addMenu("Set Type")
            typeMenu.addAction(QtGui.QIcon(getRessources("type_toDo.png") ), "To-do", lambda: self.SIGNAL_setNoteType.emit(( [self.selectedItems(),"To-do"]) ) )
            typeMenu.addAction(QtGui.QIcon(getRessources("type_client.png") ), "Client", lambda: self.SIGNAL_setNoteType.emit(( [self.selectedItems(),"Client"]) ) )
            typeMenu.addAction(QtGui.QIcon(getRessources("type_internal.png") )  , "Internal", lambda: self.SIGNAL_setNoteType.emit(([self.selectedItems(), "Internal"]) ) )
            typeMenu.addAction(QtGui.QIcon(getRessources("type_assetUpdated.png") ) , "Asset Update", lambda: self.SIGNAL_setNoteType.emit(([self.selectedItems(), "Asset Update"] ) ) )
            typeMenu.addAction(QtGui.QIcon(getRessources("type.png") ), "NoType", lambda: self.SIGNAL_setNoteType.emit(( [self.selectedItems(),None]) ) )
            
            taskMenu = menu.addMenu("Set Task")

            for entries in self.task_entriesDictList[1:] :
                
                actionFct = lambda taskValues=entries["values"] : self.SIGNAL_setNoteTask.emit( [ self.selectedItems(), taskValues ] ) 
                taskEntry = taskMenu.addAction(QtGui.QIcon(getRessources(entries["icon"]) ), entries["text"], actionFct )


            deleteMenu = menu.addAction("Delete note(s)",  lambda : self.SIGNAL_deleteNotes.emit( [self.selectedItems()] )  )
            menu.exec_(globalPos)


    def selectShot_slot(self):
        self.SIGNAL_selectShot.emit( self.selectedItems() )

    @decorateur_try_except
    def setNoteStatus_slot(self, status):
        print status

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

        else :
            option.displayAlignment = QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter 
            #option.decorationSize = QtCore.QSize(16,16)

            if index.row() % 2 :
                painter.fillRect( option.rect, QtGui.QColor(0,0,0, 0) )
            else :
                painter.fillRect( option.rect, QtGui.QColor(0,0,0, 80) )


            QtGui.QTreeWidget.drawRow(self, painter, option, index )
    

       
    def drawBranches(self, painter, rect, index):
        return 


        """
        if not self.model().hasChildren(index):
            QtGui.QTreeWidget.drawBranches(self, painter, rect, index)
        return

        """
        
        #item = index.internalPointer()
        
        
        # Draw background (separator or highlight)
        opt = QtGui.QStyleOptionViewItem(self.viewOptions())
        """
        if self.selectionModel().isSelected(index):
            painter.fillRect(rect, opt.palette.brush(QtGui.QPalette.Highlight))
        """
        # XXX: It would be nice to get rid of the connection lines in the expander.
        if self.model().hasChildren(index):
            pass
            opt.state = opt.state | QtGui.QStyle.State_Children
            
            if self.isExpanded(index):
                opt.state = opt.state | QtGui.QStyle.State_Open
                 
            prim = QtCore.QRect(rect.left(), rect.top(), self.indentation(), rect.height())
            opt.rect = prim
            self.style().drawPrimitive(QtGui.QStyle.PE_IndicatorBranch, opt, painter, self)      

           
        return








class joinQueue( Queue.PriorityQueue ) :
    def put(self, args):
        Queue.PriorityQueue.put(self, args)
        self.join() 






class Example(QtGui.QWidget):


    def __init__(self ):


        pprint("Example.__init__\n", True)
        perr("",True)
        plog("",True)



        QtGui.QWidget.__init__(self)
        #self.setWindowFlags(QtCore.Qt.WindowMaximizeButtonHint)
              
        """
        flags = QtCore.Qt.ToolTip
        
        flags |= QtCore.Qt.WindowTitleHint
        flags |= QtCore.Qt.WindowSystemMenuHint   
        flags |= QtCore.Qt.WindowMinimizeButtonHint
        flags |= QtCore.Qt.WindowMaximizeButtonHint
        flags |= QtCore.Qt.WindowCloseButtonHint
        flags |= QtCore.Qt.WindowContextHelpButtonHint
        flags |= QtCore.Qt.WindowShadeButtonHint
        flags |= QtCore.Qt.WindowStaysOnTopHint
        
        self.setWindowFlags(flags)
        """
        self.queue = None

        if "USE THREADING" :
            pprint("use threading")
            print "use threading"
            self.queue = Queue.PriorityQueue()
        else :
            pprint("don't use threading")
            self.queue = joinQueue()
        
        projectId = 191
        userDict = None

        self.InitOnShotName = {"id":0}
        self.InitFilterOnTaskName = None

        self._app = None
        try :
            self._app = sgtk.platform.current_bundle()



            projectDict = self._app.context.project
            pprint("Project :" + str( projectDict ) + "\n")
            projectId = projectDict["id"]
            
            userDict = self._app.context.user
            pprint("User :" + str( userDict ) + "\n")

            #print str(dir( self._app.context) )
            if self._app.context.task :
                self.InitFilterOnTaskName = self._app.context.task["name"]

            entityDict = self._app.context.entity
            pprint("Entity : " +  str( entityDict ) + "\n")
            
            if entityDict :
                if entityDict["type"] == "Shot" :

                    self.InitOnShotName= entityDict
                    pprint("init not manager on shot "+ str(self.InitOnShotName) + "\n")
        except :
            pprint(str( "cant get context entity") + "\n")

        

        for i in range(5) :
            sg = sg_query( self._app  )            

            sg.setProjectId(projectId)
            sg.setTempPath()
            sg.queue=self.queue
            sg.th_id = i

            sg.SIGNAL_setThumbnail.connect(self.setTreeThumbNail )
            sg.SIGNAL_setNoteList.connect(self.setNoteList )
            sg.SIGNAL_queryAllShot.connect(self.fillSeqShotTree )
            sg.SIGNAL_clearTree.connect( self.clearTree )
            sg.SIGNAL_queryNoteContent.connect( self.queryNoteContent )
            sg.SIGNAL_replyNote.connect( self.noteTreeUpdated)
            sg.SIGNAL_queryNoteVersion.connect(self.queryNoteVersion)
            sg.SIGNAL_queryVersion.connect(self.updateDrawNote_versions)
            sg.SIGNAL_addNote.connect( self.addNote )
            sg.SIGNAL_refreshNote.connect( self.refreshNote)
            
            sg.SIGNAL_queryNoteTaskAssigned.connect(self.queryNoteTaskAssigned )
            sg.start()



        self.initUI()
     

        self.queue.put( [ 3,u"fillSeqShotTree"  , None , None ] )
        ## self.queue.join() ## 

        self.shotTreeSelection_id_List = []

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


    def initUI(self):
        mainLayout = QtGui.QVBoxLayout() 
        mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(mainLayout)
        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)


        self.filteringLayout = QtGui.QHBoxLayout()
        self.filteringLayout.setContentsMargins(0,0,0,0)
        self.refreshUI_Btn = toggleBtn("PAF")


        ############# TASK




        task_entriesDictList = [ {"text" : "All", "icon" : None, "values": []  },
                            {"text" : "Compo", "icon" : "task_compo.png", "values": ["Compositing", "Comp", "Compo"] },
                            {"text" : "Anim", "icon" : "task_animation.png", "values": ["Animation","animation","anim", "Anim"]  },
                            {"text" : "lighting", "icon" : "task_lit.png" , "values": ["Lighting", "lighting"]  },
                            {"text" : "Fur", "icon" : "task_fur.png" , "values": ["fur","Fur"] },
                            {"text" : "modeling", "icon" : "task_modelisation.png" , "values": ["Modeling", "modeling"] },
                            {"text" : "rigging", "icon" : "task_rig.png" , "values": ["Rig", "rig"] },
                            {"text" : "layout", "icon" : "task_layout.png" , "values": ["Layout", "layout"] },
                            {"text" : "NoTask", "icon" : "task.png" , "values": ["NoTask"] }
                          ]
        
        task_entriesDictList = self.setCheckedFromValue(task_entriesDictList, [self.InitFilterOnTaskName] + ["NoTask"] )   
        self.taskFilterWidget =  comboFilterWidget2( {"name":"Task" , "icon": "task.png"}, task_entriesDictList, multiCheckable = True )




        ############# TYPE

        entriesDictList = [ {"text" : "All", "icon" : None , "values":[]},
                            {"text" : "To Do", "icon" : "type_toDo.png", "values":["To-do", "To Do"],"checked" : True },
                            {"text" : "Client", "icon" : "type_client.png", "values":["Client"] },
                            {"text" : "Internal", "icon" : "type_internal.png" , "values": ["Internal"]},
                            {"text" : "Asset Update", "icon" : "type_assetUpdated.png", "values":["Asset Update"]},
                            {"text" : "NoType", "icon" : "type.png" , "values": ["NoType"] },
                          ]
        entriesDictList = self.setCheckedFromValue(entriesDictList, [None] )
        self.typeFilterWidget = comboFilterWidget2( {"name":"Type" , "icon": "type.png"}, entriesDictList, multiCheckable = True ) 
        





        ############# STATUS

        entriesDictList = [ {"text" : "All", "icon" : None, "values":[]} ,
                            {"text" : "Open", "icon" : "status_opn.png", "values":["opn","Open"], "checked":True} ,
                            {"text" : "In Progress", "icon" : "status_ip.png", "values":["ip","In Progress"]} ,
                            {"text" : "Closed", "icon" : "status_clsd", "values":["clsd", "Closed"] } ,
                          ]

        entriesDictList = self.setCheckedFromValue(entriesDictList, ["Open", "ip"] )
        self.statusFilterWidget = comboFilterWidget2( {"name":"Status" , "icon": "status.png"}, entriesDictList, multiCheckable = True  )
        


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
        midLayout.setContentsMargins(2,2,2,2)
        self.rightLayout = QtGui.QHBoxLayout()
        self.rightLayout.setContentsMargins(2,2,2,2)
 
        self.myTree = QtGui.QTreeWidget() 
        self.myTree.setIconSize(QtCore.QSize(128,128))
        self.myTree.setColumnCount(11)
        self.myTree.setHeaderLabels(["Shots","Note count"])
        self.myTree.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.myTree.setFocusPolicy(QtCore.Qt.NoFocus)


        self.myTree2 = myQTree( task_entriesDictList )# QtGui.QTreeWidget() 
        self.myTree2.setIconSize(QtCore.QSize(128,128))
        self.myTree2.setColumnCount(11)
        self.myTree2.setHeaderLabels(["Note Content","Note count", "Type","Created_at", "User", "v---", "Shot", "Replies", "Shot Assignement"])
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
        header.setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        header.setResizeMode(1, QtGui.QHeaderView.ResizeToContents)
        header.setResizeMode(2, QtGui.QHeaderView.ResizeToContents)
        header.setResizeMode(3, QtGui.QHeaderView.ResizeToContents)
        header.setResizeMode(6, QtGui.QHeaderView.ResizeToContents)
        header.setResizeMode(7, QtGui.QHeaderView.ResizeToContents)
        header.setResizeMode(8, QtGui.QHeaderView.ResizeToContents)
        
        for column in range(9, self.myTree2.columnCount()):
            header.hideSection(header.logicalIndex(header.visualIndex(column)))
        header.hideSection(header.logicalIndex(1))

        header.swapSections(6,7)

        for column in range( self.myTree2.columnCount() ):
            self.myTree2.resizeColumnToContents( column )
            print header.visualIndex(column)

        leftLayout.addWidget(self.myTree)
        midLayout.addWidget(self.myTree2)


        self.rightLayout.addWidget( noteLayoutWidget( None,  [ self.getShotItemList() , self.taskFilterWidget, self.typeFilterWidget, self.statusFilterWidget,[] ], self.queue ) )
        

        wFiltering = QtGui.QWidget()
        wFiltering.setLayout(self.filteringLayout)
        horizontalSplitter = QtGui.QSplitter() 
        horizontalSplitter.addWidget(wFiltering)
        horizontalSplitter.setOrientation(QtCore.Qt.Vertical)

        horizontalSplitter.setObjectName("verti")

        mainLayout.addWidget(horizontalSplitter)
        #mainLayout.addLayout(layout)


        splitter = QtGui.QSplitter()
        splitter.setObjectName("hori")

        style = "QSplitter::handle:vertical#verti {background: qlineargradient(x1:0, y1:1, x2:0, y2:1, stop:0 rgba(120, 120, 150, 40% ), stop:1 rgba(120, 120, 150, 40% ) );border: 1px solid rgba(120, 120, 150, 40% ); width : 1px ; height : 1px ;margin-right: 2px;margin-left: 2px;border-radius: 4px;}\n"
        style += "QSplitter::handle:horizontal#hori {background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(120, 120, 150, 40% ), stop:1 rgba(120, 120, 150, 40% ));border: 1px solid rgba(120, 120, 150, 40% ) ;width: 13px;margin-top: 2px;margin-bottom: 2px;border-radius: 4px;}"
        splitter.setStyleSheet(style )
        horizontalSplitter.setStyleSheet(style )

       

        ok = QtGui.QWidget()
        ok.setLayout(leftLayout)      
        
        ok2 = QtGui.QWidget()
        ok2.setLayout(midLayout)

        ok3 = QtGui.QWidget()
        ok3.setLayout(self.rightLayout)

        
        splitter.addWidget(ok)
        splitter.addWidget(ok2)
        splitter.addWidget(ok3)

        
        splitSize = splitter.size().width()
        
        col1 = int(splitSize/3)
        col2 = int(splitSize/5)
        if self.InitOnShotName["id"] :
            col1 = 0.0

        splitter.setSizes([ col1,col2, splitSize-(col1+col2)])



        layout.addWidget(splitter)
        horizontalSplitter.addWidget(splitter)
        horizontalSplitter.setStretchFactor( 0, 0 )
        horizontalSplitter.setStretchFactor( 1, 1 )

        splitter.setStretchFactor( 0, 0 )
        splitter.setStretchFactor( 1, 1 )
        splitter.setStretchFactor( 2, 0 )


        splitter.splitterMoved.connect(self.resizeFilterLayout  )

        self.myTree.itemSelectionChanged.connect(self.shotTreeClicked )
        self.refreshUI_Btn.clicked.connect(  lambda : self.shotTreeClicked( True )  ) 

        self.taskFilterWidget.widget.currentIndexChanged.connect( self.updateTree2_withFilter )
        self.typeFilterWidget.widget.currentIndexChanged.connect( self.updateTree2_withFilter )
        self.statusFilterWidget.widget.currentIndexChanged.connect( self.updateTree2_withFilter )
        self.userNameFilterWidget.widget.textChanged.connect(self.updateTree2_withFilter)
        self.contentFilterWidget.widget.textChanged.connect(self.updateTree2_withFilter)
        self.entityAssignedFilterWidget.widget.textChanged.connect(self.updateTree2_withFilter)

        self.myTree2.SIGNAL_setNoteStatus.connect(self.setNoteStatus)
        self.myTree2.SIGNAL_setNoteType.connect(self.setNoteType)
        self.myTree2.SIGNAL_selectShot.connect(self.selectShotMyTree)
        self.myTree2.SIGNAL_deleteNotes.connect(self.deleteNotes)
        self.myTree2.SIGNAL_updateNoteContent.connect(self.updateNoteContent)
        self.myTree2.SIGNAL_setNoteTask.connect(self.setNoteTask)

        self.myTree2.itemSelectionChanged.connect(self.noteTreeClicked )

        self.groupByTypeBox.stateChanged.connect(self.refreh_myTree2)

        self.spacerItem.changeSize(col1-14, 1)
        self.filteringLayout.invalidate()

        self.show()

  
    def resizeFilterLayout(self, pos, idx):

        if idx == 1 :
             
            self.spacerItem.changeSize(pos-14, 1)
            self.filteringLayout.invalidate()


    def fillNotesTree(self, parent):
        self.queue.put( [2 , u"queryNotes"  , parent.sgData, None ] )
        ## self.queue.join() ## 


    def findInTree(self, sg_id, parent = None):
        root = self.myTree
        if parent :
            root = parent
        
        #return root.findItems( sg_id, QtCore.Qt.MatchExactly, 10 ) 
        return root.findItems( sg_id, QtCore.Qt.MatchRecursive,10 )


    def filterNote(self, noteDict ) :
        # noteDict["tag_list"],
        #print  noteDict["sg_note_type"],  noteDict["subject"]
        pass   


    def getNoteTaskNameList(self, noteDict ) :
        taskList = []
        if  noteDict["tasks"] :
            for taskDict in noteDict["tasks"] :
                taskDictName = self.taskFilterWidget.retrieveNameFromValue(taskDict["name"] )
                if not taskDictName in taskList :
                    taskList.append(taskDictName )
        if not taskList :
            return ["NoTask"]

        return  taskList



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
            print self.myTree.findItems("shotAsset_", QtCore.Qt.MatchStartsWith,  10)
            for shotAssetItem in self.myTree.findItems("shotAsset_", QtCore.Qt.MatchStartsWith  | QtCore.Qt.MatchRecursive,  10) : 
                
                self.queue.put( [ 0 , u"queryTaskAssigned" ,  [shotAssetItem.sgData, soloCheckedTask] , None ] )

    def updateNoteContent(self, obj ):
        #[0] note content
        #[1] note id
        
        self.queue.put( [ 0 , u"editNoteContent" ,  obj , None ] )
        ## self.queue.join() ## 
    

    def refreh_myTree2(self, state) :

        header = self.myTree2.header()
        if state :
            header.hideSection(header.logicalIndex(header.visualIndex(2)))
        else :
            header.showSection(header.logicalIndex(header.visualIndex(2)))
        self.shotTreeClicked(forceRedraw = True)


    def setNoteStatus(self, itemListAndStatus_list):
        for item in itemListAndStatus_list[0]:
            noteId = 0 
            if item.sgData.has_key('id') :
                noteState = {"new_sg_status_list":itemListAndStatus_list[1], "id" : item.sgData['id']}
                self.queue.put( [ 0 , u"setNoteStatus" , [noteState] , None ] )

    

    def setNoteType(self, itemListAndType_list):
        for item in itemListAndType_list[0]:
            noteId = 0 
            if item.sgData.has_key('id') :
                noteType = {"new_sg_note_type":itemListAndType_list[1], "id" : item.sgData['id']}
                self.queue.put( [ 0 , u"setNoteType" , [noteType] , None ] )


    def setNoteTask(self, itemListAndTaskValues_list) :


        for item in itemListAndTaskValues_list[0] :
            if item.sgData.has_key('id') :
                print itemListAndTaskValues_list[1]
                self.queue.put( [ 0 , u"setNoteTask" , [item.sgData, itemListAndTaskValues_list[1] ] , None ] )

    def deleteNotes(self, itemList ) :
        for item in itemList[0]:

            if item.sgData.has_key('id') :
                #noteType = {"new_sg_note_type":itemListAndType_list[1], "id" : item.sgData['id']}
                self.queue.put( [ 0 , u"deleteNote" , [item.sgData['id']] , None ] )

   
    def multiReplyNoteSlot(self, obj):
        self.queue.put( [ 0 , u"multyReplyNote" , obj , None ] )
        self.queue.join()

 
    def replyNoteSlot(self, obj) :
        self.queue.put( [ 0 , u"replyNote" , obj , None ] )
        ## self.queue.join() ## 


    def noteTreeClicked(self) :
        plog("the tree note has been clicked \n")
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
                noteData.append( itemW.sgData )
    

            elif str(itemW.text(10)).startswith("task") :
                taskList.append(str( itemW.text(0) ) )


        if noteData :
            pprint("A query note content has been put to the queue \n")
            self.queue.put( [ 0 , u"queryNoteContent"  , noteData , None ] )
            ## self.queue.join() ## 
        elif selectedItemList :

            self.drawNote(taskList)

   
    def drawNote(self, taskList = []):

        my_noteLayoutWidget = noteLayoutWidget( None,  [ self.getShotItemList(), self.taskFilterWidget, self.typeFilterWidget, self.statusFilterWidget, taskList ], self.queue )
        my_noteLayoutWidget.SIGNAL_send_NoteContent.connect( self.createNewNote )
        my_noteLayoutWidget.updateTaskFilterWidget(taskList)



        my_noteLayoutWidget.SIGNAL_createReply.connect( self.replyNoteSlot )
        my_noteLayoutWidget.SIGNAL_createMultiReply.connect( self.multiReplyNoteSlot )

        self.clearRightLayout()
        self.rightLayout.addWidget(  my_noteLayoutWidget  )


    def createNewNote(self, obj) :
        
        self.queue.put( [ 0 , u"createNote"  , [ obj ] , None ] )
        ## self.queue.join() ## 



    def shotTreeClicked(self, forceRedraw = False) :
        
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
            """
            pprint("redraw note tree ! \n") 
            keepBackList = []
            while not self.queue.empty() :
                host = self.queue.get()
                if host[0] in [150,2] :
                    keepBackList.append(host)

                self.queue.task_done()
            self.queue.join()

            pprint("add To queue clear note tree ! \n") 
            """
            self.queue.put( [-10 ,u"clearTree" , self.myTree2, None]  )
            ## self.queue.join() ## 
            """
            for kept in keepBackList:
                self.queue.put( kept )
                ## self.queue.join() ## 
            """
        selectedItemList = newItems 

        shotItemList = []
        for itemW in selectedItemList :
            pprint( itemW.text(10)  + "\n")
            if str(itemW.text(10)).startswith("shotAsset") :

                if not itemW.sgData in shotItemList :
                    shotItemList.append(itemW.sgData )

            if str(itemW.text(10)).startswith("sequence") :

                for shotWItem in itemW.getShotWidgetList() :
                    if not shotWItem.sgData in shotItemList :
                        shotItemList.append(shotWItem.sgData )
        
        for sgData in shotItemList :
            self.queue.put( [1, u"queryNotes"  , sgData, True ] )
            ## self.queue.join() ## 

        self.drawNote() 



    def getShotItemList(self):
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
  
    def addNote(self, obj ) :

        for noteDict in obj : # boucler chaques notes
            taskList = self.getNoteTaskNameList(noteDict) 

            for taskName in taskList : # trouver le task tree widget, peut y'en a voir plusieurs. une note peut etre linker a pluseiurs tasks  
                for treeWidgetItem in [ self.myTree2 ] : #treeWidgetItemList :
                    taskWidgetItemList = treeWidgetItem.findItems( "task_%s"%taskName, QtCore.Qt.MatchExactly, 10 ) 
    
                    if not taskWidgetItemList :
                        ptaskWidget = taskWidget(treeWidgetItem, {"name": taskName}, self.taskFilterWidget )
                        
    
                        taskWidgetItemList = [ ptaskWidget ]

                    for taskWidgetItem in taskWidgetItemList  : 
                        
                        findSubItemStr = 'type_'
                        group = False
                        if self.groupByTypeBox.checkState() == QtCore.Qt.Checked :
                            findSubItemStr = "type_%s"%noteDict["sg_note_type"]
                            group = True
                
                        typeNoteWidgetItem = taskWidgetItem.findItems(findSubItemStr, QtCore.Qt.MatchExactly, 10  ) 
                        
                        if not typeNoteWidgetItem :
                            typeNoteWidgetItem = typeNoteWidget(taskWidgetItem , {"name" :noteDict["sg_note_type"] },  self.typeFilterWidget , group )
                            typeNoteWidgetItem.setHidden(False)
                        else :
                            typeNoteWidgetItem = typeNoteWidgetItem[0]
                        
                        #noteDict["shotCode"] = obj[0][1]
                        noteWidget( typeNoteWidgetItem, noteDict, self.statusFilterWidget, self.typeFilterWidget, self.userNameFilterWidget, self.contentFilterWidget,  self.entityAssignedFilterWidget  )
                        taskWidgetItem.setHidden(False)
                        typeNoteWidgetItem.setHidden(False)
                        self.queue.put( [ 2 , u"queryNoteVersion"  , noteDict["id"] , None ] )
                        taskValuesList = self.taskFilterWidget.retrieveValueFromName( taskName )
                        self.queue.put( [ 2 , u"queryTaskAssigned"  , [{'id' : noteDict["shotId"],'type' : 'Shot'}, taskValuesList,  noteDict["id"]]   , None ] )
                        ## self.queue.join() ## 

                   
    def updateDrawNote_versions(self, obj) :
        noteLayoutQItem = self.rightLayout.itemAt(0)
        noteLayoutWidget= noteLayoutQItem.widget()
        if noteLayoutWidget.data == None:
            noteLayoutWidget.fill_versionWidgetCombo(obj)
    
    #

    def setTreeThumbNail(self, obj) :
        treeWidgetItemList =  self.findInTree(obj[0])

        for  treeWidgetItem in treeWidgetItemList :
            treeWidgetItem.setIcon(0, QtGui.QIcon(obj[1]))

                

    def getShotIds(self):
        shotItemList = []
        for itemW in self.myTree.selectedItems() :
            if str(itemW.text(10)).startswith("shotAsset") :
                if not itemW.text(10) in shotItemList :
                    shotItemList.append(itemW.text(10) )

            if str(itemW.text(10)).startswith("sequence") :
                for shotWItem in itemW.getShotWidgetList() :
                    if not str(shotWItem.text(10) ) in shotItemList :
                        shotItemList.append( str(shotWItem.text(10) ) )

        return shotItemList
    ##

    def setNoteList(self, obj) : # by shot

        if not obj[0][0] in self.getShotIds() :
            return
        

        treeWidgetItemList = [ self.myTree2 ]
        
        if obj[2] == None :
            treeWidgetItemList =  self.findInTree(obj[0][0] )

        taskList = {}
        for noteToGetTask in obj[1] :
            self.filterNote(noteToGetTask)
            if noteToGetTask["tasks"] :
                for taskLink in noteToGetTask["tasks"] :
                    taskLinkName =  self.taskFilterWidget.retrieveNameFromValue(taskLink["name"])
                    if not taskLinkName in taskList.keys() :
                        taskList[taskLinkName ] = 1
                    else :
                        taskList[taskLinkName ] += 1
            else :
                if not "NoTask" in taskList.keys() :
                    taskList["NoTask"] = 1
                else :
                    taskList["NoTask"] += 1

        for treeWidgetItem in treeWidgetItemList : 
            if obj[2] == None :
                treeWidgetItem.setText(1, str( len( obj[1]) ) )     

            for taskName in taskList.keys() :

                taskWidgetItem = treeWidgetItem.findItems( "task_%s"%taskName , QtCore.Qt.MatchExactly, 10 )
                if not taskWidgetItem :
                    ptaskWidget = taskWidget(treeWidgetItem, {"name": taskName}, self.taskFilterWidget )
                    ptaskWidget.setText(1, str( int( ptaskWidget.text(1) ) +  taskList[taskName] )  ) 
                else :
                    taskWidgetItem[0].setText(1, str( int( taskWidgetItem[0].text(1) ) +  taskList[taskName] )  )

        for noteDict in obj[1] : # boucler chaques notes
            taskList = self.getNoteTaskNameList(noteDict) 

            for taskName in taskList : # trouver le task tree widget, peut y'en a voir plusieurs. une note peut etre linker a pluseiurs tasks  
                for treeWidgetItem in treeWidgetItemList :
                    for taskWidgetItem in treeWidgetItem.findItems( "task_%s"%taskName, QtCore.Qt.MatchExactly, 10 )  : 
                        
                        findSubItemStr = 'type_'
                        group = False
                        if self.groupByTypeBox.checkState() == QtCore.Qt.Checked :
                            findSubItemStr = "type_%s"%noteDict["sg_note_type"]
                            group = True
                
                        typeNoteWidgetItem = taskWidgetItem.findItems(findSubItemStr, QtCore.Qt.MatchExactly, 10  ) 
                        
                        if not typeNoteWidgetItem :
                            typeNoteWidgetItem = typeNoteWidget(taskWidgetItem , {"name" :noteDict["sg_note_type"] },  self.typeFilterWidget , group )
                        else :
                            typeNoteWidgetItem = typeNoteWidgetItem[0]
                        
                        noteDict["shotCode"] = obj[0][1]
                        noteDict["shotId"] = obj[0][2]

                        noteWidget( typeNoteWidgetItem, noteDict, self.statusFilterWidget, self.typeFilterWidget, self.userNameFilterWidget, self.contentFilterWidget,  self.entityAssignedFilterWidget )
                        self.queue.put( [ 2 , u"queryNoteVersion"   , noteDict["id"] , None ] )
                        taskValuesList = self.taskFilterWidget.retrieveValueFromName( taskName )
                        self.queue.put( [ 2 , u"queryTaskAssigned"  , [{'id' : noteDict["shotId"],'type' : 'Shot'}, taskValuesList,  noteDict["id"]]   , None ] )
                        ## self.queue.join() ## 
    ###
        self.updateTree2_withFilter()

    def fillSeqShotTree(self, shotDictList = []):

        root = self.myTree

        seqList=[]

        for shot_sgData in   shotDictList :

            if not shot_sgData["sg_sequence"] :
                nullSequenceList = self.findInTree( "sequence_0",  None)
                seqItem = None

                if not nullSequenceList :
                    seqItem = sequenceWidget(root, {"name": u"No Sequence", "id": 0 })
                    
                    shotItem = shotAssetWidget(seqItem, shot_sgData)


                else :
                    shotItem = shotAssetWidget(nullSequenceList[0], shot_sgData)


            elif not shot_sgData["sg_sequence"] in seqList :
                seqItem = sequenceWidget(root, shot_sgData["sg_sequence"])
                shotItem = shotAssetWidget(seqItem, shot_sgData)
                seqList.append( shot_sgData["sg_sequence"])

                #self.fillNotesTree(shotItem)
            else :
                for seqItem in self.findInTree( "sequence_%i"%shot_sgData["sg_sequence"]["id"],  None) :
                    shotItem = shotAssetWidget(seqItem, shot_sgData)
                    #self.fillNotesTree(shotItem)

            if shot_sgData["id"] == self.InitOnShotName["id"] :
                pprint("select with InitOnShotName")
                shotItem.setSelected(True)

        self.queue.put( [ 150 , u"downloadThumbnail"  , shotDictList , self.findInTree ] )
 
    ####

    def clearTree(self, obj) :
        pprint(" clear tree \n")
        obj[0].clear()
        obj[0].lastItem_edited = None


    #####

    def queryNoteContent(self, obj) :

        sg_noteContentList = obj[0]
        if len(sg_noteContentList) == 0 :
            pprint("create Note \n")
        elif len(sg_noteContentList) == 1 :
            pprint("show Note \n")


            my_noteLayoutWidget = noteLayoutWidget( sg_noteContentList )
            my_noteLayoutWidget.SIGNAL_createReply.connect( self.replyNoteSlot)

            self.clearRightLayout()
            self.rightLayout.addWidget(  my_noteLayoutWidget  )
            
        else :
            pprint("Multi Reply Note \n")
            my_noteLayoutWidget = noteLayoutWidget( sg_noteContentList )
            my_noteLayoutWidget.SIGNAL_createMultiReply.connect( self.multiReplyNoteSlot)

            self.clearRightLayout()
            self.rightLayout.addWidget(  my_noteLayoutWidget  ) 

    ######

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


        self.queue.put( [ -1 , u"queryNoteVersion"  , int_noteId , None ] )

        ## self.queue.join() ## 
        if obj[1]:   
            self.queue.put( [ -1 , u"queryNoteContent"  , noteData , None ] )
            ## self.queue.join() ## 
        self.queue.join()
    
   
    def queryNoteVersion(self, obj) :
        for noteWidget in self.myTree2.findItems("note_%i"%obj[0], QtCore.Qt.MatchRecursive,10) :
            
            noteWidget.setText(5, obj[1])
            noteWidget.setText(7, str(obj[2]) )

    def queryNoteTaskAssigned(self, obj) :
        for noteWidget in self.myTree2.findItems("note_%i"%obj[0], QtCore.Qt.MatchRecursive,10) :
            noteWidget.setText(8, str("\n".join(obj[1]) ) )
            self.updateTree2_withFilter()

def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    import os
    from PyQt4 import QtGui, QtCore
    main()








