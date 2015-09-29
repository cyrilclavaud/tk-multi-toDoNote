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



class comboFilterWidget3(QtGui.QComboBox):
    SIGNAL_currentIndexChanged = _signal(object, object)
    SIGNAL_filterResultEmpty = _signal(object)


    def __init__(self, filterLineWidget = None , filterTasksAssigneesLineWidget = None  , parent = None ) :

        super(comboFilterWidget3, self).__init__(parent )

        self.filterWidget = filterLineWidget 
        self.filterTasksAssigneesLineWidget = filterTasksAssigneesLineWidget 

        self.currentIdx = 0

        self.filterWidget.widget.textChanged.connect(self.filterItemList)
        self.filterTasksAssigneesLineWidget.widget.textChanged.connect( self.filterItemList )

        self.drawComplex = True
        self.itemList = []
        self.filteredItemList = []

        self.currentIndexChanged.connect(self.computeNewIndex)


    def mousePressEvent(self, event ):
        if self.drawComplex :
            QtGui.QComboBox.mousePressEvent(self, event ) 
        return

    def computeNewIndex(self, test = None ) :

        currentItemText = str(self.currentText())
        idx = 0
        for  item in self.itemList :
            if currentItemText == item["code"] :
                self.currentIdx = idx
                break
            idx+=1


        self.SIGNAL_currentIndexChanged.emit(self.currentIdx, True)

    def currentIndex(self):
        currentItemText = str(self.currentText())
        idx = 0
        for  item in self.itemList :
            if currentItemText == item["code"] :
                self.currentIdx = idx
                break
            idx+=1
            
        return self.currentIdx


    def fillItem(self, itemList = None ) :
        self.blockSignals(True)
        if itemList :
            self.itemList = itemList
        else :
            self.clear()



        self.filteredItemList = []

        assignedToTxt = self.filterTasksAssigneesLineWidget.widget.text()
        if not isinstance(assignedToTxt, unicode):
            assignedToTxt = unicode(assignedToTxt.toUtf8() , "utf-8" )


        txtFilter = self.filterWidget.widget.text()
        if not isinstance(txtFilter, unicode):
            txtFilter = unicode(txtFilter.toUtf8() , "utf-8" ) 



        if txtFilter == ""  and assignedToTxt == "" :
            pass #print "---> nothing to Filter"
        else :
            for item in self.itemList :
                if txtFilter.upper() in item["code"].upper()  :# and ( assignedToTxt != ""  ):
                    if  assignedToTxt != "" :
                        if assignedToTxt.upper() in " ".join( item["sgAvailableAssignees"] ).upper():
                            self.filteredItemList.append( item )                            
                    else :
                        self.filteredItemList.append( item ) 

        if not  self.filteredItemList :
            for item in self.itemList :
                self.addItem( item["code"])
        else :
            for item in self.filteredItemList :
                self.addItem( item["code"])


        if self.count() == 1 :
            self.drawComplex = False
        else : 
            self.drawComplex = True
        

        self.blockSignals(False)
        
        if txtFilter != ""  or assignedToTxt != ""  :
            if not self.filteredItemList :
                self.SIGNAL_filterResultEmpty.emit(True)
            else :
                self.SIGNAL_filterResultEmpty.emit(False)
        else :
            self.SIGNAL_filterResultEmpty.emit(False)
        


        if not itemList :
            currentItemText = str(self.currentText())
            idx = 0
            for  item in self.itemList :
                if currentItemText == item["code"] :
                    self.currentIdx = idx
                    break
                idx+=1
            self.SIGNAL_currentIndexChanged.emit(self.currentIdx, False)

        self.repaint()

    def filterItemList(self, test  ) :
        self.fillItem(itemList = None)


    def paintEvent(self   , paintEvent):
        painter = QtGui.QStylePainter(self)
        opt = QtGui.QStyleOptionComboBox()
        self.initStyleOption(opt)
        if self.drawComplex :
            painter.drawComplexControl(QtGui.QStyle.CC_ComboBox, opt)

        painter.drawControl(QtGui.QStyle.CE_ComboBoxLabel, opt)


