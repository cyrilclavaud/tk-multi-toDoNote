#!/usr/bin/python
# -*- coding: utf-8 -*-

import _strptime

try :
    from sgtk.platform.qt import QtCore, QtGui
    _signal = QtCore.Signal 
    outFileName = "side"

except :
    from PyQt4 import QtGui, QtCore
    _signal = QtCore.pyqtSignal
    outFileName = "cute"


import copy

import utils
from utils import *

import ui_widget
from ui_widget import *

import treeWidgetItem
from treeWidgetItem import *

import imageDisplay
import imageScribble
import imagePicker



class noteContentLayout(QtGui.QWidget) :
    SIGNAL_createReply      = _signal(object)
    SIGNAL_createMultiReply = _signal(object)
    SIGNAL_send_NoteContent = _signal(object)

    ## ## @decorateur_try_except
    def __init__(self, dataType , data , noteData = None, parent = None) :
        super(noteContentLayout, self).__init__(parent ) 





        self.data = data
        self.noteData = noteData # is a list


        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        layoutContainer = QtGui.QHBoxLayout()
        titleGridLayout = QtGui.QGridLayout()
        layoutContainer.addLayout(titleGridLayout)
        
        #titleGridLayout.setColumnStretch(2,40)

        # author
        authorTxt = "unknown" 

        self.attachmentLayout = QtGui.QHBoxLayout()


        self.Qt_noteContent = my_textEdit( "", editable = bool(self.data) , parent = self) # QtGui.QTextEdit( )


        if self.data :

            try :
                self.Qt_noteContent.setPlainText( QtCore.QString.fromUtf8( self.data["content"]) )
            except :
                self.Qt_noteContent.setPlainText(self.data["content"] )

            if dataType == "Reply" :
                titleGridLayout.setColumnStretch(0,0)
                titleGridLayout.setColumnStretch(1,1)   
                
                authorHtmlTxt = "<font size=2 color=#BBBBBB>Author : "+self.data["user"]['name']+"</font><br>"
                dateHtmlTxt   = "<font size=2 color=#BBBBBB>Date : "+self.data["created_at"].strftime('%Y-%m-%d %H:%M:%S')+"</font>"
                labelText = QtGui.QLabel(authorHtmlTxt+dateHtmlTxt , parent = self )   
            
               
                titleGridLayout.setHorizontalSpacing(20)
                titleGridLayout.addWidget(labelText, 0,0, QtCore.Qt.AlignTop )
                titleGridLayout.addWidget( self.Qt_noteContent, 0, 1  )
                layout.addLayout(layoutContainer)
                layout.addLayout(self.attachmentLayout)
                titleGridLayout.setContentsMargins(0,0,0,0)
                layout.setContentsMargins(0,0,0,0)

            else :
                authorHtmlTxt = "<font color=#BBBBBB>Author : "+ self.data["user"]['name'] + "</font><br>"
                dateHtmlTxt = "<font color=#BBBBBB>Date : <b>"+self.data["created_at"].strftime('%Y-%m-%d %H:%M:%S')+"</font></b><br>"
                labelText = QtGui.QLabel(authorHtmlTxt+dateHtmlTxt , parent = self )

 
                titleGridLayout.addWidget(labelText, 0,0, QtCore.Qt.AlignTop)

                layout.addLayout(layoutContainer)
                layout.addWidget(self.Qt_noteContent)
                layout.addLayout(self.attachmentLayout)

                self.Qt_noteContent.setStyleSheet("QTextEdit { color : #F0F0F0 ; }")
                titleGridLayout.setContentsMargins(0,0,0,0)
                layout.setContentsMargins(0,0,0,0)


        

        if not self.data : 
            if dataType == "Reply" :  
                if len(self.noteData)>1 :
                    self.Qt_noteContent.setText(u"Type a reply for all the selected notes") 
                else :
                    self.Qt_noteContent.setText(u"Type a reply")
                    self.Qt_noteContent.selectAll()
                    self.Qt_noteContent.SIGNAL_return.connect(self.replyNoteSlot)

            elif dataType == "Note":
                self.Qt_noteContent.setText(u"Type a note")
                self.Qt_noteContent.setFocus()
                self.Qt_noteContent.selectAll()
                self.Qt_noteContent.SIGNAL_return.connect(self.createNoteSlot)
            layout.setContentsMargins(0,0,0,0)

            layout.addLayout(layoutContainer)
            layout.addWidget(self.Qt_noteContent)
            layout.addLayout(self.attachmentLayout)



        if self.data :
            for attachementFile in self.data["queriedAttachement"] :
                labelImage = PicButton(attachementFile["fileOnDisk"], overImageName = "magnifier.png", parent = self)

                labelImage.SIGNAL_imageClicked.connect( self.showImageDisplay )

                self.attachmentLayout.addWidget(labelImage)
        else :
            attachButton = QtGui.QPushButton(parent = self)
            attachmentPixmap = QtGui.QPixmap(getRessources("note_attachment.png"))
            attachementScaled = attachmentPixmap.scaled ( 32, 32, QtCore.Qt.KeepAspectRatio)
            attachButton.setIcon(QtGui.QIcon(attachementScaled))
            attachButton.clicked.connect(self.addAttachment)


            screenShotButton = QtGui.QPushButton(parent = self)
            attachmentPixmap = QtGui.QPixmap(getRessources("note_screenShot.png"))
            attachementScaled = attachmentPixmap.scaled ( 32, 32, QtCore.Qt.KeepAspectRatio)
            screenShotButton.setIcon(QtGui.QIcon(attachementScaled))
            screenShotButton.clicked.connect(self.addScreenShot)

            self.attachmentLayout.addWidget(screenShotButton)
            self.attachmentLayout.addWidget(attachButton)

            replyButton = None
            if dataType == "Reply" :   
                replyButton = QtGui.QPushButton("Reply", parent = self)
                replyButton.clicked.connect(self.replyNoteSlot)
                replyButton.setMinimumHeight(18)
                replyButton.setStyleSheet( "QPushButton {border: 1px solid #39B3FF;border-radius: 6px;background-color: #474747;background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 0.67, stop: 0 #6B6B6B, stop: 1  #474747);}")

                self.statusLabel = QtGui.QComboBox( parent = self )
                self.statusLabel.addItem(QtGui.QIcon(getRessources("status_opn.png")), "Open")
                self.statusLabel.addItem(QtGui.QIcon(getRessources("status_clsd.png")), "closed")
                self.statusLabel.addItem(QtGui.QIcon(getRessources("status_ip.png")), "In progress")

                if self.noteData[0]["sg_status_list"] == "opn" :
                    self.statusLabel.setCurrentIndex(0)
                elif self.noteData[0]["sg_status_list"] == "clsd" :
                    self.statusLabel.setCurrentIndex(1)
                elif self.noteData[0]["sg_status_list"] == "ip" : 
                    self.statusLabel.setCurrentIndex(2)

                self.statusLabel.setMaximumWidth(100)
                #self.connect(self.statusLabel, QtCore.SIGNAL("currentIndexChanged(int)"),  self.updateNodeDataStatus )
                self.statusLabel.currentIndexChanged.connect(self.updateNodeDataStatus )

                layout.addWidget(self.statusLabel)
                layout.addWidget(replyButton)

            elif dataType == "Note":
                #self.linkFilterWidget = comboFilterWidget2()

                replyButton = QtGui.QPushButton("Create Note",  parent = self )
                replyButton.clicked.connect(self.createNoteSlot)
                replyButton.setMinimumHeight(18)
                replyButton.setStyleSheet( "QPushButton {border: 1px solid #39B3FF;border-radius: 6px;background-color: #3990CA;background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 0.67, stop: 0 #3990CA, stop: 1  #215272);}")


                layout.addWidget(replyButton)

                


        self.attachmentLayout.addStretch()

        style = "background-color: red;"

    ## ## @decorateur_try_except
    def editNoteContent(self, mouseEvent ) :
        print "edit me"
    
    ## ## @decorateur_try_except
    def updateNodeDataStatus(self, comboIdx) :

        if self.statusLabel.currentIndex() == 0 :
            self.noteData[0]["new_sg_status_list"] = "opn"
        elif self.statusLabel.currentIndex() == 1 :
            self.noteData[0]["new_sg_status_list"] = "clsd"
        elif self.statusLabel.currentIndex() == 2 :
            self.noteData[0]["new_sg_status_list"] = "ip"
    
    ## ## @decorateur_try_except
    def addAttachment(self) :

        attacheFile = QtGui.QFileDialog.getOpenFileName()
        if isinstance(attacheFile, tuple) : # pySide 
            attacheFile = attacheFile[0]


        if os.path.isfile(attacheFile) :
            import shutil
            import datetime
            temp_attacheFile = os.path.join(getTempPath(), "tmp" ,datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + os.path.basename(str(attacheFile) ) )
            if not os.path.isdir(os.path.dirname(temp_attacheFile) ) :
                os.makedirs( os.path.dirname(temp_attacheFile) )

            shutil.copy(attacheFile,temp_attacheFile)
            imageWidget = PicButton( temp_attacheFile, overImageName = "pencil.png"  )
            style = " QLabel {  border: 2px solid green;   border-radius: 4px;   padding: 2px;  } "
            imageWidget.setStyleSheet(style)

            imageWidget.SIGNAL_imageClicked.connect(self.editImageDisplay)
            self.attachmentLayout.insertWidget(0, imageWidget )

    ## ## @decorateur_try_except
    def addScreenShot(self) :


        attacheFile = imagePicker.take_a_screenShot()
        if os.path.isfile(attacheFile) :
            import shutil
            import datetime
            temp_attacheFile = os.path.join(getTempPath(), "tmp" ,datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + os.path.basename(str(attacheFile) ) )
            if not os.path.isdir(os.path.dirname(temp_attacheFile) ) :
                os.makedirs( os.path.dirname(temp_attacheFile) )
            shutil.copy(attacheFile,temp_attacheFile)
            imageWidget = PicButton( temp_attacheFile, overImageName = "pencil.png" )
            style = " QLabel {  border: 2px solid green;   border-radius: 4px;   padding: 2px;  } "
            imageWidget.setStyleSheet(style)

            imageWidget.SIGNAL_imageClicked.connect(self.editImageDisplay )

            self.attachmentLayout.insertWidget(0, imageWidget )

    ## ## @decorateur_try_except
    def createNoteSlot(self) :


        noteContent = ""
        fieldContent = self.Qt_noteContent.toPlainText()
        if fieldContent != "" and fieldContent != "Type a reply" and fieldContent != "Type a reply for all the selected notes":
            if isinstance(fieldContent, unicode):
                noteContent =  fieldContent
            else :
                noteContent = unicode ( fieldContent.toUtf8(), "utf-8" )


        attachementFile = []
        for itemIdx in range(self.attachmentLayout.count() ):
            widget = self.attachmentLayout.itemAt(itemIdx).widget()
            if hasattr(widget, "fileOnDisk") :
                attachementFile.append(widget.fileOnDisk)
        


        self.SIGNAL_send_NoteContent.emit(  [  { "content" : noteContent , "uploads" : attachementFile  }]) #,  "subject" : "paf pas" } ] )

    ## ## @decorateur_try_except
    def replyNoteSlot(self):

        replyContent = ""
        fieldContent = self.Qt_noteContent.toPlainText()
        if fieldContent != "" and fieldContent != "Type a reply" :
            if isinstance(fieldContent, unicode):
                replyContent =  fieldContent
            else :
                replyContent = unicode ( fieldContent.toUtf8(), "utf-8" )

        attachementFile = []
        for itemIdx in range(self.attachmentLayout.count() ):
            widget = self.attachmentLayout.itemAt(itemIdx).widget()
            if hasattr(widget, "fileOnDisk") :
                attachementFile.append(widget.fileOnDisk)

        self.updateNodeDataStatus(0)
        if len(self.noteData) == 1 :

            value = { "type":"Note", "id":self.noteData[0]["id"], "replies":self.noteData[0]["replies"], "sg_status_list": self.noteData[0]["sg_status_list"], "new_sg_status_list" : self.noteData[0]["new_sg_status_list"] }
            self.SIGNAL_createReply.emit(   [  { "content" : replyContent , "uploads" : attachementFile } , value ]  )
        else :
            valueList = []
            for noteDict in self.noteData:
                valueList.append(  { "type":"Note", "id":noteDict["id"], "replies":noteDict["replies"], "sg_status_list": noteDict["sg_status_list"], "new_sg_status_list" : self.noteData[0]["new_sg_status_list"]  }  )

            self.SIGNAL_createMultiReply.emit(  [  { "content" : replyContent , "uploads" : attachementFile } , valueList ]  )

    ## ## @decorateur_try_except
    def showImageDisplay(self, imageFileName ) :

        imV = imageDisplay.ImageViewer(self)
        imV.setImage(imageFileName)
        imV.show()

    ## ## @decorateur_try_except
    def editImageDisplay(self, imageFileName ) :


        window = imageScribble.MainWindow( self )
        window.SIGNAL_imageUpdate.connect(self.refresh_attachementLayout)
        

        window.setWindowModality(QtCore.Qt.ApplicationModal)
        window.openImage(imageFileName)
        window.show()

    ## ## @decorateur_try_except
    def refresh_attachementLayout(self) :
        for itemIdx in range(self.attachmentLayout.count() ):
            widget = self.attachmentLayout.itemAt(itemIdx).widget()
            if hasattr(widget, "update") :
                widget.update()











