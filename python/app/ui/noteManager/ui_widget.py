#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
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


class my_textEdit(QtGui.QTextEdit) :
    SIGNAL_return = _signal()    
    def __init__(self, text, editable = True, parent = None) :


        QtGui.QTextEdit.__init__(self, text, parent)
        if editable :
            self.setReadOnly(True);
            self.setFrameStyle(QtGui.QFrame.NoFrame);
            pal = QtGui.QPalette()
            pal.setColor(QtGui.QPalette.Base, QtCore.Qt.transparent);
            self.setPalette(pal)
         
            self.setLineWrapMode(QtGui.QTextEdit.WidgetWidth);
            self.setWordWrapMode(QtGui.QTextOption.WrapAnywhere);

            self.document().documentLayout().documentSizeChanged.connect(self.adjustMinimumSize) 
        else :
            action = QtGui.QAction( self)
            action.setShortcuts( ["Ctrl+Enter","Ctrl+Return"] )
            action.triggered.connect(self.actionReturn)
            self.addAction(action)

            self.setToolTip("Ctrl+Enter to create without pushing button")
            #print "-> do"
            #self.connect (action, SIGNAL (triggered (bool)), this, SLOT (emitText());
       # print "do -> DONE"
    def actionReturn(self ) :
        if self.hasFocus():
            self.SIGNAL_return.emit()

    def adjustMinimumSize(self, size) :
    
        self.setMinimumHeight(size.height() + 2 * self.frameWidth())
    


class toggleBtn(QtGui.QPushButton) :
    def __init__(self, label, parent = None):
        QtGui.QPushButton.__init__(self,  parent)
        self.setIcon(QtGui.QIcon(getRessources("refreshUI.png") ))
        self.setFlat(True);
        self.setIconSize(QtCore.QSize(16,16));

        style = 'QPushButton:hover{border: 1px solid rgb(48,226,227)}'
        self.setStyleSheet("QPushButton{outline: none;}"+style);
        
class loadingWidget(QtGui.QWidget) :
    ## @decorateur_try_except
    def __init__(self, intSize = 50, parent = None):
        QtGui.QWidget.__init__(self, parent)
         
        # Load the file into a QMovie

        self.movie = QtGui.QMovie(getRessources( "preloader_%i.gif"%intSize), QtCore.QByteArray(), self)
         
        size = self.movie.scaledSize()
        self.setGeometry(intSize, intSize, size.width(), size.height())

         
        self.movie_screen = QtGui.QLabel( parent = self)
        # Make label fit the gif
        #self.movie_screen.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.movie_screen.setAlignment(QtCore.Qt.AlignLeft)
         
        # Create the layout
        main_layout = QtGui.QVBoxLayout()
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.addWidget(self.movie_screen)
         
        self.setLayout(main_layout)
         
        # Add the QMovie object to the label
        self.movie.setCacheMode(QtGui.QMovie.CacheAll)
        self.movie.setSpeed(100)
        self.movie_screen.setMovie(self.movie)
        self.movie.start() 