class comboFilterWidget2(QtGui.QWidget):


    SIGNAL_currentIndexesChanged = _signal(object)
    SIGNAL_TaskcurrentIndexesChanged = _signal(object)

    def __init__(self, typeDict , entriesDictList , showLabel = True, multiCheckable = False, parent = None ):
        super(comboFilterWidget2, self).__init__(parent )
 
        self.drawComplex = True

        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)

        self.typeDict =  typeDict 
        self.entriesDictList =  entriesDictList 

 
        label = QtGui.QLabel(  parent = self )
        

        self.multiCheckable = multiCheckable 

        if showLabel :
            label.setText( typeDict["name"] )

            if typeDict["icon"] :
                icon  = QtGui.QLabel( parent = self )
                icon.setPixmap(  QtGui.QPixmap(getRessources(typeDict["icon"])).scaled ( 16, 16, QtCore.Qt.KeepAspectRatio )  )
                icon.setMaximumWidth(16)

            
                layout.addWidget(icon)
            if not typeDict["name"] :
                label.hide()
                layout.setSpacing(0)
            layout.addWidget(label)
        self.widget = QtGui.QComboBox( parent = self )
        self.widget.setItemDelegate( QtGui.QItemDelegate(self ))

        self.widget.setMinimumWidth(120)

      
        checkCount = 0
        if not self.multiCheckable :
            
            for entryDict in entriesDictList :
                if entryDict.has_key("checked") :
                    if entryDict["checked"] == True :
                        checkCount+= 1




        idx = 0
        for entryDict in entriesDictList :
            if not self.multiCheckable :


                if not entryDict.has_key("checked") or not checkCount :
                    entryDict["checked"] = True
                
                if entryDict["checked"] :
                    if entryDict["icon"] :
                        self.widget.addItem( QtGui.QIcon(getRessources( entryDict["icon"] ) ), entryDict["text"]  )
                    else :
                        self.widget.addItem(  entryDict["text"]   )
                
                if self.widget.count == 1 :
                    #-self.widget.setEnabled(False)

                    self.drawComplex = False

            else :
                if entryDict["icon"] :
                    self.widget.addItem( QtGui.QIcon(getRessources( entryDict["icon"] ) ), entryDict["text"]  )
                    #self.widget.addItem(  entryDict["text"]  )
                else :
                    self.widget.addItem(  entryDict["text"]   )

                item = self.widget.model().item(idx, 0)

               
                if entryDict.has_key("checked") : 

                    if entryDict["checked"] :
                        
                        item.setCheckState(QtCore.Qt.Unchecked)

                        self.handleItemPressed(item.index())
                    
                    else :
                        item.setCheckState(QtCore.Qt.Checked)
                        self.handleItemPressed(item.index())   

                else :
                    item.setCheckState(QtCore.Qt.Unchecked)
                    entryDict["checked"] = False


     
           
                
            idx +=1



       
        if self.multiCheckable :
            
            self.widget.paintEvent = self.widget_paintEvent
            
            self.widget.view().viewport().installEventFilter(self) 
            self.widget.view().pressed.connect(self.handleItemPressed)
            self.menuOpt = self.getDisplayOpt()
            
        elif self.widget.count() == 1 :
            
            #-self.widget.setEnabled(False)
            self.drawComplex = False

        layout.addWidget(self.widget)
        if self.multiCheckable :        
            self.widget.currentIndexChanged.connect(self.sendCheckedIndexes)
        else :
            self.widget.paintEvent = self.single_widget_paintEvent
            self.widget.mousePressEvent  = self.widget_mousePressEvent



    def widget_mousePressEvent(self, event ):
        if self.drawComplex :
            QtGui.QComboBox.mousePressEvent(self.widget, event ) 
        return


    def eventFilter(self, obj, event) :


        if ( event.type() == QtCore.QEvent.MouseButtonRelease and obj == self.widget.view().viewport() ) :
            self.widget.repaint()
            return True

        return False

    

    def single_widget_paintEvent(self, paintEvent):
        painter = QtGui.QStylePainter(self.widget)
        opt = QtGui.QStyleOptionComboBox()
        self.widget.initStyleOption(opt)

        if self.drawComplex :
            painter.drawComplexControl(QtGui.QStyle.CC_ComboBox, opt)

        painter.drawControl(QtGui.QStyle.CE_ComboBoxLabel, opt)

    def widget_paintEvent(self, paintEvent):

        painter = QtGui.QStylePainter(self.widget)
        painter.setPen(self.widget.palette().color(QtGui.QPalette.Text) )
         
        
        opt = QtGui.QStyleOptionComboBox()
        self.widget.initStyleOption(opt)       

        
        opt.currentText = self.menuOpt[0]
        if not self.menuOpt[1] :
            opt.currentIcon = QtGui.QIcon()
        else :
            opt.currentIcon = QtGui.QIcon(getRessources(self.retrieveIconFromValue(self.menuOpt[0] ) ))


        painter.drawComplexControl(QtGui.QStyle.CC_ComboBox, opt)

        painter.drawControl(QtGui.QStyle.CE_ComboBoxLabel, opt)



    def getDisplayOpt(self):
        checkedList = []
        uncheckedList = []
        for entries in self.entriesDictList :
            if not entries.has_key("checked"):
               entries["checked"] = False 
            if entries["checked"] :
                checkedList.append(entries["text"])
            else :
                uncheckedList.append(entries["text"])

        if len(checkedList) == 0 :
            return ["Nothing",0]
        elif len(checkedList) == 1 :
            return [checkedList[0],1]
        elif len(uncheckedList) == 0 :
            return ["All",0]
        else :
            return ["Multi"+self.typeDict["name"],0]


    def handleItemPressed(self, index):
        clickedItem = self.widget.model().itemFromIndex(index)
        if index.row() == 0 :

            for rowIdx in range( 1, index.model().rowCount()  ) :
                modIndex =  index.model().index(rowIdx,0) 
                item = self.widget.model().itemFromIndex(modIndex)
                
                if clickedItem.checkState() == QtCore.Qt.Checked:
                    self.entriesDictList[rowIdx]["checked"] = False
                    item.setCheckState(QtCore.Qt.Unchecked)
                else:
                    item.setCheckState(QtCore.Qt.Checked)
                    self.entriesDictList[rowIdx]["checked"] = True
        
            if clickedItem.checkState() == QtCore.Qt.Checked:
                self.entriesDictList[index.row()]["checked"] = False
                clickedItem.setCheckState(QtCore.Qt.Unchecked)
            else:
                self.entriesDictList[index.row()]["checked"] = True
                clickedItem.setCheckState(QtCore.Qt.Checked)

        else :
            if clickedItem.checkState() == QtCore.Qt.Checked:
                self.entriesDictList[index.row()]["checked"] = False
                clickedItem.setCheckState(QtCore.Qt.Unchecked)
            else:
                self.entriesDictList[index.row()]["checked"] = True
                clickedItem.setCheckState(QtCore.Qt.Checked)

            checkedList = []
            uncheckedList = []
            for entries in self.entriesDictList[1:] :
                if not entries.has_key("checked") :
                    entries["checked"] = False

                if entries["checked"] :
                    checkedList.append(entries["text"])
                else :
                    uncheckedList.append(entries["text"])
            
            modIndex =  index.model().index(0,0)
            item = self.widget.model().itemFromIndex(modIndex)

            if not uncheckedList :
                
                self.entriesDictList[0]["checked"] = True
                item.setCheckState(QtCore.Qt.Checked)
            else :
                self.entriesDictList[0]["checked"] = False
                item.setCheckState(QtCore.Qt.Unchecked)     


        self.menuOpt = self.getDisplayOpt()

        self.widget.currentIndexChanged.emit(0)

    def getfilterList(self):
        if self.multiCheckable :
            valuesList = []
            for entries in self.entriesDictList:
                if entries["checked"] :
                    valuesList.extend(entries["values"])
            return valuesList
        else :
            return self.retrieveValueFromName( str(self.widget.currentText()) ) 
    
    ## @decorateur_try_except
    def retrieveIconFromValue(self, value ) :
        for entriesDict  in  self.entriesDictList :
            if value in entriesDict["values"] :
                return  entriesDict["icon"]
        return value
    

    def retrieveIndiceFromValue(self, value) :
        idx = 0 
        for entriesDict  in  self.entriesDictList :
            if value in entriesDict["values"] :
                return  idx
            idx  += 1
        return 0

    ## @decorateur_try_except
    def retrieveValueFromName(self, name):
        for entriesDict  in  self.entriesDictList :
            if name in entriesDict["values"] :
                return  entriesDict["values"]
        return name




    ## @decorateur_try_except
    def retrieveNameFromValue(self, value) :
        #return value

        for entriesDict  in  self.entriesDictList :
            if value in entriesDict["values"] :
                return  entriesDict["text"]
        return value
    
    ## @decorateur_try_except
    def retrieveDictFromSelection(self):

        return self.retrieveValueFromName(self.widget.currentText())
    
    ## @decorateur_try_except
    def retrieveDict(self):
        import copy
        return copy.deepcopy( self.typeDict ) , copy.deepcopy( self.entriesDictList[1:] )


    ## @decorateur_try_except
    def setFromValue(self, name ) :
        idx = 0
        idx = self.widget.findText(name)
        self.widget.setCurrentIndex(idx)
        
    ## @decorateur_try_except
    def setMyCurrentIndex(self, index ):

        self.widget.setCurrentIndex(0) 





    ##################################### 
    def getSoloChecked(self):
        checkedIndexList = self.getCheckedIndexes()
        if len( checkedIndexList ) == 1 :
            if not 0 in checkedIndexList :
                return self.entriesDictList[checkedIndexList[0]]["values"]
            else :
                return None

        return None


    def getCheckedBoolList(self) :
        boolList = [] #QtCore.QStringList()
        for dictEntries in  self.entriesDictList :
            if dictEntries["checked"] :
                boolList.append(True )
            else :
                boolList.append(False )
        return boolList

    def getCheckedIndexes(self ):
        indexesList = []
        idx = 0
        for dictEntries in  self.entriesDictList :
            if dictEntries["checked"] :
                indexesList.append(idx)
            idx += 1

        
        if not indexesList :
            return range(len( self.entriesDictList )  )
        
        return indexesList

    def getTaskCheckedIndexes(self ):
        indexesList = []
        idx = 0
        for dictEntries in  self.entriesDictList :
            if dictEntries["checked"] :
                indexesList.append(idx)
            idx += 1

                
        return indexesList

    ## @decorateur_try_except
    def sendCheckedIndexes(self, index):

        self.SIGNAL_currentIndexesChanged.emit( self.getCheckedIndexes() )
        self.SIGNAL_TaskcurrentIndexesChanged.emit( self.getTaskCheckedIndexes() )


    def currentCheckedIndexes(self):
        checkedIndexes = self.getCheckedIndexes()
        if not checkedIndexes :
            return range(len(self.entriesDictList)-1)[0]
        else :
            return checkedIndexes[0]

    ## @decorateur_try_except
    def getMyValuesFromIndexes(self, indexList) :
        idx = 1
        valueLists = []
        for entryDict in self.entriesDictList :
            if idx in  indexList :
                valueLists.append(entryDict["values"])
            else :
                valueLists.append(None)
            idx+=1
        return valueLists

    ## @decorateur_try_except
    def setMyCurrentFromIndexes(self, indexList, availableTaskList = None ):


      
        self.widget.blockSignals(True)
        self.widget.clear()

        idx = 1
        for entryDict in self.entriesDictList :
            if idx in  indexList :
                if availableTaskList == None : 
                    if entryDict["icon"] :
                        self.widget.addItem( QtGui.QIcon(getRessources( entryDict["icon"] ) ), entryDict["text"]  )
                    else :
                        self.widget.addItem(  entryDict["text"]   )
                else :


                    if len(availableTaskList) == 0 or entryDict["text"] == "NoTask"  :
                        if "NoTask" in entryDict["values"] :
                            if entryDict["icon"] :
                                self.widget.addItem( QtGui.QIcon(getRessources( entryDict["icon"] ) ), entryDict["text"]  )
                            else :
                                self.widget.addItem(  entryDict["text"]   )
                    else :
                        test = False
                        for availableTask in availableTaskList :
                            if availableTask in entryDict["values"] :
                                test = True

                        if test :
                            if entryDict["icon"] :
                                self.widget.addItem( QtGui.QIcon(getRessources( entryDict["icon"] ) ), entryDict["text"]  )
                            else :
                                self.widget.addItem(  entryDict["text"]   )
            idx+=1


        if not self.widget.count() :
            self.widget.addItem( QtGui.QIcon(getRessources(  self.entriesDictList[-1]["icon"] ) ),  self.entriesDictList[-1]["text"]  )

        self.widget.blockSignals(False)



        
        if self.widget.count()==1:
            self.drawComplex = False
        else :
            self.drawComplex = True
        
        
        QtGui.QApplication.processEvents()
        self.widget.repaint()
        
        self.widget.currentIndexChanged.emit(0)

