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



import utils
from utils import *

import ui_widget
from ui_widget import *

import treeWidgetItem
from treeWidgetItem import *

import imageDisplay
import imageScribble
import imagePicker


class GrowingTextEdit(QtGui.QTextEdit):

    def __init__(self, *args, **kwargs):
        super(GrowingTextEdit, self).__init__(*args, **kwargs)  
        self.document().contentsChanged.connect(self.sizeChange)

        self.heightMin = 0
        self.heightMax = 65000

    def sizeChange(self):
        docHeight = self.document().size().height()
        if self.heightMin <= docHeight <= self.heightMax:
            self.setMinimumHeight(docHeight)

class noteContentLayout(QtGui.QWidget) :
    SIGNAL_createReply      = _signal(object)
    SIGNAL_createMultiReply = _signal(object)
    SIGNAL_send_NoteContent = _signal(object)

    @decorateur_try_except
    def __init__(self, dataType , data , noteData = None, parent= None) :
        super(noteContentLayout, self).__init__(parent ) 
        self.data = data
        self.noteData = noteData # is a list


        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        layoutContainer = QtGui.QHBoxLayout()
        titleGridLayout = QtGui.QGridLayout()
        layoutContainer.addLayout(titleGridLayout)
        titleGridLayout.setColumnStretch(1,10)
        titleGridLayout.setColumnStretch(2,40)

        # author
        authorTxt = "unknown" 

        self.attachmentLayout = QtGui.QHBoxLayout()
        self.Qt_noteContent = QtGui.QTextEdit()


        if self.data :

            try :
                self.Qt_noteContent.setPlainText( QtCore.QString.fromUtf8( self.data["content"]) )
            except :
                self.Qt_noteContent.setPlainText(self.data["content"] )

            if dataType == "Reply" :

                
                authorHtmlTxt = "<font size=2 color=#BBBBBB>Author : "+self.data["user"]['name']+"</font><br>"
                dateHtmlTxt   = "<font size=2 color=#BBBBBB>Date : "+self.data["created_at"].strftime('%Y-%m-%d %H:%M:%S')+"</font>"
                labelText = QtGui.QLabel(authorHtmlTxt+dateHtmlTxt)                
                
                contentLabel = QtGui.QLabel(self.data["content"])
                contentLabel.setAlignment(QtCore.Qt.AlignTop)
                contentLabel.setStyleSheet("QLabel { color : #F0F0F0 }")
                contentLabel.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
                
                titleGridLayout.setHorizontalSpacing(20)
                titleGridLayout.addWidget(labelText, 0,0, QtCore.Qt.AlignTop )
                titleGridLayout.addWidget( contentLabel, 0, 1 )
                layout.addLayout(layoutContainer)
                layout.addLayout(self.attachmentLayout)
                titleGridLayout.setContentsMargins(0,0,0,0)
                layout.setContentsMargins(0,0,0,0)

            else :
                authorHtmlTxt = "<font color=#BBBBBB>Author : "+ self.data["user"]['name'] + "</font><br>"
                dateHtmlTxt = "<font color=#BBBBBB>Date : <b>"+self.data["created_at"].strftime('%Y-%m-%d %H:%M:%S')+"</font></b><br>"
                labelText = QtGui.QLabel(authorHtmlTxt+dateHtmlTxt)
                titleGridLayout.addWidget(labelText, 0,0, QtCore.Qt.AlignTop)

                contentLabel = QtGui.QLabel(self.data["content"])
                contentLabel.setAlignment(QtCore.Qt.AlignTop)

                contentLabel.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

                layout.addLayout(layoutContainer)
                layout.addWidget(contentLabel)
                layout.addLayout(self.attachmentLayout)

                contentLabel.setStyleSheet("QLabel { color : #F0F0F0 ; }")
                titleGridLayout.setContentsMargins(0,0,0,0)
                layout.setContentsMargins(0,0,0,0)


        

        if not self.data : 
            if dataType == "Reply" :  
                if len(self.noteData)>1 :
                    self.Qt_noteContent.setText(u"Type a reply for all the selected notes") 
                else :
                    self.Qt_noteContent.setText(u"Type a reply")


            elif dataType == "Note":
                self.Qt_noteContent.setText(u"Type a note")

            layout.setContentsMargins(0,0,0,0)

            layout.addLayout(layoutContainer)
            layout.addWidget(self.Qt_noteContent)
            layout.addLayout(self.attachmentLayout)



        if self.data :
            for attachementFile in self.data["queriedAttachement"] :
                labelImage = PicButton(attachementFile["fileOnDisk"], overImageName = "magnifier.png")

                labelImage.SIGNAL_imageClicked.connect( self.showImageDisplay )

                self.attachmentLayout.addWidget(labelImage)
        else :
            attachButton = QtGui.QPushButton()
            attachmentPixmap = QtGui.QPixmap(getRessources("note_attachment.png"))
            attachementScaled = attachmentPixmap.scaled ( 32, 32, QtCore.Qt.KeepAspectRatio)
            attachButton.setIcon(QtGui.QIcon(attachementScaled))
            attachButton.clicked.connect(self.addAttachment)


            screenShotButton = QtGui.QPushButton()
            attachmentPixmap = QtGui.QPixmap(getRessources("note_screenShot.png"))
            attachementScaled = attachmentPixmap.scaled ( 32, 32, QtCore.Qt.KeepAspectRatio)
            screenShotButton.setIcon(QtGui.QIcon(attachementScaled))
            screenShotButton.clicked.connect(self.addScreenShot)

            self.attachmentLayout.addWidget(screenShotButton)
            self.attachmentLayout.addWidget(attachButton)

            replyButton = None
            if dataType == "Reply" :   
                replyButton = QtGui.QPushButton("Reply")
                replyButton.clicked.connect(self.replyNoteSlot)

                self.statusLabel = QtGui.QComboBox()
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


            elif dataType == "Note":
                replyButton = QtGui.QPushButton("Create Note")
                replyButton.clicked.connect(self.createNoteSlot)
            
            layout.addWidget(replyButton)

        self.attachmentLayout.addStretch()

        style = "background-color: red;"

    @decorateur_try_except
    def editNoteContent(self, mouseEvent ) :
        print "edit me"
    @decorateur_try_except
    def updateNodeDataStatus(self, comboIdx) :

        if self.statusLabel.currentIndex() == 0 :
            self.noteData[0]["new_sg_status_list"] = "opn"
        elif self.statusLabel.currentIndex() == 1 :
            self.noteData[0]["new_sg_status_list"] = "clsd"
        elif self.statusLabel.currentIndex() == 2 :
            self.noteData[0]["new_sg_status_list"] = "ip"
    

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


    @decorateur_try_except
    def showImageDisplay(self, imageFileName ) :

        imV = imageDisplay.ImageViewer(self)
        imV.setImage(imageFileName)
        imV.show()

    @decorateur_try_except
    def editImageDisplay(self, imageFileName ) :


        window = imageScribble.MainWindow( self )
        window.SIGNAL_imageUpdate.connect(self.refresh_attachementLayout)
        

        window.setWindowModality(QtCore.Qt.ApplicationModal)
        window.openImage(imageFileName)
        window.show()


    def refresh_attachementLayout(self) :
        for itemIdx in range(self.attachmentLayout.count() ):
            widget = self.attachmentLayout.itemAt(itemIdx).widget()
            if hasattr(widget, "update") :
                widget.update()