class versionWidgetCombo(QtGui.QWidget) :
    ## @decorateur_try_except
    def __init__(self, parent = None):
        super(versionWidgetCombo, self).__init__(parent)
        
        self.versionDatas = []
        self.pathToMovie = None
       
        self.masterLayout = QtGui.QVBoxLayout()
        self.masterLayout.setContentsMargins(0,0,0,0)


        self.setLayout(self.masterLayout)


        self.layout = QtGui.QHBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)

        titleLabel = QtGui.QLabel("Create Note" ,  parent = self )
        #titleLabel.setStyleSheet("QLabel { background-color : red; color : blue; }");
        font = QtGui.QFont("" , 10 , QtGui.QFont.Bold )
        titleLabel.setFont(font)

        titleLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.masterLayout.addWidget(titleLabel)
        self.masterLayout.addLayout(self.layout)


        self.pic= loadingWidget(  parent = self ) 
        # ####self.pic.setMaximumWidth(50)

        

        infoLayout = QtGui.QVBoxLayout()
        infoLayout.setAlignment(QtCore.Qt.AlignTop )
        self.layout.addLayout( infoLayout)
        self.layout.addStretch()
        self.layout.addWidget(self.pic,QtCore.Qt.AlignLeft)

       
        self.versionQtCombo = QtGui.QComboBox( parent = self )
        self.nameQt = QtGui.QLabel("", parent = self)
        self.userQt = QtGui.QLabel("", parent = self)
        self.dateQt = QtGui.QLabel("", parent = self )
        self.taskQt =  QtGui.QLabel("", parent = self )

        comboLayout = QtGui.QHBoxLayout()
        comboLayout.setContentsMargins(0,0,0,0)
        comboLayout.addWidget( QtGui.QLabel("Link to version : " , parent = self ))
        comboLayout.addWidget( self.versionQtCombo,QtCore.Qt.AlignLeft )

        infoLayout.addLayout( comboLayout )

        infoLayout.addWidget( self.nameQt )    
        infoLayout.addWidget( self.userQt ) 
        infoLayout.addWidget( self.dateQt )   
        infoLayout.addWidget( self.taskQt )
        infoLayout.addSpacing( 100)

        #infoLayout.addStretch()
        infoLayout.setContentsMargins(0,0,0,0)
        infoLayout.setSpacing(0)

        self.layout.addSpacing(5)


        self.versionQtCombo.currentIndexChanged.connect(self.setVersionValue)



    ## @decorateur_try_except
    def setVersionValue(self, idx) :


        if idx == 0 :
            self.nameQt.setText("Name : None" )
            self.userQt.setText("User : None" )
            self.dateQt.setText("Created : None" )
            self.taskQt.setText("Task : None")

            self.pic.setParent(None)
            self.pic = PicButton( getRessources( "empty.png"),50,50, overImageName = None)
            #self.pic.setMaximumWidth(2000)
            self.layout.addWidget(self.pic,QtCore.Qt.AlignLeft )
        else :
            versionData = self.versionDatas[idx-1]

            versionDataName = versionData["user"]
            if not versionDataName :
                versionDataName = "unknow"
            else :
                versionDataName = versionData["user"]["name"]


            versionString = versionData["code"] 
            splits = re.findall(r' v\d+', versionData["code"] )
            if splits :
                versionString = splits[-1]
            
            self.nameQt.setText("Name : %s"%versionData["code"].replace(versionString, "<b>%s</b>"%versionString) )    
            self.userQt.setText("%s : <b>%s</b"%("User"  ,  versionDataName ) )  
            self.dateQt.setText("%s : <b>%s</b"%("Created", versionData["created_at"]) ) 
            versionText = "None"
            if versionData['sg_task']  :
                versionText =versionData['sg_task']["name"]
            self.taskQt.setText("%s : <b>%s</b"%("Task", versionText ) ) 
            self.pic.setParent(None)
            self.pic = PicButton( versionData["downloadedImage"] ,200,200, overImageName = "play.png",  doStart=True)
            

            self.layout.addWidget(self.pic,QtCore.Qt.AlignLeft )
            self.pathToMovie = versionData["sg_path_to_movie"]
            self.pic.SIGNAL_imageClicked.connect(self.play_pathToMovie)


    ## @decorateur_try_except
    def play_pathToMovie(self, file):
        
        if self.pathToMovie :
            convertPath =   OS_convertPath( self.pathToMovie )
            osSystem( convertPath )

    ## @decorateur_try_except
    def setOnLoading(self):
        if self.pic :
            self.pic.setParent(None)
        self.pic = loadingWidget( parent = self )
        self.pic.setMaximumWidth(50)
        self.layout.addWidget(self.pic,QtCore.Qt.AlignLeft )
    
    ## @decorateur_try_except
    def updateWidget(self, datas ):
        self.versionDatas= datas[0]


        self.pic.setParent(None)


        self.versionQtCombo.blockSignals(True)
        self.versionQtCombo.clear()

        self.versionQtCombo.addItem(str("None") ) 
        versionData = None
        idx = 0
        for versionData in self.versionDatas :

            versionDataName = versionData["user"]
            if not versionDataName :
                versionDataName = "unknow"
            else :
                versionDataName = versionData["user"]["name"]
            versionString = versionData["code"] 
            splits = re.findall(r' v\d+', versionData["code"] )
            if splits :
                versionString = splits[-1]

            if idx == 0 :
                self.versionQtCombo.addItem(str(versionString) + " ( Last )" )  
            else :
                self.versionQtCombo.addItem(str(versionString) )
            idx += 1

        if len(self.versionDatas) :
            self.versionQtCombo.setEnabled(True)
            self.versionQtCombo.setCurrentIndex(1)
            self.setVersionValue(1)
        else :
            self.versionQtCombo.setEnabled(False)
            self.versionQtCombo.setCurrentIndex(0)
            self.setVersionValue(0)

        
        self.versionQtCombo.blockSignals(False)


    def getCurrentIndexVersionData(self):
        comboIdx = self.versionQtCombo.currentIndex()
        if comboIdx == 0 :
            return None
        else :
            return self.versionDatas[comboIdx-1]
         