class lineEditFilterWidget(QtGui.QWidget) :

    ### @decorateur_try_except
    def __init__(self, typeDict , parent = None ):

        super(lineEditFilterWidget, self).__init__(parent )

        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)

        label = QtGui.QLabel( typeDict["name"] )
        icon = None
        if typeDict["icon"] :
            icon  = QtGui.QLabel()
            icon.setPixmap(  QtGui.QPixmap(getRessources(typeDict["icon"])).scaled ( 16, 16, QtCore.Qt.KeepAspectRatio )  )

        self.widget = QtGui.QLineEdit()
        if icon :
            layout.addWidget(icon)
        layout.addWidget(label)

        layout.addWidget(self.widget)

    def getText(self):
        text = self.widget.text() 
        if text :
            if not isinstance(text, unicode):
                text = unicode(text.toUtf8() , "utf-8" ) 
            return text
        else :
            return None


class taskLinks(QtGui.QWidget ):

    def __init__(self, childNoteTasks, parent = None):
        QtGui.QWidget.__init__(self, parent)
        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.setLayout(layout)
 
        self.isSelected = False
        self.mainLabel = None
        self.normalStyle = None
        self.litStyle = None
        self.highlightStyle = None 
        self.labelList = []


        test = "border-radius: 3px 3px ; "
        borderType = "outset "
        styleAlign = " qproperty-alignment: AlignCenter; "

        idx = 0
        for a in childNoteTasks :


            if borderType == "inset " :
                borderType = "outset "
            else :
                borderType = "inset "

            colorLabel = None #QtGui.QPushButton() #QtGui.QLabel()
            statusLabel = None
            transparent = "0"




            underLayout = QtGui.QHBoxLayout()
            underLayout.setContentsMargins(0,0,0,0)
            underLayout.setSpacing(1)
            underLayout.addSpacing(3)
            layout.addLayout(underLayout)

            

            if a["type"] == "master" :  
                if idx == 0 : # [TaskName]
                    colorLabel = QtGui.QLabel( parent = self)
                    self.mainLabel = colorLabel
                    self.labelList.append(colorLabel)
                    colorLabel.setAutoFillBackground(True)
                    colorLabel.setMaximumHeight(16)
                    font = colorLabel.font()
                    font.setPointSize(9);
                    #font.setWeight( QtGui.QFont.Bold )
                    
                    colorLabel.setFont(font)
                    colorLabel.setText(a["name"])       
                    underLayout.addWidget(colorLabel )

                    if a["status"] == "opn"  :
                        foreColor =  "color : rgb(210,210,210);"
                    elif a["status"] == "ip" :
                        foreColor = "color : rgb(60,60,30);"
                    else :
                        foreColor =  "color : rgb(150,150,150);"

                    
                    borderType = " none "
                    styleAlign =  " qproperty-alignment: AlignCenter; "
                    style = "QLabel {  " + styleAlign + foreColor + "background-color : rgba( 71,101,125, 0 ) ; "+test +" border: 1px " + borderType + " rgba( 30,30,30, 255) ;}"
                    colorLabel.setStyleSheet(style)

                    self.normalStyle = style
                    self.highlightStyle = "QLabel {  " + styleAlign + " color :rgb(48,226,227) ; " + "background-color : rgba( 71,101,125, 0 ) ; "+test +" border: 1px " + borderType + " rgba( 30,30,30, 255) ;}"
                    self.litStyle = "QLabel {  " + styleAlign + " color :rgb(230,230,230) ; " + "background-color : rgba( 71,101,125, 0 ) ; "+test +" border: 1px " + borderType + " rgba( 30,30,30, 255) ;}"
                
                else : 
                    colorLabel = QtGui.QPushButton( parent = self)

                    fct = lambda checked = False, noteId =  a['id'], taskName = a["name"] : parent.selectNote_from_id( noteId, taskName )
                    colorLabel.clicked.connect(fct)
                    colorLabel.enterEvent = lambda event, noteId = a['id'], parentTree = parent : self.my_enterEvent(event, noteId, parentTree) 
                    colorLabel.leaveEvent = lambda event, noteId = a['id'], parentTree = parent : self.my_leaveEvent(event, noteId, parentTree) 

                    colorLabel.setAutoFillBackground(True)
                    colorLabel.setMaximumHeight(13)
                    colorLabel.setFlat(True)
                    font = colorLabel.font()
                    font.setPointSize(8);
                    #font.setWeight( QtGui.QFont.Bold )
                    
                    colorLabel.setFont(font)
                    colorLabel.setText(a["name"])       
                    underLayout.addWidget(colorLabel)

                    if a["status"] == "opn"  :
                        foreColor =  "color : rgb(210,210,210);"
                        backGroundColorStyle = " background-color : rgba( 71,101,125, 255 ) ; "
                        backGroundColorStyle = " background-color : rgba( 40,141,223, 255 ) ; "
                    elif a["status"] == "ip" :
                        foreColor = "color : rgb(60,60,30);"
                        backGroundColorStyle = " background-color : rgba( 173,155, 93, 255 ) ; "
                        backGroundColorStyle = " background-color : rgba( 218,183, 98, 255 ) ; "

                    else :
                        foreColor =  "color : rgb(150,150,150);"
                        backGroundColorStyle = " background-color : rgba( 95, 95, 95, 255 ) ; "
                        backGroundColorStyle = " background-color : rgba( 35, 35, 35, 255 ) ; "

                    hoverStyle = " QPushButton:hover{  border: 1px solid rgb(48,226,227);} "
                    style = "QPushButton {  " + foreColor + backGroundColorStyle + test +" border: 1px " + borderType + " rgba( 30,30,30, 255) ;}"
                    colorLabel.setStyleSheet(style + hoverStyle)

            else :
                if idx == 0 : # [] * 

                    """
                    colorLabel = QtGui.QLabel( parent = self)
                    colorLabel.setAutoFillBackground(True)
                    colorLabel.setMaximumWidth(8)
                    colorLabel.setMaximumHeight(11)
                    
                    underLayout.addWidget(colorLabel )
                    style = "QLabel {  background-color : rgba( 71,101,125, 0 ) ; "+test +" border: 2px " + borderType + " rgba( 30,30,30, 255) ;}"
                    colorLabel.setStyleSheet(style)
                    """

                    statusLabel = QtGui.QLabel( parent = self)
                    statusLabel.setText(a["name"])
                    self.mainLabel = statusLabel
                    self.labelList.append(statusLabel)

                    font = statusLabel.font()
                    font.setPointSize(9);
                    #font.setWeight( QtGui.QFont.Bold )
                    statusLabel.setFont(font)
                    underLayout.addWidget(statusLabel )


                    
                    if a["status"] == "opn"  :
                        foreColor =  "color : rgb(210,210,210);"
                    elif a["status"] == "ip" :
                        foreColor = "color : rgb(60,60,30);"
                    else :
                        foreColor =  "color : rgb(150,150,150);"



                    borderType = " none "
                    styleAlign =  " "
                    style = "QLabel {  " + styleAlign + foreColor + "background-color : rgba( 71,101,125, 0 ) ; "+test +" border: 1px " + borderType + " rgba( 30,30,30, 255) ;}"
                    statusLabel.setStyleSheet(style)
                
                    self.normalStyle = style
                    self.highlightStyle = "QLabel {  " + styleAlign + " color :rgb(48,226,227) ; " + "background-color : rgba( 71,101,125, 0 ) ; "+test +" border: 2px " + borderType + " rgba( 30,30,30, 255) ;}"
                    self.litStyle =  "QLabel {  " + styleAlign + " color :rgb(230,230,230) ; " + "background-color : rgba( 71,101,125, 0 ) ; "+test +" border: 2px " + borderType + " rgba( 30,30,30, 255) ;}"

                else :
                    
                    colorLabel = QtGui.QPushButton( parent = self)
                    colorLabel.setAutoFillBackground(True)
                    colorLabel.setMaximumWidth(10)
                    colorLabel.setMaximumHeight(13)

                    fct = lambda checked = False, noteId =  a['id'], taskName = a["name"] : parent.selectNote_from_id( noteId, taskName )
                    colorLabel.clicked.connect(fct)
                    colorLabel.enterEvent = lambda event, noteId = a['id'], parentTree = parent : self.my_enterEvent(event, noteId, parentTree) 
                    colorLabel.leaveEvent = lambda event, noteId = a['id'], parentTree = parent : self.my_leaveEvent(event, noteId, parentTree) 


                    statusLabel = QtGui.QLabel( parent = self)
                    statusLabel.setText(a["name"])
                    self.labelList.append(statusLabel)

                    font = statusLabel.font()
                    font.setPointSize(8);
                    statusLabel.setFont(font)

                    underLayout.addWidget(colorLabel )
                    underLayout.addWidget(statusLabel )



                    if a["status"] == "opn"  :
                        backGroundColorStyle = " background-color : rgba( 71,101,125, 255 ) ; "
                        backGroundColorStyle = " background-color : rgba( 40,141,223, 255 ) ; "
                    elif a["status"] == "ip" :
                        backGroundColorStyle = " background-color : rgba( 173,155, 93, 255 ) ; "
                        backGroundColorStyle = " background-color : rgba( 218,183, 98, 255 ) ; "
                    else :
                        backGroundColorStyle = " background-color : rgba( 95, 95, 95, 255 ) ; "
                        backGroundColorStyle = " background-color : rgba( 35, 35, 35, 255 ) ; "

                    hoverStyle = " QPushButton:hover{  border: 1px solid rgb(48,226,227);} "
                    style = "QPushButton { "+ backGroundColorStyle + " "+test +" border: 1px " + borderType + " rgba( 30,30,30, 255) ;}"
                    colorLabel.setStyleSheet(style + hoverStyle)
                    


                    if childNoteTasks[0]["status"] == "opn"  :
                        foreColor =  "color : rgb(210,210,210);"
                    elif childNoteTasks[0]["status"] == "ip" :
                        foreColor = "color : rgb(60,60,30);"
                    else :
                        foreColor =  "color : rgb(150,150,150);"

                    borderType = " none "
                    styleAlign =  " "
                    style = "QLabel {  " + styleAlign + foreColor + "background-color : rgba( 71,101,125, 0 ) ; "+test +" border: 2px " + borderType + " rgba( 30,30,30, 255) ;}"
                    statusLabel.setStyleSheet(style)

            idx+=1

        layout.addStretch()

    def setMyLabelColor(self, state) :
        if state :
            self.mainLabel.setStyleSheet(self.highlightStyle)

        else :
            if self.isSelected :
                self.mainLabel.setStyleSheet(self.litStyle)
            else :
                self.mainLabel.setStyleSheet(self.normalStyle)


    def my_enterEvent(self, event , noteID, parentTree ) :

        items = parentTree.findItems("note_%i"%noteID,  QtCore.Qt.MatchRecursive,10 )
        for item in items :
            item.taskLinksWidget.setMyLabelColor(True)

    def my_leaveEvent(self, event , noteID, parentTree ) :

        items = parentTree.findItems("note_%i"%noteID,  QtCore.Qt.MatchRecursive,10 )
        for item in items :
            item.taskLinksWidget.setMyLabelColor(False)

    def lit(self, isSelected):
        self.isSelected = isSelected
        for lab in self.labelList :
            if isSelected :
                lab.setStyleSheet(self.litStyle)
            else :
                lab.setStyleSheet(self.normalStyle) 