class noteLayoutWidget(QtGui.QWidget) :

    SIGNAL_createReply = _signal(object)
    SIGNAL_createMultiReply = _signal(object)
    SIGNAL_send_NoteContent = _signal(object)

    ## ## @decorateur_try_except
    def filterTasks(self, indexList):


        availableTaskList = self.shotList[self.shotComboBox.currentIndex()]["sgAvailableTaskList"]


        assignedToTxt = self.top_assigneesFilterWidget.widget.text()
        if not isinstance(assignedToTxt, unicode):
            assignedToTxt = unicode(assignedToTxt.toUtf8() , "utf-8" )

        if not assignedToTxt == "" :

            availableTaskList= []
            for tasks in self.shotList[self.shotComboBox.currentIndex()]["sgtaskDictWithAssignees"].keys() :
                #print assignedToTxt.upper() , " ".join(comboFilterWidgetList[0][idx]["sgtaskDictWithAssignees"][tasks]).upper() 
                if assignedToTxt.upper() in " ".join(self.shotList[self.shotComboBox.currentIndex()]["sgtaskDictWithAssignees"][tasks]).upper() :
                    
                    availableTaskList.append(tasks)



        self.taskFilterWidget.setMyCurrentFromIndexes( indexList, availableTaskList)


        if self.taskFilterWidget.widget.count() == 1 :
            self.taskFilterWidget.drawComplex = False
        else :
            self.taskFilterWidget.drawComplex = True


        QtGui.QApplication.processEvents()
        self.taskFilterWidget.widget.repaint()


    def disableNoteLayout(self, filterIsEmpty) :
        if not filterIsEmpty :
            self.setEnabled(True)
        else :
            self.setEnabled(False)


    def __init__(self, data, comboFilterWidgetList = None, threadQueue = None, sgtkQueue = None, color = False, parent= None) : 

        super(noteLayoutWidget, self).__init__(parent ) 

        self.top_assigneesFilterWidget = None


        self.taskFilterWidget = None
        self.shotWidgetItemList = None
        self.my_versionWidgetCombo = None
        self.queue = None
        self.myNoteBox = None
        self.receiveFocusWidget = None
        self.shotList = None
        self.getFocus = True

        self.data = data

        self.multiDisplay = False
        if self.data :  
            if len(self.data) > 1 :
                self.multiDisplay = True




        self.replyListWidget = None # hold Replies, if any !


        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)


        titleGridLayout = QtGui.QGridLayout()
        titleGridLayout.setColumnStretch(0, False);
        titleGridLayout.setColumnStretch(1, False);
        



        self.titreLabel = None
        if self.data :
            if not self.multiDisplay :
                pass
                

        elif  comboFilterWidgetList[0] :

            self.top_assigneesFilterWidget  = comboFilterWidgetList[5]

            self.queue = threadQueue
            self.sgtkQueue = sgtkQueue

            idx = 0
            self.shotComboBox = comboFilterWidget3( comboFilterWidgetList[4], comboFilterWidgetList[5],  parent= self )         
            self.shotComboBox.fillItem(comboFilterWidgetList[0] )
            self.shotWidgetItemList = comboFilterWidgetList[0]
            

            fct = lambda idx , getFocus, shotItemList = comboFilterWidgetList[0] , top_taskFilterWidget = comboFilterWidgetList[1] ,  top_assigneesFilterWidget =  comboFilterWidgetList[5] : self.refillTaskFilter( idx, getFocus, shotItemList,  top_taskFilterWidget, top_assigneesFilterWidget )
            self.shotComboBox.SIGNAL_currentIndexChanged.connect( fct )
            self.shotComboBox.SIGNAL_filterResultEmpty.connect( self.disableNoteLayout )
            

            titleGridLayout.addWidget(QtGui.QLabel("Shot/Asset" , parent= self ), idx,0)
            titleGridLayout.addWidget(self.shotComboBox , idx, 1)
            

            idx +=1



            typeDict , entriesDictList = comboFilterWidgetList[1].retrieveDict()
            myShotItem = comboFilterWidgetList[0][0]


            assignedToTxt = comboFilterWidgetList[5].widget.text()
            if not isinstance(assignedToTxt, unicode):
                assignedToTxt = unicode(assignedToTxt.toUtf8() , "utf-8" )

            availableTaskList = myShotItem["sgAvailableTaskList"]
            if not assignedToTxt == "" :

                availableTaskList= []
                for tasks in myShotItem["sgtaskDictWithAssignees"].keys() :
                    #print assignedToTxt.upper() , " ".join(comboFilterWidgetList[0][idx]["sgtaskDictWithAssignees"][tasks]).upper() 
                    if assignedToTxt.upper() in " ".join(myShotItem["sgtaskDictWithAssignees"][tasks]).upper() :
                        
                        availableTaskList.append(tasks)


            checkNumber = 0
            for idx in range(len(entriesDictList)) :

                if entriesDictList[idx]["text"] == "NoTask"  : 
                    if not checkNumber :
                        entriesDictList[idx]["checked"] = True
                    continue


                if len(availableTaskList) == 0 :
                    if "NoTask" in entriesDictList[idx]["values"] :
                        entriesDictList[idx]["checked"] = True
                    else :
                        entriesDictList[idx]["checked"] = False
                else :
                    test = False
                    for availableTask in availableTaskList :
                        if availableTask in entriesDictList[idx]["values"] :
                            test = True

                    if  entriesDictList[idx]["checked"] == True and not test :
                        entriesDictList[idx]["checked"] = False

                if  entriesDictList[idx]["checked"] == True :
                    checkNumber += 1



            self.taskFilterWidget = comboFilterWidget2( typeDict , entriesDictList, showLabel = False,  parent= self )
            self.taskFilterWidget.widget.currentIndexChanged.connect(  self.getVersion )
            if self.taskFilterWidget.widget.count() == 1 :
                self.taskFilterWidget.drawComplex = False
            self.shotList = comboFilterWidgetList[0]
            comboFilterWidgetList[1].SIGNAL_TaskcurrentIndexesChanged.connect(self.filterTasks)
            
            titleGridLayout.addWidget(QtGui.QLabel("Task" , parent= self ), idx,0)
            titleGridLayout.addWidget(self.taskFilterWidget , idx,1)


            idx +=1
            self.typeFilterWidget = comboFilterWidget2(*comboFilterWidgetList[2].retrieveDict(),showLabel = False,  parent= self )
            if self.typeFilterWidget.widget.count() == 1 :
                self.typeFilterWidget.drawComplex = False

            comboFilterWidgetList[2].SIGNAL_currentIndexesChanged.connect(self.typeFilterWidget.setMyCurrentFromIndexes)
            titleGridLayout.addWidget(QtGui.QLabel("Type" , parent= self ), idx,0)
            titleGridLayout.addWidget(self.typeFilterWidget, idx,1)



            idx +=1
            self.statusFilterWidget = comboFilterWidget2(*comboFilterWidgetList[3].retrieveDict(),showLabel = False ,  parent= self )
            if self.statusFilterWidget.widget.count() == 1 :
                self.statusFilterWidget.drawComplex = False

            comboFilterWidgetList[3].SIGNAL_currentIndexesChanged.connect(self.statusFilterWidget.setMyCurrentFromIndexes)
            titleGridLayout.addWidget(QtGui.QLabel("Status" , parent = self ), idx,0)
            titleGridLayout.addWidget(self.statusFilterWidget , idx,1)

            self.titreLabel = QtGui.QLineEdit("", parent = self)
            self.titreLabel.hide()


            self.my_versionWidgetCombo = versionWidgetCombo( parent = self )
            self.my_versionWidgetCombo.versionQtCombo.currentIndexChanged.connect( self.setTextEditOnFocus )
            layout.addWidget( self.my_versionWidgetCombo )

            # separator
            line = QtGui.QFrame( parent = self  )
            line.setFrameShape(QtGui.QFrame.HLine)
            line.setFrameShadow(QtGui.QFrame.Sunken)
            layout.addWidget(line)


        else :
            selectLabel = QtGui.QLabel("<font color:#F0F0F0><b> Select a Shot or a Note </b></font>" , parent= self )
            selectLabel.setAlignment(QtCore.Qt.AlignCenter) 
            font = selectLabel.font()
            font.setPointSize(10)
            selectLabel.setFont(font)
            layout.addWidget(selectLabel)

        
        self.statusLabel = None
        if self.data :
            if not self.multiDisplay :
                noteLinkVersion = [] 
                if self.data[0].has_key("note_links") :

                    for linksDict in self.data[0]["note_links"] :
                        if linksDict["type"] == "Version" :
                            noteLinkVersion.append( linksDict )

                if noteLinkVersion :
                    versionLayout = QtGui.QHBoxLayout()
                    versionLayout.setContentsMargins(0,0,0,0)
                    layout.addLayout(versionLayout )

                    idx = 0
                    for versionDict in noteLinkVersion :
                        taskIcon = None
                        if versionDict["sg_task"] :
                            taskIcon = comboFilterWidgetList[1].retrieveIconFromValue(versionDict["sg_task"]["name"])

                        if idx == 0 and len(noteLinkVersion)  > 1 :
                            shortCutCodeList = ["Ctrl+Space"]
                        else :
                            shortCutCodeList = ["Ctrl+Alt+Space"]

                        versionLayout.addWidget(versionWidget(versionDict , shortCutCodeList = shortCutCodeList ,taskIcon = taskIcon, parent = self) )

                        idx+=1

                    if len(noteLinkVersion) == 2 :
                        labelArrow =  QtGui.QLabel( parent= self )
                        labelArrow.setPixmap(QtGui.QPixmap(getRessources("versionArrow.png" ) ) )
                        versionLayout.insertWidget(1, labelArrow )


                if noteLinkVersion :
                    line = QtGui.QFrame( parent= self )
                    line.setFrameShape(QtGui.QFrame.HLine)
                    line.setFrameShadow(QtGui.QFrame.Sunken)
                    layout.addWidget(line)


        # Note content
        contentLayout = QtGui.QHBoxLayout()

        if self.data :
            if not self.multiDisplay :
                contentLayout.addWidget(noteContentLayout("Note", self.data[0],  noteData = None, parent = self ))
        elif  comboFilterWidgetList[0] :
            my_noteContentLayout = noteContentLayout("Note", None,  noteData = None, parent = self )
            my_noteContentLayout.SIGNAL_send_NoteContent.connect(self.todo)
            self.receiveFocusWidget = my_noteContentLayout.Qt_noteContent
            contentLayout.addWidget(my_noteContentLayout)


        if self.data :
            if not self.multiDisplay :
               
                tmpLayout = QtGui.QVBoxLayout()
                tmpLayout.setContentsMargins(0,0,0,0)

                #tmpLayout.addLayout(titleGridLayout )
                tmpLayout.addLayout(contentLayout )
                tmpLayout.addStretch()


                w = QtGui.QWidget( parent= self )
                w.setLayout( tmpLayout )

                myScrollNote = QtGui.QScrollArea( parent= self )
                myScrollNote.setHorizontalScrollBarPolicy ( QtCore.Qt.ScrollBarAlwaysOff )
                myScrollNote.setWidget(w)
                myScrollNote.setWidgetResizable(True)
                

                style = "QScrollArea {border: 0px none gray; border-radius: 0px;}"
                myScrollNote.setStyleSheet(style)

                self.myNoteBox    = QtGui.QGroupBox( str(self.data[0]["subject"] )  )
                self.myNoteBox.setCheckable(True)

                self.myNoteBox.installEventFilter(self)

                myNoteBox_layout = QtGui.QHBoxLayout()
                myNoteBox_layout.setContentsMargins(5,10,0,0)
                myNoteBox_layout.addWidget(myScrollNote)
                self.myNoteBox.setLayout(myNoteBox_layout)
                
                borderColor = "#CCCCCC"
                if self.data[0]["sg_status_list"] == "opn":
                    borderColor = "#30A6E3"
                elif self.data[0]["sg_status_list"] == "ip":
                    borderColor = "#FFC31E"

                style =  "QGroupBox  { border: 2px solid "+borderColor+";  border-radius: 5px; margin-top: 2ex; } "
                style += "QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 0 3px; color: "+borderColor+" ;} "
                style += "QGroupBox::indicator { width: 20px; height: 20px;} "
                p =  getRessources("status_"+self.data[0]["sg_status_list"]+".png" ).replace("\\","/")
                style += "QGroupBox::indicator:checked { image: url('"+ p +"'); }"
                

                self.myNoteBox.setStyleSheet(style)  
                layout.addWidget(self.myNoteBox)

        else :
            layout.addLayout(titleGridLayout)
            layout.addLayout(contentLayout)


        # Reply widget
        if self.data :
            if not self.multiDisplay :
                
                myEmptyNewReply = noteContentLayout("Reply", None,    noteData = self.data, parent = self )
                self.receiveFocusWidget = myEmptyNewReply.Qt_noteContent

                myEmptyNewReply.SIGNAL_createReply.connect( self.replyNoteSlot )
                
                replyDataList = self.data[0]["queriedReplies"]
                if replyDataList :
            
                     #[0,1,2]
                    myform = QtGui.QVBoxLayout()
                    myReplyBox = QtGui.QGroupBox()
                    

                    style = " QGroupBox  { background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 rgba(255, 255, 255, 0%), stop: 1 rgba(0, 0, 0, 33%) ); border: 0px none gray; border-radius: 0px}"

                    myReplyBox.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
                    myReplyBox.setStyleSheet(style)
                    myReplyBox.setLayout(myform)
                    
                    scroll = QtGui.QScrollArea( parent= self )

                    scroll.setWidget(myReplyBox)
                    scroll.setWidgetResizable(True)


                    style = "QScrollArea {border: 0px none gray; border-radius: 0px;}"
                    scroll.setStyleSheet(style)
                    scroll.setHorizontalScrollBarPolicy ( QtCore.Qt.ScrollBarAlwaysOff )
                    moveScrollBarToBottom = lambda min, max : scroll.verticalScrollBar().setValue(max)
                    scroll.verticalScrollBar().rangeChanged.connect(moveScrollBarToBottom) 


                    for replyData in  replyDataList :
                        myform.addWidget(noteContentLayout("Reply", replyData, noteData = None, parent = self ))
                        line = QtGui.QFrame( parent = self )
                        line.setFrameShape(QtGui.QFrame.HLine)
                        line.setFrameShadow(QtGui.QFrame.Sunken)

                        myform.addWidget(line)
                    
                    

                    replyBox = QtGui.QGroupBox(" Replies " )
                    replyBox_layout = QtGui.QHBoxLayout()
                    replyBox_layout.setContentsMargins(0,10,0,0)
                    replyBox.setLayout(replyBox_layout)
                    replyBox_layout.addWidget( scroll)

                    style =  "QGroupBox  { border: 2px solid gray;  border-radius: 5px; margin-top: 2ex; } "
                    style += "QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 0 3px; }"
                    replyBox.setStyleSheet(style)

                    layout.addWidget(replyBox)
                    
                layout.addWidget(myEmptyNewReply)
            
            else :

         

                myEmptyNewReply = noteContentLayout("Reply", None,  noteData = self.data, parent = self  )
                myEmptyNewReply.SIGNAL_createMultiReply.connect( self.multiReplyNoteSlot )
                
                layout.addWidget(myEmptyNewReply)


    ## ## @decorateur_try_except
    def refillTaskFilter(self, idx, getFocus, shotItemList, top_taskFilterWidget, top_assigneesFilterWidget  ):
       
        self.getFocus = getFocus

        availableTaskList = shotItemList[idx]["sgAvailableTaskList"]
        
        assignedToTxt = top_assigneesFilterWidget.widget.text()
        if not isinstance(assignedToTxt, unicode):
            assignedToTxt = unicode(assignedToTxt.toUtf8() , "utf-8" )

        if not assignedToTxt == "" :

            availableTaskList= []
            for tasks in shotItemList[idx]["sgtaskDictWithAssignees"].keys() :
                #print assignedToTxt.upper() , " ".join( shotItemList[idx]["sgtaskDictWithAssignees"][tasks] ).upper() 
                if assignedToTxt.upper() in " ".join(shotItemList[idx]["sgtaskDictWithAssignees"][tasks]).upper() :
                    
                    availableTaskList.append(tasks)
                #print assignedToTxt.upper()
        self.taskFilterWidget.setMyCurrentFromIndexes( top_taskFilterWidget.getTaskCheckedIndexes() ,  availableTaskList  )


        self.getVersion(0)

    ## ## @decorateur_try_except
    def eventFilter(self, obj, event):
 
        if obj == self.myNoteBox :
            if event.type() in [QtCore.QEvent.MouseButtonDblClick, QtCore.QEvent.MouseButtonPress, QtCore.QEvent.MouseButtonRelease ] :
 
                return True
            else :
                return False
        else :
            return QtGui.QWidget.eventFilter(self, obj, event);
     
    ## ## @decorateur_try_except
    def setComboTasks(self, indexList ) :
        
        self.taskFilterWidget.setMyCurrentFromIndexes

        self.taskFilterWidget.setMyCurrentFromIndexes( indexList )
        #self.queue

    ## ## @decorateur_try_except   
    def todo(self, obj) :
        bodyKey = {'content' : obj[0]['content']}

        # get ComboFilter data
        taskList = self.taskFilterWidget.getfilterList()

        if "NoTask" in taskList :  
            taskList = []

        plog("In\n")
        plog(str(taskList) + "\n")
        shot_SgData  = self.shotWidgetItemList[self.shotComboBox.currentIndex()]

        versionData = self.my_versionWidgetCombo.getCurrentIndexVersionData()
        typeNote  = self.typeFilterWidget.getfilterList()
        
        typeKey = {}
        if not "NoType" in typeNote :
            typeKey = { "sg_note_type":  typeNote[0] }
        

        statusNote = self.statusFilterWidget.getfilterList()
        statusKey = { "sg_status_list" : statusNote[0] }


        linksKey = { "note_links" : [ ] }

        
        if versionData : #
            linksKey["note_links"].append( {'type': 'Version', 'id' : versionData["id"]  } )

        if not taskList :
            linksKey["note_links"].append( {'type': shot_SgData['type'], 'id' : shot_SgData['id']} )            


        sujectContent = self.titreLabel.text()
        if sujectContent :
            if not isinstance(sujectContent, unicode):
                sujectContent = unicode ( sujectContent.toUtf8(), "utf-8" )
                noteDict.update( {"subject": sujectContent }  )

        noteDict = {}
        noteDict.update( bodyKey)
        noteDict.update( typeKey)
        noteDict.update( linksKey)
        noteDict.update( statusKey)

        # {'content': u'ma superbe note', 'note_links': [{'type': 'Shot', 'id': 2527}, {'type': 'Version', 'id': 17127}], 'sg_note_type': 'To-do', 'sg_status_list': 'opn'}
        
        plog(str(taskList) + "off\n")

        self.SIGNAL_send_NoteContent.emit([noteDict,  obj[0]["uploads"], shot_SgData, taskList ] )

    ## ## @decorateur_try_except
    def updateTaskFilterWidget(self, taskListName ):
        if self.taskFilterWidget : 
            if taskListName :
                self.taskFilterWidget.widget.blockSignals(True)
                self.taskFilterWidget.setFromValue(taskListName[0])
                self.taskFilterWidget.widget.blockSignals(False)
            self.getVersion(0)

    ## ## @decorateur_try_except
    def replyNoteSlot(self, obj) :

        self.SIGNAL_createReply.emit(obj)
                
    ## ## @decorateur_try_except
    def multiReplyNoteSlot(self, obj) :

        self.SIGNAL_createMultiReply.emit(obj)


    ## ## @decorateur_try_except
    def getVersion(self, idx):


        shotIdx = self.shotComboBox.currentIndex()
        if self.my_versionWidgetCombo :
            self.my_versionWidgetCombo.setOnLoading()

        # flushSgtkQueue
        while not self.sgtkQueue.empty():
            try:
                self.sgtkQueue.get(False)
            except Empty:
                continue
            self.sgtkQueue.task_done()
        self.sgtkQueue.put([-5, u"getExecutable",   [self.shotWidgetItemList[shotIdx]["id"], self.taskFilterWidget.retrieveDictFromSelection(), str(self.taskFilterWidget.widget.currentText()), self.shotWidgetItemList[shotIdx]["code"], self.shotWidgetItemList[shotIdx]["type"]  ] , None ] ) 
        
        self.queue.put([0, u"getVersion",  [ [self.shotWidgetItemList[shotIdx]["id"], self.shotWidgetItemList[shotIdx]["type"] ]  , self.taskFilterWidget.retrieveDictFromSelection(), [self.shotComboBox.currentText(), self.taskFilterWidget.widget.currentText() ] ] , None ] )


        
        if self.receiveFocusWidget :
            if self.getFocus :
                self.receiveFocusWidget.setFocus()
    
    def setTextEditOnFocus(self, idx) :
        if self.receiveFocusWidget :
            if self.getFocus :
                self.receiveFocusWidget.setFocus()

    ## ## @decorateur_try_except
    def fill_versionWidgetCombo(self, obj) :

        if self.my_versionWidgetCombo :
            if obj[1][0] == self.shotComboBox.currentText() and obj[1][1] == self.taskFilterWidget.widget.currentText() :
                self.my_versionWidgetCombo.updateWidget(obj)