class versionWidget(QtGui.QWidget) :

    ## @decorateur_try_except
    def __init__(self, versionData, shortCutCodeList = None ,taskIcon = None, parent=None):
        super(versionWidget, self).__init__(parent)
        self.pathToMovie = versionData["sg_path_to_movie"]
        if not self.pathToMovie :
            print "sg_path_to_movie is empty", versionData

        testLayout = QtGui.QVBoxLayout() 
        testLayout.setContentsMargins(0,0,0,0)
        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        testLayout.addLayout(layout) 
        self.setLayout(testLayout)


        pic =   PicButton(versionData["downloadedImage"],200,200, overImageName = "play.png",  doStart=True ,  parent = self )
        pic.setMaximumWidth(200)
        pic.SIGNAL_imageClicked.connect(self.play_pathToMovie)


        titleLay = QtGui.QHBoxLayout()
        titleLay.addStretch()
        titleLay.setContentsMargins(0,0,0,0)

        if versionData.has_key("Title") :
            titleLabel = QtGui.QLabel(versionData["Title"] ,  parent = self )
            titleLabel.setAlignment(QtCore.Qt.AlignCenter)
            if taskIcon :
                taskIconLabel = QtGui.QLabel()
                taskIconLabel.setPixmap( QtGui.QPixmap(getRessources(taskIcon)).scaled( 16,16, QtCore.Qt.KeepAspectRatio)    )
                titleLay.addWidget(taskIconLabel)    
            titleLay.addWidget(titleLabel)
            testLayout.addLayout(titleLay)
        titleLay.addStretch()
        pic.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(pic)




        versionDataName = versionData["user"]
        if not versionDataName :
            versionDataName = "unknow"
        else :
            versionDataName = versionData["user"]["name"]


        versionString = versionData["code"] 
        splits = re.findall(r' v\d+', versionData["code"] )
        if splits :
            versionString = splits[-1]

        txt = versionString +"\n"
        txt+= "name : %s\n"%versionData["code"]
        txt+= "%s : %s\n"%("user"  ,  versionDataName )
        txt+= "%s : %s\n"%("created", versionData["created_at"])
        if versionData["sg_task"] :
            txt+= "%s : %s\n"%("task", versionData["sg_task"]["name"])
        txt+= "\n  - Shortcut -\n" 
        txt+= "%s : %s"%("Play :", str( shortCutCodeList ))
        self.setToolTip(txt)

        if shortCutCodeList :
            action = QtGui.QAction( self)
            action.setShortcuts( shortCutCodeList )
            action.triggered.connect(self.play_pathToMovie)
            self.addAction(action)



    ## @decorateur_try_except
    def play_pathToMovie(self, file = None):
        if self.pathToMovie :
            convertPath =   OS_convertPath( self.pathToMovie )
            osSystem( convertPath )