class noteWidget(QtGui.QTreeWidgetItem) :

   ### @decorateur_try_except
    def __init__(self, parent, sgData, taskFilterWidget, filterWidget, typeFilterWidget,  userNameFilterWidget, contentFilterWidget, entityAssignedFilterWidget, shotAssetFilterWidget  ):

        super(noteWidget, self).__init__(parent )

        self.statusColor = None
        #print sgData
        self.taskParsedName = "NoTask"
        self.taskLinksWidget = None
        self.sgData = sgData
        self.filterWidget = filterWidget
        self.userNameFilterWidget = userNameFilterWidget
        self.contentFilterWidget = contentFilterWidget
        self.entityAssignedFilterWidget = entityAssignedFilterWidget
        self.taskFilterWidget = taskFilterWidget
        self.shotAssetFilterWidget = shotAssetFilterWidget

        content = "None"
        if sgData["content"] :
            content = unicode(sgData["content"] , "utf-8")

        sg_noteType = "NoType"
        if sgData["sg_note_type"] :
            sg_noteType = str(sgData["sg_note_type"])

        self.setText(10, "note_%i"%sgData["id"] )
        self.setText(0, content )
        #self.setIcon(0, QtGui.QIcon( getRessources("asset.png" ) ))
        nullPic = QtGui.QPixmap(1,5)
        nullPic.fill( QtGui.QColor( 0,0,0,0)  )
        self.setIcon(0, QtGui.QIcon( nullPic))
        #self.setSizeHint(0, QtCore.QSize(100,100) )

        masterTaskName = "NoTask"
        if sgData["tasks"] :
            masterTaskName = self.taskFilterWidget.retrieveNameFromValue( sgData["tasks"][0]["name"] ) 
        
        self.taskParsedName = masterTaskName

        childNoteTasks = []
        if sgData.has_key("spawnedDict") :
            if sgData["spawnedDict"].has_key("masterSpawn") :
                masterTask = { "name" : self.taskFilterWidget.retrieveNameFromValue( masterTaskName ) , "status" : sgData["sg_status_list"], "type":"master"    }
                childNoteTasks.append(masterTask)
                for childNote in sgData["spawnedDict"]["masterSpawn"] :
                    childNoteTaskName = "NoTask"
                    if childNote["tasks"] :
                        childNoteTaskName = self.taskFilterWidget.retrieveNameFromValue( childNote["tasks"][0]["name"] )
                    childNoteTasks.append(  { "name" : childNoteTaskName , "status" : childNote["sg_status_list"], "id":childNote["id"] , "type":"child"    } )

            elif sgData["spawnedDict"].has_key("spawnFrom"):
                
                masterTask = { "name"  : self.taskFilterWidget.retrieveNameFromValue( masterTaskName ) ,"status" : sgData["sg_status_list"], "type":"child"    }
                childNoteTasks.append(masterTask)
                childNoteTaskName ="NoTask"
                if sgData["spawnedDict"]["spawnFrom"]["tasks"] :
                    childNoteTaskName = self.taskFilterWidget.retrieveNameFromValue( sgData["spawnedDict"]["spawnFrom"]["tasks"][0]["name"] )
                childNoteTasks.append(  { "name"  : childNoteTaskName , "status" : sgData["spawnedDict"]["spawnFrom"]["sg_status_list"], "id":sgData["spawnedDict"]["spawnFrom"]["id"], "type":"master" } )

                for siblingNote in sgData["spawnedDict"]["spawnSiblings"] : 
                    childNoteTaskName = "NoTask"
                    if siblingNote["tasks"] :
                        childNoteTaskName = self.taskFilterWidget.retrieveNameFromValue( siblingNote["tasks"][0]["name"] )
                    childNoteTasks.append(  { "name" : childNoteTaskName , "status" : siblingNote["sg_status_list"], "id":siblingNote["id"] , "type":"child"    } )

        if not childNoteTasks :
            self.setText(1, self.taskFilterWidget.retrieveNameFromValue( masterTaskName ) )
            #font = QtGui.QFont("" , 9 , QtGui.QFont.Bold )
            #self.setFont(1, font)
        else :
            self.taskLinksWidget =  taskLinks( childNoteTasks , parent = self.treeWidget() ) 
            self.treeWidget().setItemWidget( self, 1 , self.taskLinksWidget)

        self.setText(2, sg_noteType )

        #self.setIcon(2, QtGui.QIcon( QtGui.QPixmap(getRessources(typeFilterWidget.retrieveIconFromValue( sg_noteType ))).scaled ( 16, 16, QtCore.Qt.KeepAspectRatio ) ) )
        self.setText(3, str(sgData["created_at"].strftime("%Y-%m-%d %H:%M"))  )
        self.setText(9, str(sgData["created_at"].strftime("%Y-%m-%d %H:%M"))  )
        self.setText(3, str("patapouf")  )
        self.setText(4, str(sgData["user"]["name"] )  )
        self.setText(6, str(sgData["shotCode"] )  )
        self.set_my_bacgroundColor()
        self.do_hidding()

        self.setExpanded(False)

        self.textBox = False
        self.editing_text = None

    def litTaskLink(self):

        if self.taskLinksWidget :
            self.taskLinksWidget.lit(self.isSelected())


    def getSpawnedFrom(self) :
        if self.sgData.has_key("spawnedDict") :
            if self.sgData["spawnedDict"].has_key("spawnFrom"):
                return self.sgData["spawnedDict"]["spawnFrom"]

        return None



    def getSpawnedTaskNote(self) :

        if self.sgData.has_key("spawnedDict") :
            spawnedDict = {}
            if self.sgData["spawnedDict"].has_key("masterSpawn") :
                for a in  self.sgData["spawnedDict"]["masterSpawn"] :
                    keyName = "NoTask"
                    if a["tasks"] :
                        keyName = self.taskFilterWidget.retrieveNameFromValue( a["tasks"][0]["name"] )
                    spawnedDict[keyName] = a
            else :
                keyName = "NoTask"
                if self.sgData["spawnedDict"]["spawnFrom"]["tasks"] :
                    keyName = self.taskFilterWidget.retrieveNameFromValue(self.sgData["spawnedDict"]["spawnFrom"]["tasks"][0]["name"])
                spawnedDict[keyName] = self.sgData["spawnedDict"]["spawnFrom"]
                
                for a in  self.sgData["spawnedDict"]["spawnSiblings"] :
                    keyName = "NoTask"
                    if a["tasks"] :
                        keyName = self.taskFilterWidget.retrieveNameFromValue( a["tasks"][0]["name"] )
                    spawnedDict[keyName] = a

            return spawnedDict
        else :
            return {}

        return {}
    def setEditableMode(self, editable) :
        self.setHidden(True)
        if editable :

            self.textBox = QtGui.QTextEdit()
            self.textBox.setPlainText(self.text(0) )
            self.treeWidget().setItemWidget( self, 0 , self.textBox )
            self.editing_text = self.text(0)
            self.setText(0, "")
        
        else :


            if self.textBox :
                text = self.textBox.toPlainText()
                self.treeWidget().removeItemWidget( self, 0 )
                self.setText( 0,  text )

                if self.editing_text != self.text(0) :

                    if not isinstance(text, unicode):
                        text =  unicode ( text.toUtf8(), "utf-8" )

                    self.treeWidget().SIGNAL_updateNoteContent.emit( [text, self.sgData['id'] ] )


        self.setHidden(False)



    
    def setTextColor(self, color, bold = False):
        font = QtGui.QFont("" , 9 , QtGui.QFont.Bold )
        b = QtGui.QBrush(color)
        self.setForeground( 5 , b );
        
        if bold :
            self.setFont( 5, font );


    def setMultiColor( self, foreColor, backColor ):

        self.setForeground(0, foreColor)
        self.setForeground(1, foreColor)
        self.setForeground(2, foreColor)
        self.setBackground(3, foreColor)
        self.setForeground(4, foreColor)
        self.setForeground(5, foreColor)
        self.setForeground(6, foreColor)
        self.setForeground(7, foreColor)
        self.setForeground(8, foreColor)
        self.setForeground(9, foreColor)


        self.setBackground(0, backColor)
        self.setBackground(1, backColor)
        self.setBackground(2, backColor)
        self.setBackground(3, backColor)
        self.setBackground(4, backColor)
        self.setBackground(5, backColor)
        self.setBackground(6, backColor)
        self.setBackground(7, backColor)
        self.setBackground(8, backColor)
        self.setBackground(9, backColor)

    def set_my_bacgroundColor(self ): 


        backColor = QtGui.QColor(0, 191, 255, 25)
        foreColor = QtGui.QBrush( QtGui.QColor(210,210,210) )

        if self.sgData["sg_status_list"] == "opn" : # bleur
            backColor = QtGui.QColor(115,195,255, 100)

            self.setMultiColor(foreColor, backColor )

            if str(self.text(11)) == "False" :
                self.setTextColor(QtGui.QColor(250,250,210), bold = True)
            else :
                self.setTextColor(QtGui.QColor(210,210,210))

        elif self.sgData["sg_status_list"] == "ip" : # orange FFA500
            backColor = QtGui.QColor(250,220,122, 160)

            foreColor = QtGui.QBrush( QtGui.QColor(60,60,30) )
            self.setMultiColor(foreColor, backColor )

            if str(self.text(11)) == "False" :
                self.setTextColor(QtGui.QColor(60,60,30), bold = True)
            else :
                self.setTextColor(QtGui.QColor(40,40,00))


        elif self.sgData["sg_status_list"] == "clsd" : # vert
            backColor = QtGui.QColor(95, 95, 95, 100)

            foreColor = QtGui.QBrush( QtGui.QColor(150,150,150) )
            self.setMultiColor(foreColor, backColor )

            if str(self.text(11)) == "False" :
                self.setTextColor(QtGui.QColor(210,210,210))
            else :
                self.setTextColor(QtGui.QColor(150,150,150))
        else :
            self.setMultiColor(foreColor, backColor )

        self.statusColor = backColor



    ### @decorateur_try_except
    def updateData(self, dataDict ):
        self.sgData.update( dataDict )
        self.set_my_bacgroundColor()
        self.do_hidding()

    
    def __lt__(self, otherItem):
        column = self.treeWidget().sortColumn()


        if column == 0 :

            orig  = self.sgData["sg_status_list"]      + str(self.sgData["created_at"])
            other = otherItem.sgData["sg_status_list"] + str(otherItem.sgData["created_at"])
            return orig < other
        elif column == 1 :
            orig  = self.taskParsedName +  str( self.sgData["sg_note_type"] )      + self.sgData["sg_status_list"] + str(self.sgData["created_at"])
            other = otherItem.taskParsedName +  str( otherItem.sgData["sg_note_type"] ) + otherItem.sgData["sg_status_list"] + str(otherItem.sgData["created_at"])
            return orig < other 

        elif column == 2 :
            orig  = str(self.sgData["sg_note_type"])      + self.sgData["sg_status_list"] + str(self.sgData["created_at"])
            other = str(otherItem.sgData["sg_note_type"]) + otherItem.sgData["sg_status_list"] + str(otherItem.sgData["created_at"])
            return orig < other

        elif column == 9 :
            orig  = str(self.sgData["created_at"])
            other = str(otherItem.sgData["created_at"])
            return orig < other
        elif column == 5 :
            orig  = str(self.text(11))  + str(self.text(column)) 
            other = str(otherItem.text(11))  + str(otherItem.text(column)) 
            return orig < other
        elif column == 7 :
            orig  = int(self.text(7))
            other = int(otherItem.text(7))
            return orig < other
        else :
            orig  = str(self.text(column)) + self.sgData["sg_status_list"]
            other = str(otherItem.text(column)) +  otherItem.sgData["sg_status_list"]
            return orig < other

        return QtGui.QTreeWidgetItem.__lt__(self, otherItem)




    def checkFilterShotAsset(self) :
        filterText = self.shotAssetFilterWidget.getText()


        text = self.text(6)
        if not isinstance(text, unicode):
            text = unicode(self.text(6).toUtf8() , "utf-8" ) 

        if not filterText :
            return False
        else :
            if text.upper().find( filterText.upper() ) +1 :
                return False
            elif text.find( filterText )  + 1 :
                return False
            else :
                return True


    def checkFilterStatus(self) :
        if not self.filterWidget.getfilterList() :
            
            return True
        else :
            if self.sgData["sg_status_list"] in self.filterWidget.getfilterList() :
                return False
            else :
                return True


    def checkFilterContent(self):
        filterText = self.contentFilterWidget.getText()

        text = self.text(0)
        if not isinstance(text, unicode):
            text = unicode(self.text(0).toUtf8() , "utf-8" ) 

        if not filterText :
            return False
        else :
            if text.upper().find( filterText.upper() ) +1 :
                return False
            elif text.find( filterText )  + 1 :
                return False
            else :
                return True


    def checkFilterUser(self) :
        filterText = self.userNameFilterWidget.getText()
        
        text = self.text(4)
        if not isinstance(text, unicode):
            text = unicode(self.text(4).toUtf8() , "utf-8" ) 
    
        if not filterText :
            return False
        else :
            if text.upper().find( filterText.upper() ) +1 :
                return False
            elif text.find( filterText )  + 1 :
                return False
            else :
                return True

    def checkFilterAssigned(self) :
        filterText = self.entityAssignedFilterWidget.getText()
        text = self.text(8)
        if not isinstance(text, unicode):
            text = unicode(self.text(8).toUtf8() , "utf-8" ) 
    
        if not filterText :
            return False
        elif text == "" :
            return False

        else :
            if text.upper().find( filterText.upper() ) +1 :
                return False
            elif text.find( filterText )  + 1 :
                return False
            else :
                return True

    def checkFilterTasks(self) :
        if not self.taskFilterWidget.getfilterList() :
            
            return True
        else :
            testTask = "NoTask" 
            if self.sgData["tasks"] :
                testTask = self.sgData["tasks"][0]["name"]
            if testTask in self.taskFilterWidget.getfilterList() :
                return False
            else :
                return True

    ### @decorateur_try_except
    def do_hidding(self, getState = False) :

        status  = self.checkFilterStatus()
        user    = self.checkFilterUser() 
        content = self.checkFilterContent()
        assignedTo = self.checkFilterAssigned()
        task = self.checkFilterTasks()
        shot = self.checkFilterShotAsset()

        if not status and not user and not content and not assignedTo and not task and not shot :
            self.setHidden(False)
            return False
        else :
            self.setHidden(True)
            return True


