#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
ZetCode PyQt4 tutorial 

In this example, we draw text in Russian azbuka.

author: Jan Bodnar
website: zetcode.com 
last edited: September 2011
"""

import sys
import hashlib
import random
import string
import datetime
import _strptime

import utils
from utils import *

try :
    from sgtk.platform.qt import QtCore, QtGui
    _signal = QtCore.Signal 
    outFileName = "side"

except :
    from PyQt4 import QtGui, QtCore
    _signal = QtCore.pyqtSignal
    outFileName = "cute"


class Filter(QtCore.QObject):
    def eventFilter(self, widget, event):
        # FocusOut event

        if event.type() == QtCore.QEvent.FocusOut:
            if isinstance( QtGui.QApplication.focusWidget(), ToDoLineEdit) :
                print "keep editor"
            else :
                # do custom stuff
                print 'focus out'
            # return False so that the widget will also handle the event
            # otherwise it won't focus out
            # return False
        else:
            pass
            # we don't care about other events
            # return False

        return QtGui.QWidget.eventFilter(self, widget, event)

class notification(object):
    def __init__( self, sender, receiver, date, message, noteDict ) :
        self.sender = sender
        self.receiver = receiver
        self.date = date
        self.message = message
        self.noteDict = noteDict
    
        self.timeago()



    def timeago(self):
        date = self.date #datetime.datetime(2015, 07, 29, 10, 20, 4, 534918)
        now = datetime.datetime.now()

        elapsedSeconds = (now-date).total_seconds()
        elapsedMinutes = elapsedSeconds/60
        elapsedhours = elapsedMinutes/60
        elapsedDays = elapsedhours/24
        elapsedWeeks = elapsedDays/7
        elapsedMonths = elapsedWeeks/4
        elapsedYears = elapsedDays/365

        scale = ["second","minute", "hour", "day", "week", "month", "Year"]


        elList = []
        elList.append(elapsedSeconds)
        elList.append(elapsedMinutes)
        elList.append(elapsedhours)
        elList.append(elapsedDays)
        elList.append(elapsedWeeks)
        elList.append(elapsedMonths)
        elList.append(elapsedYears)

        count = 0

        Min =  10**10
        for el in elList:
            
            if el < Min :
                Min = el
            if el < 1.0 :
                if count>0:
                    count -=1
                break
            count+=1

        plural = ''
        if  int(elList[count])> 1 :
            plural = 's'

        return str(int(elList[count]))+" "+ str(scale[count])+plural+ " ago" 

    def text(self):
        intColor = int(hashlib.sha1(self.sender).hexdigest(), 16) % (256 ** 3)
        userColor =  '#{0:06X}'.format(intColor)              
        return "<font color='"+userColor+"'>" +self.sender+ "</font> (" +self.timeago()+")> " + self.message


class ToDoLineEdit(QtGui.QLineEdit):
    def __init__(self, text , parent = None ) :
        QtGui.QLineEdit.__init__(self, text, parent) 


        completer = QtGui.QCompleter()
        self.setCompleter(completer)

        self.model = QtGui.QStringListModel()
        completer.setModel(self.model)

        

    def setAutoCompletion(self, peopleList ):
        self.model.setStringList(peopleList)

class NotificationWriter(QtGui.QWidget):
    def __init__(self, parent = None ) :
        QtGui.QWidget.__init__(self, parent) 

        lay = QtGui.QHBoxLayout()
        lay.setContentsMargins(0,0,0,0)
        lay.setSpacing(0)

        self.writeTo = ToDoLineEdit("who ?") 
        self.writeWhat = ToDoLineEdit("what ?")
        self.sendButton = QtGui.QPushButton()
        self.sendButton.setIcon(QtGui.QIcon(getRessources("sendNotification") ))

        self.sendButton.setFlat(True);
        self.sendButton.setIconSize(QtCore.QSize(20,20));
        style = 'QPushButton:hover{border: 1px solid rgb(48,226,227)}'
        self.sendButton.setStyleSheet("QPushButton{outline: none;}"+style);
        self.sendButton.notificationAttr = True

        lay.addWidget(self.writeTo)
        lay.addSpacing(5)
        lay.addWidget(self.writeWhat)
        lay.addSpacing(5)
        lay.addWidget(self.sendButton)
        self.setLayout(lay)


        self.writeTo.setMaximumWidth(150)


class NotificationBar(QtGui.QWidget):
    
    def __init__(self, notificationList = [], peopleList = [], parent = None):
        QtGui.QWidget.__init__(self, parent)


        self.speedFactor = 1

        self.notificationList = notificationList
        self.notification = 0

        

        self.lay = QtGui.QHBoxLayout()
        self.lay.setSpacing(0)
        self.lay.setContentsMargins(0,0,0,0)
        

        self.setLayout(self.lay)


        self.labelEdit = NotificationWriter()
        self.label=QtGui.QLabel()
        #self.setText()

        self.label.setAlignment(QtCore.Qt.AlignTop)
        self.label.setMinimumHeight(32)
        self.label.setMinimumWidth(600)
        self.animate = QtCore.QPropertyAnimation(self.label, "pos")
        self.animate.finished.connect(self.myfinished)

        self.lay.addWidget(self.label)
        self.geom = QtCore.QRect()
        self.painted = False

        self._filter = Filter()
        self.labelEdit.writeTo.installEventFilter(self)
        self.labelEdit.writeTo.setAutoCompletion(peopleList)
        self.labelEdit.writeWhat.installEventFilter(self)
        self.labelEdit.sendButton.installEventFilter(self)

        self.radioChecked = 0

        if self.radioChecked == 0 :
            self.notificationList = docLoad()
        elif self.radioChecked == 1 :
            self.notificationList = autoLoad()
        else :
            self.notificationList = []

    def eventFilter(self, widget, event):
        # FocusOut event

        if event.type() == QtCore.QEvent.FocusOut:
            if isinstance( QtGui.QApplication.focusWidget(), ToDoLineEdit) :
                print "keep editor"
            elif hasattr(QtGui.QApplication.focusWidget(), "notificationAttr"):
                print "keep editor"
            else :
                self.stopWritingNotification()
                print 'focus out'

            # return False so that the widget will also handle the event
            # otherwise it won't focus out
            # return False
        else:
            pass
            # we don't care about other events
            # return False

        return QtGui.QWidget.eventFilter(self, widget, event)

    def writeNotification(self):
        self.label.setParent(None)
        self.lay.addWidget(self.labelEdit )
        self.labelEdit.writeWho.setFocus()

    def stopWritingNotification(self):
        self.labelEdit.setParent(None)
        self.lay.addWidget(self.label )


    def answerNotifcation(self):
        self.label.setParent(None)
        self.lay.addWidget(self.labelAnswer )
        self.labelAnswer.writeWhat.setFocus()




    def setText(self):
        if not len(self.notificationList) :
            self.label.setText("Launch Bar")
            return

        self.label.setText( self.notificationList[self.notification].text() )


    def rectChanged(self):
        if self.rect().right()!= self.geom.right() : return True
        elif self.rect().left()!= self.geom.left() : return True
        if self.rect().top()!= self.geom.top() : return True
        elif self.rect().bottom()!= self.geom.bottom() : return True

        return False

    def setAnim(self):

        self.setText()

        dist = self.rect().bottom()-self.rect().top()
        self.animate.setStartValue(QtCore.QPoint(0,self.rect().top() ))
        self.animate.setEndValue(QtCore.QPoint(0,self.rect().bottom() ))
        self.animate.setDuration(200*dist*self.speedFactor)
        self.animate.start()


    def paintEvent(self, e):
        if not self.painted or self.rectChanged():
            self.geom = self.rect()
            self.painted=True
            self.setAnim()

    
    def myfinished(self) :
        #print "finished"

        self.notification+=1
        if ( self.notification > len(self.notificationList)-1 ) :
            self.notification = 0

        if len(self.notificationList) :
            self.setText()
            
            self.setAnim()
            self.animate.setCurrentTime( 0)

    def updateNotificationList(self, notificationList):
        self.notificationList = notificationList
        self.notification = 0


    def radioButtonClicked(self, radio):
        self.radioChecked = radio
        if self.radioChecked == 0 :
            self.notificationList = docLoad()
        elif self.radioChecked == 1 :
            self.notificationList = autoLoad()
        else :
            self.notificationList = []

        self.notification = 0
        self.setText()
       
        self.setAnim()
        self.animate.setCurrentTime( 0)
        self.animate.pause()

        

    def mousePressEvent (self, event ):
        if event.button() == QtCore.Qt.LeftButton:
            if QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ShiftModifier :
                print "add to selection", self.notification
            elif QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ControlModifier :
                print "next"
                self.myfinished()
            else :
                print "select", self.notification

        if event.button() == QtCore.Qt.RightButton:
            globalPos = self.mapToGlobal(event.pos());
            menu = QtGui.QMenu()
            
            ag = QtGui.QActionGroup(menu, exclusive=True)
            docAction =  QtGui.QAction("Show news",  menu , triggered=lambda: self.radioButtonClicked(0)) 
            docAction.setCheckable( True )
            if self.radioChecked == 0 :
                docAction.setChecked( True )


            a = ag.addAction(docAction)
            menu.addAction(a)
            notiAction =  QtGui.QAction("Show notification",  menu , triggered=lambda: self.radioButtonClicked(1)) 
            notiAction.setCheckable( True )
            if self.radioChecked == 1 :
                notiAction.setChecked( True )
            a = ag.addAction(notiAction)
            menu.addAction(a)


            muteAction =  QtGui.QAction("Mute",  menu ,  triggered = lambda: self.radioButtonClicked(2) ) 
            muteAction.setCheckable( True )
            if self.radioChecked == 2 :
                muteAction.setChecked( True )
            a = ag.addAction(muteAction)
            menu.addAction(a)


            """
            notificationMenu = menu.addAction(QtGui.QIcon(getRessources("notification.png")),"Notify somebody",  self.writeNotification  ) 
            menu.addAction(notificationMenu)
            """

            #menu.addAction( QtGui.QAction("Remove", menu) )
            #menu.addAction( QtGui.QAction("Answer", menu) )
            #menu.addAction( QtGui.QAction("Status", menu) )
            self.animate.pause()
            menu.exec_(globalPos)
            if self.notificationList :   
                print "resume !"
                self.animate.resume()
            else :
                print self.animate.state()


            self.menu = menu
        

        #QtGui.QWidget.mousePressEvent(self, event)


class MyWidgetHolder(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)

        notificationList = []
        # sender, receiver, date, message, noteDict )
        notificationList.append( notification("Cyrilc", "john", datetime.datetime.now(), "Wait for approval ! rhooooooo lr lr bon y va oui ou non il est l'heure d'ylller j'ai faim. et de toute facon il est l'heure", "pas") )
        notificationList.append( notification("Donat", "john", datetime.datetime.now(), "Peu continuer !", "pas") )
        notificationList.append( notification("MikeB", "john", datetime.datetime.now(), "Oui c'est sympas", "pas") )
        notificationList.append( notification("Aurelien", "john", datetime.datetime.now(), "Launch Time", "pas") )
        notificationList.append( notification("Thomas", "john", datetime.datetime.now(), "Wait for appoval", "pas") )
        notificationList.append( notification("James", "john", datetime.datetime.now(), "Approved", "pas") )
        notificationList.append( notification("Mike", "john", datetime.datetime.now(), "Aurevoir John !", "pas") )
        notificationList.append( notification("Tristan", "john", datetime.datetime.now(), "Bonjour John !", "pas") )
        notificationList.append( notification("Eric", "john", datetime.datetime.now(), "Bonjour John !", "pas") )
        notificationList.append( notification("Francois", "john", datetime.datetime.now(), "Bonjour John !", "pas") )


        path_to_shotgunApi = getPathToShotgunApi()
        sys.path.append(path_to_shotgunApi)

        from shotgun_api3 import Shotgun
        self.SERVER_PATH = "https://nozon.shotgunstudio.com"
        self.SCRIPT_NAME = 'noteManager'     
        self.SCRIPT_KEY = '30b93ec002ce2e22ecd6fb31fdda6063797deed1d612b4f6ca39e8030104707c'
        self.sg = Shotgun(self.SERVER_PATH, self.SCRIPT_NAME, self.SCRIPT_KEY)
        sg_spawnedNotes = self.sg.find("CustomEntity04", [ ['sg_note','is_not', None] ] ,   ["project"] )
        for a in sg_spawnedNotes :
            print a


        self.setMinimumWidth(1000)
        self.setMinimumHeight(50)

        self.noteBarW = NotificationBar(notificationList, ["jack","popeye","james","conan le barbare"])
        button = QtGui.QPushButton("pafpaf")
        #button.clicked.connect(self.noteBarW.addNotification)

        lay = QtGui.QVBoxLayout()
        lay.addWidget(button)
        lay.addWidget(self.noteBarW)
        lay.addWidget(QtGui.QPushButton("pafpaf"))
        self.setLayout(lay)
        lay.setSpacing(0)
        lay.setContentsMargins(0,0,0,0)
        self.show()


def autoLoad():
    notificationList = []
        # sender, receiver, date, message, noteDict )
    notificationList.append( notification("Cyrilc", "john", datetime.datetime.now(), "Wait for approval ! rhooooooo lr lr bon y va oui ou non il est l'heure d'ylller j'ai faim. et de toute facon il est l'heure", "pas") )  
    notificationList.append( notification("Cyrilc", "john", datetime.datetime.now(), "Wait for approval !", "pas") )
    notificationList.append( notification("Donat", "john", datetime.datetime.now(), "Peu continuer !", "pas") )
    notificationList.append( notification("MikeB", "john", datetime.datetime.now(), "Oui c'est sympas", "pas") )
    notificationList.append( notification("Aurelien", "john", datetime.datetime.now(), "Launch Time", "pas") )
    notificationList.append( notification("Thomas", "john", datetime.datetime.now(), "Wait for appoval", "pas") )
    notificationList.append( notification("James", "john", datetime.datetime.now(), "Approved", "pas") )
    notificationList.append( notification("Mike", "john", datetime.datetime.now(), "Aurevoir John !", "pas") )
    notificationList.append( notification("Tristan", "john", datetime.datetime.now(), "Bonjour John !", "pas") )
    notificationList.append( notification("Eric", "john", datetime.datetime.now(), "Bonjour John !", "pas") )
    notificationList.append( notification("Francois", "john", datetime.datetime.now(), "Bonjour John !", "pas") )

    return notificationList


def docLoad():
    notificationList = []
        # sender, receiver, date, message, noteDict )
    docDate = datetime.datetime(2015, 9, 7, 17,31,0,0)
    datetime.datetime.now()
    notificationList.append( notification("ToDoNote", "john", docDate, "News : The LaunchBar refreshes every 5 secondes", "pas") )  
    notificationList.append( notification("ToDoNote", "john", docDate, "News : The assignedTo filter now just acts on the shot/asset list", "pas") )
    notificationList.append( notification("ToDoNote", "john", docDate, "BugFix : QuickEdit note can be closed by clicking on the 'create note' bar", "pas") )
    notificationList.append( notification("ToDoNote", "john", docDate, "UI optimization : The 'reply' and 'create' note buttons are color differenced", "pas") )
    notificationList.append( notification("ToDoNote", "john", docDate, "UI optimization : A dot marks every note", "pas") )

    return notificationList

def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = MyWidgetHolder()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()