class PicButton(QtGui.QLabel):
    SIGNAL_imageClicked = _signal(object)

    ## @decorateur_try_except
    def __init__(self, imageFileName, x = 100, y = 100 , overImageName = "pencil.png" , doStart=False , parent=None):
        super(PicButton, self).__init__(parent)
        self.do_on_hover  = True 
        self.isNullPixmap = True 
        if overImageName == None :
            self.do_on_hover = False

        if not overImageName :
            overImageName = "empty.png"
        self.overImagePath = getRessources(overImageName)
        self.resultPix = None
        self.x = x 
        self.y = y
        self.setMaximumWidth(x)

        self.fileOnDisk =  imageFileName
        self.attachmentPixmap = QtGui.QPixmap(imageFileName)
        if self.attachmentPixmap.isNull() :
            if doStart :
                self.attachmentPixmap = QtGui.QPixmap(getRessources("version.png") ).scaled ( 100,100, QtCore.Qt.KeepAspectRatio)
                self.setMaximumWidth(100)
                self.setPixmap(self.attachmentPixmap)
                self.isNullPixmap = False
                self.do_on_hover  = True 
                self.createOverlayPixmap(alpha = 0)
                self.setAlignment(QtCore.Qt.AlignLeft)
       
            else :
                self.attachmentPixmap = QtGui.QPixmap(getRessources("fileError.png") )
                self.setPixmap(self.attachmentPixmap)
                self.isNullPixmap = True
        else :

            self.attachmentPixmap = self.attachmentPixmap.scaled ( self.x, self.y, QtCore.Qt.KeepAspectRatio)
            self.setPixmap(self.attachmentPixmap)
            self.isNullPixmap = False

            if self.do_on_hover :
                self.createOverlayPixmap()
                style = " QLabel {  border: 2px solid gray;   border-radius: 4px;   padding: 2px;  } "
                self.setStyleSheet(style)





    def update(self):
        self.attachmentPixmap = QtGui.QPixmap(self.fileOnDisk ).scaled( self.x, self.y, QtCore.Qt.KeepAspectRatio)
        self.setPixmap( self.attachmentPixmap)
        if self.do_on_hover :
            self.createOverlayPixmap()

    ## @decorateur_try_except
    def mousePressEvent(self, event):
        super(PicButton, self).mousePressEvent(event)

        self.SIGNAL_imageClicked.emit( self.fileOnDisk)


    ## @decorateur_try_except
    def createOverlayPixmap(self , alpha = 45):


        px = float(self.attachmentPixmap.width())/3.0
        py= float(self.attachmentPixmap.height())/3.0

        pf = px
        if px > py :
            pf = py

        overPix = QtGui.QPixmap(self.overImagePath ).scaled( pf, pf, QtCore.Qt.KeepAspectRatio)
        self.resultPix = QtGui.QPixmap(self.attachmentPixmap.width(), self.attachmentPixmap.height() )
        self.resultPix.fill(QtCore.Qt.transparent)

        painter = QtGui.QPainter(self.resultPix) 
        painter.drawPixmap(0,0, self.attachmentPixmap)
        painter.fillRect(0,0,self.attachmentPixmap.width() ,self.attachmentPixmap.height(), QtGui.QColor(0,0,0,alpha))
        painter.drawPixmap(px, py, overPix)
        del painter


    def enterEvent(self, event):
        if self.do_on_hover :
            if self.resultPix :
                self.setPixmap(self.resultPix)

  
    def leaveEvent(self, event):
        if self.do_on_hover :
            self.setPixmap(self.attachmentPixmap)