class emptyWidget(QtGui.QTreeWidgetItem):
    def __init__(self, parent ):
        super(emptyWidget, self).__init__(parent )
        self.sgData = None

        self.setText(0, "" )
        self.setText(10, "EMPTYNOTE" )
    def __lt__(self, otherItem):
        if QtCore.Qt.AscendingOrder == self.treeWidget().header().sortIndicatorOrder() :
        
            return 0
        else :
            return  1

class taskWidget(QtGui.QTreeWidgetItem) :

    ### @decorateur_try_except
    def __init__(self, parent, sgData, filterWidget ):


        super(taskWidget, self).__init__(parent )

        self.filterWidget = filterWidget

        self.statusColor = QtGui.QColor(85,85,85)

        self.sgData = sgData
        self.sgData['id'] = 0
        #self.setText(10, "task_%s"%sgData["name"] )
        self.setText(10, "task_dontCarre" )
        

        font = QtGui.QFont("" , 9 , QtGui.QFont.Bold )
        self.setFont( 0, font );


        self.setText(0, str(sgData["name"])  )
        self.setText(0, "Create New note"  )
        #self.setText(1, str(0) )


        ressources = QtGui.QPixmap(  getRessources( "add_notes.png" ) )
        
        for dataEntries in self.filterWidget.entriesDictList :
            if self.sgData["name"] in dataEntries["values"] :
                   ressources = QtGui.QPixmap( getRessources(dataEntries["icon"])    )  




        ressources =  ressources.scaled (32, 32, QtCore.Qt.KeepAspectRatio)
        
        self.setMysizeHint()
        self.setIcon(0, QtGui.QIcon(  ressources ) )
        self.setExpanded(True)
        

        backColor = QtGui.QColor(85, 85, 85, 255)
        self.setBackground(0, backColor)
        self.setBackground(1, backColor)
        self.setBackground(2, backColor)
        self.setBackground(3, backColor)
        self.setBackground(4, backColor)
        self.setBackground(5, backColor)
        self.setBackground(6, backColor)
        self.setBackground(7, backColor)
        self.setBackground(8, backColor)
        self.setBackground(9, backColor)



        self.do_hidding()



    def setMysizeHint( self ) :
        self.setSizeHint(0, QtCore.QSize(0,0))
        self.setSizeHint(1, QtCore.QSize(0,0))
        self.setSizeHint(2, QtCore.QSize(0,0))
        self.setSizeHint(3, QtCore.QSize(0,0))
        self.setSizeHint(4, QtCore.QSize(0,0))
        self.setSizeHint(5, QtCore.QSize(0,0))
        self.setSizeHint(6, QtCore.QSize(0,0))
        self.setSizeHint(7, QtCore.QSize(0,0))
        self.setSizeHint(8, QtCore.QSize(0,0))
        self.setSizeHint(9, QtCore.QSize(0,0))

    ### @decorateur_try_except
    def findItems(self, text, method,col) :
        matchItem = []
        for child_idx in range(self.childCount()) :
            childItem = self.child(child_idx) 
            if str(childItem.text(col)).startswith( text ) :
                matchItem.append(childItem)

        return matchItem

    def find_all_notesId(self) :
        idNoteList = []
        for child_idx in range(self.childCount()) :
            childItem = self.child(child_idx) 
            
            if childItem.sgData :
                idNoteList.append(childItem.sgData["id"])

        return idNoteList

    def __lt__(self, otherItem):

        if QtCore.Qt.AscendingOrder == self.treeWidget().header().sortIndicatorOrder() :
        
            return 1
        else :
            return  0




        currentIdx = self.filterWidget.retrieveIndiceFromValue(self.text(0))
        otherIdx = self.filterWidget.retrieveIndiceFromValue(otherItem.text(0) )

        if QtCore.Qt.AscendingOrder == self.treeWidget().header().sortIndicatorOrder() :
        
            return currentIdx<otherIdx
        else :
            return  currentIdx>otherIdx
        """
        if self.text(0) == "NoTask" :
            return 1
        else : 
            return 0
        """

    def do_hidding(self) :
        self.setHidden(False)
        self.setExpanded(True)

        return
        """
        if self.text(0) == "NoTask" :
            self.setHidden(False)
            self.setExpanded(True)
            return False 
        """
        if not self.filterWidget.getfilterList() :
           self.setHidden(False)
           self.setExpanded(True)
           return False 
        else :
            if self.sgData["name"] in self.filterWidget.getfilterList() :
                self.setHidden(False)
                self.setExpanded(True)
                return False
            else :
                self.setHidden(False)
                self.setExpanded(True)
                return True