class noteLayoutWidget(QtGui.QWidget) :

    SIGNAL_createReply = _signal(object)
    SIGNAL_createMultiReply = _signal(object)
    SIGNAL_send_NoteContent = _signal(object)

    @decorateur_try_except
    def __init__(self, data, comboFilterWidgetList = None, threadQueue = None, color = False, parent= None) : 

        super(noteLayoutWidget, self).__init__(parent ) 
        self.taskFilterWidget = None
        self.shotWidgetItemList = None
        self.my_versionWidgetCombo = None
        self.queue = None
        self.myNoteBox = None

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
        
        # titre
        titreLabelText = QtGui.QLabel("Subject : ")
        titreLabelText.setMaximumWidth(50)

        self.titreLabel = None
        if self.data :
            if not self.multiDisplay :
                self.titreLabel = QtGui.QLabel("<b>"+ str(self.data[0]["subject"]) +"</b>")
                titleGridLayout.addWidget(titreLabelText  ,0,0)
                titleGridLayout.addWidget(self.titreLabel ,0,1)
                # status 
                statusLabelText = QtGui.QLabel("Status : ")
                statusLabelText.setMaximumWidth(50)
                titleGridLayout.addWidget(statusLabelText, 1,0)
        

        elif  comboFilterWidgetList[0] :

            self.queue = threadQueue

            idx = 0
            self.shotComboBox = QtGui.QComboBox()
            for shotItem in comboFilterWidgetList[0] :
                self.shotComboBox.addItem( shotItem["code"])

            self.shotWidgetItemList = comboFilterWidgetList[0]
            self.shotComboBox.currentIndexChanged.connect(self.getVersion)


            titleGridLayout.addWidget(QtGui.QLabel("Shot"), idx,0)
            titleGridLayout.addWidget(self.shotComboBox , idx, 1)
            
            if len(comboFilterWidgetList[0]) ==1:
                self.shotComboBox.setEnabled(False)
            

            idx +=1
            self.taskFilterWidget = comboFilterWidget2( *comboFilterWidgetList[1].retrieveDict(), showLabel = False )
            self.taskFilterWidget.widget.currentIndexChanged.connect(  self.getVersion)
            comboFilterWidgetList[1].SIGNAL_currentIndexesChanged.connect(self.taskFilterWidget.setMyCurrentFromIndexes)
            titleGridLayout.addWidget(QtGui.QLabel("Task"), idx,0)
            titleGridLayout.addWidget(self.taskFilterWidget , idx,1)


            idx +=1
            self.typeFilterWidget = comboFilterWidget2(*comboFilterWidgetList[2].retrieveDict(),showLabel = False )
            comboFilterWidgetList[2].SIGNAL_currentIndexesChanged.connect(self.typeFilterWidget.setMyCurrentFromIndexes)
            titleGridLayout.addWidget(QtGui.QLabel("Type"), idx,0)
            titleGridLayout.addWidget(self.typeFilterWidget, idx,1)



            idx +=1
            self.statusFilterWidget = comboFilterWidget2(*comboFilterWidgetList[3].retrieveDict(),showLabel = False )
            comboFilterWidgetList[3].SIGNAL_currentIndexesChanged.connect(self.statusFilterWidget.setMyCurrentFromIndexes)
            titleGridLayout.addWidget(QtGui.QLabel("Status"), idx,0)
            titleGridLayout.addWidget(self.statusFilterWidget , idx,1)

            """
            idx +=1
            self.titreLabel = QtGui.QLineEdit("")
            titleGridLayout.addWidget(titreLabelText  ,idx,0)
            titleGridLayout.addWidget(self.titreLabel ,idx,1)
            """

            self.my_versionWidgetCombo = versionWidgetCombo()
            layout.addWidget( self.my_versionWidgetCombo )

            # separator
            line = QtGui.QFrame()
            line.setFrameShape(QtGui.QFrame.HLine)
            line.setFrameShadow(QtGui.QFrame.Sunken)
            layout.addWidget(line)


        else :
            selectLabel = QtGui.QLabel("<font color:#F0F0F0><b> Select a Shot </b></font>")
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
                    for versionDict in noteLinkVersion :
                        versionLayout.addWidget(versionWidget(versionDict) )
                    if len(noteLinkVersion) == 2 :
                        labelArrow =  QtGui.QLabel()
                        labelArrow.setPixmap(QtGui.QPixmap(getRessources("versionArrow.png" ) ) )
                        versionLayout.insertWidget(1, labelArrow )


                if noteLinkVersion :
                    line = QtGui.QFrame()
                    line.setFrameShape(QtGui.QFrame.HLine)
                    line.setFrameShadow(QtGui.QFrame.Sunken)
                    layout.addWidget(line)

                self.statusLabel = QtGui.QLabel()
                self.statusLabel.setText('<img src="'+getRessources("status_"+self.data[0]["sg_status_list"] +".png")+'" />') 
        
                titleGridLayout.addWidget(self.statusLabel, 1,1)


        # Note content
        contentLayout = QtGui.QHBoxLayout()

        if self.data :
            if not self.multiDisplay :
                contentLayout.addWidget(noteContentLayout("Note", self.data[0] ))
        elif  comboFilterWidgetList[0] :
            my_noteContentLayout = noteContentLayout("Note", None)
            my_noteContentLayout.SIGNAL_send_NoteContent.connect(self.todo)

            contentLayout.addWidget(my_noteContentLayout)


        if self.data :
            if not self.multiDisplay :
               
                tmpLayout = QtGui.QVBoxLayout()
                tmpLayout.setContentsMargins(0,0,0,0)

                #tmpLayout.addLayout(titleGridLayout )
                tmpLayout.addLayout(contentLayout )
                tmpLayout.addStretch()


                w = QtGui.QWidget()
                w.setLayout( tmpLayout )

                myScrollNote = QtGui.QScrollArea()
                myScrollNote.setWidget(w)
                myScrollNote.setWidgetResizable(True)
                

                style = "QScrollArea {border: 0px none gray; border-radius: 0px;}"
                myScrollNote.setStyleSheet(style)

                self.myNoteBox    = QtGui.QGroupBox( str(self.data[0]["subject"])  )
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
                
            
                replyDataList = self.data[0]["queriedReplies"] #[0,1,2]
                myform = QtGui.QVBoxLayout()
                myReplyBox = QtGui.QGroupBox()
                

                style = " QGroupBox  { background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 rgba(255, 255, 255, 0%), stop: 1 rgba(0, 0, 0, 33%) ); border: 0px none gray; border-radius: 0px}"

                myReplyBox.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
                myReplyBox.setStyleSheet(style)
                myReplyBox.setLayout(myform)
                
                scroll = QtGui.QScrollArea()

                scroll.setWidget(myReplyBox)
                scroll.setWidgetResizable(True)


                style = "QScrollArea {border: 0px none gray; border-radius: 0px;}"
                scroll.setStyleSheet(style)
                moveScrollBarToBottom = lambda min, max : scroll.verticalScrollBar().setValue(max)
                scroll.verticalScrollBar().rangeChanged.connect(moveScrollBarToBottom) 
                


                myEmptyNewReply = noteContentLayout("Reply", None,    self.data    , None)
                myEmptyNewReply.SIGNAL_createReply.connect( self.replyNoteSlot )

                if replyDataList :
                    for replyData in  replyDataList :
                        myform.addWidget(noteContentLayout("Reply", replyData, None))
                        line = QtGui.QFrame()
                        line.setFrameShape(QtGui.QFrame.HLine)
                        line.setFrameShadow(QtGui.QFrame.Sunken)

                        myform.addWidget(line)
                    
                    

                    replyBox = QtGui.QGroupBox(" Replies ")
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

         

                myEmptyNewReply = noteContentLayout("Reply", None,  self.data   , None)
                myEmptyNewReply.SIGNAL_createMultiReply.connect( self.multiReplyNoteSlot )
                
                layout.addWidget(myEmptyNewReply)

    #def moveScrollBarToBottom(self, min, max):


    def eventFilter(self, obj, event):
 
        if obj == self.myNoteBox :
            if event.type() in [QtCore.QEvent.MouseButtonDblClick, QtCore.QEvent.MouseButtonPress, QtCore.QEvent.MouseButtonRelease ] :
                print "click"
                return True
            else :
                return False
        else :
            return QtGui.QWidget.eventFilter(self, obj, event);
     
 


    def setComboTasks(self, indexList ) :
        
        self.taskFilterWidget.setMyCurrentFromIndexes( indexList )
        #self.queue


    @decorateur_try_except    
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
            linksKey["note_links"].append( {'type': 'Shot', 'id' : shot_SgData['id']} )            


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

    @decorateur_try_except
    def updateTaskFilterWidget(self, taskListName ):
        if self.taskFilterWidget : 
            if taskListName :
                self.taskFilterWidget.widget.blockSignals(True)
                self.taskFilterWidget.setFromValue(taskListName[0])
                self.taskFilterWidget.widget.blockSignals(False)
            self.getVersion(0)


    @decorateur_try_except
    def replyNoteSlot(self, obj) :

        self.SIGNAL_createReply.emit(obj)
                
    @decorateur_try_except
    def multiReplyNoteSlot(self, obj) :

        self.SIGNAL_createMultiReply.emit(obj)



    @decorateur_try_except
    def getVersion(self, idx):


        shotIdx = self.shotComboBox.currentIndex()
        if self.my_versionWidgetCombo :
            self.my_versionWidgetCombo.setOnLoading()


        self.queue.put([-5, u"getExecutable",   [self.shotWidgetItemList[shotIdx]["id"], self.taskFilterWidget.retrieveDictFromSelection(), str(self.taskFilterWidget.widget.currentText()), self.shotWidgetItemList[shotIdx]["code"] ] , None ] ) 
        self.queue.put([0, u"getVersion",  [self.shotWidgetItemList[shotIdx]["id"], self.taskFilterWidget.retrieveDictFromSelection(), [self.shotComboBox.currentText(), self.taskFilterWidget.widget.currentText() ] ] , None ] )





    @decorateur_try_except
    def fill_versionWidgetCombo(self, obj) :


        if self.my_versionWidgetCombo :
            if obj[1][0] == self.shotComboBox.currentText() and obj[1][1] == self.taskFilterWidget.widget.currentText() :
                self.my_versionWidgetCombo.updateWidget(obj)

