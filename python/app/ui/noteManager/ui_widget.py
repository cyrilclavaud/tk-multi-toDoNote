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


class toggleBtn(QtGui.QPushButton) :
    def __init__(self, label, parent = None):
        QtGui.QPushButton.__init__(self,  parent)
        self.setIcon(QtGui.QIcon(getRessources("refreshUI.png") ))
        self.setFlat(True);
        self.setIconSize(QtCore.QSize(16,16));
        self.setStyleSheet("QPushButton{outline: none;}");

class loadingWidget(QtGui.QWidget) :
    @decorateur_try_except
    def __init__(self, parent = None):
        plog("loadingWidget.__init__\n")
        QtGui.QWidget.__init__(self, parent)
         
        # Load the file into a QMovie
        self.movie = QtGui.QMovie(getRessources( "preloader.gif"), QtCore.QByteArray(), self)
         
        size = self.movie.scaledSize()
        self.setGeometry(50, 50, size.width(), size.height())

         
        self.movie_screen = QtGui.QLabel()
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
    @decorateur_try_except
    def __init__(self, parent = None):
        plog("versionWidgetCombo.__init__\n")
        super(versionWidgetCombo, self).__init__(parent)
        
        self.versionDatas = []
        self.pathToMovie = None
       
        self.masterLayout = QtGui.QVBoxLayout()
        self.masterLayout.setContentsMargins(0,0,0,0)


        self.setLayout(self.masterLayout)


        self.layout = QtGui.QHBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)

        titleLabel = QtGui.QLabel("Link to version")
        titleLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.masterLayout.addWidget(titleLabel)
        self.masterLayout.addLayout(self.layout)


        #pic = PicButton( getRessources( "preloader.gif"),200,200, overImageName = "play.png")
        #pic.setMaximumWidth(200)
        #pic.SIGNAL_imageClicked.connect(self.play_pathToMovie)
        self.pic= loadingWidget() # PicButton( getRessources( "preloader.gif"),200,200, overImageName = "play.png") #loadingWidget()
        self.pic.setMaximumWidth(50)

        

        infoLayout = QtGui.QVBoxLayout()
        infoLayout.setAlignment(QtCore.Qt.AlignTop )
        self.layout.addLayout( infoLayout)
        self.layout.addStretch()
        self.layout.addWidget(self.pic,QtCore.Qt.AlignTop)

       
        self.versionQtCombo = QtGui.QComboBox( )
        self.nameQt = QtGui.QLabel("")
        self.userQt = QtGui.QLabel("")
        self.dateQt = QtGui.QLabel("" )

        infoLayout.addWidget( self.versionQtCombo ) 
        infoLayout.addWidget( self.nameQt )    
        infoLayout.addWidget( self.userQt ) 
        infoLayout.addWidget( self.dateQt )   
        infoLayout.addSpacing( 100)

        #infoLayout.addStretch()
        infoLayout.setContentsMargins(0,0,0,0)
        infoLayout.setSpacing(0)

        self.layout.addSpacing(5)


        self.versionQtCombo.currentIndexChanged.connect(self.setVersionValue)



    @decorateur_try_except
    def setVersionValue(self, idx) :


        if idx == 0 :
            self.nameQt.setText("name : None" )
            self.userQt.setText("user : None" )
            self.dateQt.setText("created : None" )

            self.pic.setParent(None)
            self.pic = PicButton( getRessources( "empty.png"),50,50, overImageName = None)
            self.pic.setMaximumWidth(50)
            self.layout.addWidget(self.pic,QtCore.Qt.AlignTop)
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
            
            self.nameQt.setText("name : %s"%versionData["code"].replace(versionString, "<b>%s</b>"%versionString) )    
            self.userQt.setText("%s : <b>%s</b"%("user"  ,  versionDataName ) )  
            self.dateQt.setText("%s : <b>%s</b"%("created", versionData["created_at"]) )   
            
            self.pic.setParent(None)
            self.pic = PicButton( versionData["downloadedImage"] ,200,200, overImageName = "play.png",  doStart=True)
            if self.pic.isNullPixmap :
                self.pic.setMaximumWidth(50)
            else :
                self.pic.setMaximumWidth(200)

            self.layout.addWidget(self.pic,QtCore.Qt.AlignTop)
            self.pathToMovie = versionData["sg_path_to_movie"]
            self.pic.SIGNAL_imageClicked.connect(self.play_pathToMovie)


    @decorateur_try_except
    def play_pathToMovie(self, file):
        
        if self.pathToMovie :
            convertPath = self.pathToMovie.replace( "//server01/shared2/"  , "S:\\")
            os.system("start %s"%convertPath )

    @decorateur_try_except
    def setOnLoading(self):
        if self.pic :
            self.pic.setParent(None)
        self.pic = loadingWidget()
        self.pic.setMaximumWidth(50)
        self.layout.addWidget(self.pic,QtCore.Qt.AlignTop)
    
    @decorateur_try_except
    def updateWidget(self, datas ):
        self.versionDatas= datas[0]


        self.pic.setParent(None)
        """
        self.pic = PicButton( getRessources( "version.png"),200,200, overImageName = "empty.png")
        self.pic.setMaximumWidth(200)
        """

        self.versionQtCombo.blockSignals(True)
        self.versionQtCombo.clear()

        self.versionQtCombo.addItem(str("None") ) 
        versionData = None
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

            self.versionQtCombo.addItem(str(versionString) ) 

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

    @decorateur_try_except
    def __init__(self, versionData, parent=None):
        plog("versionWidget.__init__\n")
        super(versionWidget, self).__init__(parent)
        self.pathToMovie = versionData["sg_path_to_movie"]
       
        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)

        self.setLayout(layout)


        pic =   PicButton(versionData["downloadedImage"],200,200, overImageName = "play.png")
        pic.setMaximumWidth(200)
        pic.SIGNAL_imageClicked.connect(self.play_pathToMovie)

        layout.addWidget(pic)

        infoLayout = QtGui.QVBoxLayout()
        infoLayout.setAlignment(QtCore.Qt.AlignTop)
        layout.addLayout( infoLayout)


        versionDataName = versionData["user"]
        if not versionDataName :
            versionDataName = "unknow"
        else :
            versionDataName = versionData["user"]["name"]


        versionString = versionData["code"] 
        splits = re.findall(r' v\d+', versionData["code"] )
        if splits :
            versionString = splits[-1]
        
        infoLayout.addWidget(QtGui.QLabel("name : %s"%versionData["code"].replace(versionString, "<b>%s</b>"%versionString) ) )    
        infoLayout.addWidget(QtGui.QLabel("%s : <b>%s</b"%("user"  ,  versionDataName ) ) ) 
        infoLayout.addWidget(QtGui.QLabel("%s : <b>%s</b"%("created", versionData["created_at"]) ) )   


        #infoLayout.addStretch()
        infoLayout.setContentsMargins(0,0,0,0)
        infoLayout.setSpacing(0)

        layout.addSpacing(5)

    @decorateur_try_except
    def play_pathToMovie(self, file):
        
        convertPath = self.pathToMovie.replace( "//server01/shared2/"  , "S:\\")
        os.system("start %s"%convertPath )