class sequenceWidget(QtGui.QTreeWidgetItem) :


    def __init__(self, parent, sgData ):
        super(sequenceWidget, self).__init__(parent )

        self.sgData = sgData

        self.setText(10, "sequence_%i"%sgData["id"] )
        self.setText(0, str(sgData["name"])  )

        self.setIcon(0, QtGui.QIcon( getRessources(u"sequence.png" ) ) )
        self.setExpanded(False)

    def getShotWidgetList(self) :
        matchItem = []
        for child_idx in range(self.childCount()) :
            matchItem.append(self.child(child_idx) )

        return matchItem

    def __lt__(self, otherItem):

        #if QtCore.Qt.AscendingOrder == self.treeWidget().header().sortIndicatorOrder() :
        orig  =  str(self.sgData["type"])+ str(self.sgData["name"])
        other = str(otherItem.sgData["type"]) + str(otherItem.sgData["name"])
        if QtCore.Qt.AscendingOrder == self.treeWidget().header().sortIndicatorOrder() :
            return orig > other
        else :
            return orig < other

class assetWidget(QtGui.QTreeWidgetItem) :


    def __init__(self, parent, sgData ):
        super(assetWidget, self).__init__(parent )

        self.sgData = sgData

        self.setText(10, "assetType_%s"%sgData["name"] )
        self.setText(0, str(sgData["name"])  )

        self.setIcon(0, QtGui.QIcon( getRessources(u"asset.png" ) ) )
        self.setExpanded(False)

    def getShotWidgetList(self) :
        matchItem = []
        for child_idx in range(self.childCount()) :
            matchItem.append(self.child(child_idx) )

        return matchItem

    def __lt__(self, otherItem):

        #if QtCore.Qt.AscendingOrder == self.treeWidget().header().sortIndicatorOrder() :
        orig  =  str(self.sgData["type"])+ str(self.sgData["name"])
        other = str(otherItem.sgData["type"]) + str(otherItem.sgData["name"])
        if QtCore.Qt.AscendingOrder == self.treeWidget().header().sortIndicatorOrder() :
            return orig > other
        else :
            return orig < other


class shotAssetWidget(QtGui.QTreeWidgetItem) :
    x = 128
    y = 128
    def __init__(self, parent, sgData, entityType ):
        super(shotAssetWidget, self).__init__(parent )

        self.sgData = sgData
        self.sgData["sgAvailableTaskList"] = None


        self.setText(10, "shotAsset_%i"%sgData["id"]  )
        self.setText(0, str(sgData["code"])  )



    def do_filterText(self, filterText ) :

        
        text = self.text(0)
        if not isinstance(text, unicode):
            text = unicode(self.text(0).toUtf8() , "utf-8" ) 
    
        if not filterText :
            return False
        else :
            if text.upper().find( filterText.upper() ) +1 :
                return False
            elif text.find( filterText )  + 1 :
                return False
            else :
                return True


    def do_filterAssignees(self, taskAssigneesText) :
        

        if not self.sgData.has_key("sgAvailableAssignees") :
            return False

        text = " ".join( self.sgData["sgAvailableAssignees"] )
        if not isinstance(text, unicode):
            text = unicode(text , "utf-8" ) 
 

        if not taskAssigneesText :
            return False
        else :
            if text.upper().find( taskAssigneesText.upper() ) +1 :
                return False
            elif text.find( taskAssigneesText )  + 1 :
                return False
            else :
                return True

    def do_filterTask(self, taskFilterList, taskAssigneesText  ) :



        if not self.sgData.has_key("sgtaskDictWithAssignees") :
            return False

        availableTaskList = self.sgData["sgtaskDictWithAssignees"].keys()


        if not taskFilterList and not taskAssigneesText :
            return False
        else :
            
            #print taskFilterList
            for taskFilter in taskFilterList :
                
                if taskFilter == "NoTask" :
                    if len(taskFilterList)>1 :
                        if not availableTaskList :
                            return False
                    else :
                        return False
                
                if taskFilter in availableTaskList :
                    if not taskAssigneesText :
                        return False
                  
                    text = " ".join( self.sgData["sgtaskDictWithAssignees"][taskFilter] )
                    if text.upper().find( taskAssigneesText.upper() ) +1 :
                        return False
                    else : 
                        pass
                

            return True



    def do_hidding( self, filterText, taskAssigneesText, taskFilterList ) :


        shotAssetChecked  = self.do_filterText(filterText)
        taskChecked = None
        if taskFilterList :
            taskChecked = self.do_filterTask(taskFilterList, taskAssigneesText )
        else :
            taskChecked = self.do_filterAssignees(taskAssigneesText)



        if not taskChecked and not shotAssetChecked :
            self.setHidden(False)
            return False
        else :
            self.setHidden(True)
            return True





    def findItems(self, text, method,col) :
        matchItem = []
        for child_idx in range(self.childCount()) :
            childItem = self.child(child_idx) 
            if childItem.text(col) == text :
                matchItem.append(childItem)

        return matchItem


    def __lt__(self, otherItem):


        orig  =  str(self.sgData["code"])
        other = str(otherItem.sgData["code"]) 
        return orig > other