class PicButton(QtGui.QLabel):
    SIGNAL_imageClicked = _signal(object)

    @decorateur_try_except
    def __init__(self, imageFileName, x = 100, y = 100 , overImageName = "pencil.png" , doStart=False ,parent=None):
        plog("PicButton.__init__\n")
        super(PicButton, self).__init__(parent)
        self.do_on_hover  = True 
        self.isNullPixmap = True 
        if overImageName == None :
            self.do_on_hover = False

        self.overImagePath = getRessources(overImageName)
        self.resultPix = None
        self.x = x 
        self.y = y

        self.fileOnDisk =  imageFileName
        self.attachmentPixmap = QtGui.QPixmap(imageFileName)
        if self.attachmentPixmap.isNull() :
            if doStart :
                self.attachmentPixmap = QtGui.QPixmap(getRessources("no_thumbnail.png") ).scaled ( 45,45, QtCore.Qt.KeepAspectRatio)
                self.setPixmap(self.attachmentPixmap)
                self.isNullPixmap = True
                self.setAlignment(QtCore.Qt.AlignTop)
       
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

    @decorateur_try_except
    def mousePressEvent(self, event):
        super(PicButton, self).mousePressEvent(event)

        self.SIGNAL_imageClicked.emit( self.fileOnDisk)


    @decorateur_try_except
    def createOverlayPixmap(self ):


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
        painter.fillRect(0,0,self.attachmentPixmap.width() ,self.attachmentPixmap.height(), QtGui.QColor(0,0,0,45))
        painter.drawPixmap(px, py, overPix)
        del painter

    @decorateur_try_except
    def enterEvent(self, event):
        if self.do_on_hover :
            if self.resultPix :
                self.setPixmap(self.resultPix)

    @decorateur_try_except    
    def leaveEvent(self, event):
        if self.do_on_hover :
            self.setPixmap(self.attachmentPixmap)






