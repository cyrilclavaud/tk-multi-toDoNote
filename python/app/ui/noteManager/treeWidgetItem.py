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




class comboFilterWidget2(QtGui.QWidget):


    SIGNAL_currentIndexesChanged = _signal(object)

    def __init__(self, typeDict , entriesDictList , showLabel = True, multiCheckable = False, parent = None ):
        super(comboFilterWidget2, self).__init__(parent )


        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)

        self.typeDict = typeDict
        self.entriesDictList = entriesDictList

        self.multiCheckable = multiCheckable

        if showLabel :
            label = QtGui.QLabel( typeDict["name"] )
            icon  = QtGui.QLabel()
            icon.setPixmap(  QtGui.QPixmap(getRessources(typeDict["icon"])).scaled ( 16, 16, QtCore.Qt.KeepAspectRatio )  )
            icon.setMaximumWidth(16)
            layout.addWidget(icon)
            layout.addWidget(label)
    
        self.widget = QtGui.QComboBox()
        self.widget.setItemDelegate(QtGui.QItemDelegate(self ))

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
                    self.widget.setEnabled(False)


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
            self.widget.setEnabled(False)

        layout.addWidget(self.widget)
        if self.multiCheckable :        
            self.widget.currentIndexChanged.connect(self.sendCheckedIndexes)
   

    def eventFilter(self, obj, event) :


        if ( event.type() == QtCore.QEvent.MouseButtonRelease and obj == self.widget.view().viewport() ) :
            self.widget.repaint()
            return True
        
        return False

    

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
            return self.entriesDictList[self.widget.currentIndex()]["values"]
    
    @decorateur_try_except
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

    @decorateur_try_except
    def retrieveValueFromName(self, name):
        for entriesDict  in  self.entriesDictList :
            if name in entriesDict["values"] :
                return  entriesDict["values"]
        return name




    @decorateur_try_except
    def retrieveNameFromValue(self, value) :
        #return value

        for entriesDict  in  self.entriesDictList :
            if value in entriesDict["values"] :
                return  entriesDict["text"]
        return value
    
    @decorateur_try_except
    def retrieveDictFromSelection(self):

        return self.retrieveValueFromName(self.widget.currentText())
    
    @decorateur_try_except
    def retrieveDict(self):
        return self.typeDict, self.entriesDictList[1:]


    @decorateur_try_except
    def setFromValue(self, name ) :
        idx = 0
        idx = self.widget.findText(name)
        self.widget.setCurrentIndex(idx)
        
    @decorateur_try_except
    def setMyCurrentIndex(self, index ):


        self.widget.setCurrentIndex(0) 
        self.widget.setEnabled(True)






    ##################################### 
    def getSoloChecked(self):
        checkedIndexList = self.getCheckedIndexes()
        if len( checkedIndexList ) == 1 :
            if not 0 in checkedIndexList :
                return self.entriesDictList[checkedIndexList[0]]["values"]
            else :
                return None

        return None


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

    @decorateur_try_except
    def sendCheckedIndexes(self, index):

        self.SIGNAL_currentIndexesChanged.emit( self.getCheckedIndexes() )


    def currentCheckedIndexes(self):
        checkedIndexes = self.getCheckedIndexes()
        if not checkedIndexes :
            return range(len(self.entriesDictList)-1)[0]
        else :
            return checkedIndexes[0]

    @decorateur_try_except
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

    @decorateur_try_except
    def setMyCurrentFromIndexes(self, indexList ):

        self.widget.blockSignals(True)
        self.widget.clear()

        idx = 1
        for entryDict in self.entriesDictList :
            if idx in  indexList :
                if entryDict["icon"] :
                    self.widget.addItem( QtGui.QIcon(getRessources( entryDict["icon"] ) ), entryDict["text"]  )
                else :
                    self.widget.addItem(  entryDict["text"]   )
            idx+=1

        self.widget.blockSignals(False)


        self.widget.currentIndexChanged.emit(0)
        
        if self.widget.count()==1:
            self.widget.setEnabled(False)
        else :
            self.widget.setEnabled(True)
        


class lineEditFilterWidget(QtGui.QWidget) :

    #@decorateur_try_except
    def __init__(self, typeDict , parent = None ):

        super(lineEditFilterWidget, self).__init__(parent )

        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)

        label = QtGui.QLabel( typeDict["name"] )
        icon  = QtGui.QLabel()
        icon.setPixmap(  QtGui.QPixmap(getRessources(typeDict["icon"])).scaled ( 16, 16, QtCore.Qt.KeepAspectRatio )  )

        self.widget = QtGui.QLineEdit()

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

class noteWidget(QtGui.QTreeWidgetItem) :

    #@decorateur_try_except
    def __init__(self, parent, sgData, filterWidget, typeFilterWidget,  userNameFilterWidget, contentFilterWidget, entityAssignedFilterWidget  ):

        super(noteWidget, self).__init__(parent )


        self.sgData = sgData
        self.filterWidget = filterWidget
        self.userNameFilterWidget = userNameFilterWidget
        self.contentFilterWidget = contentFilterWidget
        self.entityAssignedFilterWidget = entityAssignedFilterWidget

        content = "None"
        if sgData["content"] :
            content = unicode(sgData["content"] , "utf-8")

        sg_noteType = "NoType"
        if sgData["sg_note_type"] :
            sg_noteType = str(sgData["sg_note_type"])

        self.setText(10, "note_%i"%sgData["id"] )
        self.setText(0, content )


        self.setText(2, sg_noteType )

        self.setIcon(2, QtGui.QIcon( QtGui.QPixmap(getRessources(typeFilterWidget.retrieveIconFromValue( sg_noteType ))).scaled ( 16, 16, QtCore.Qt.KeepAspectRatio ) ) )
        self.setText(3, str(sgData["created_at"].strftime("%Y-%m-%d %H:%M"))  )
        self.setText(4, str(sgData["user"]["name"] )  )
        self.setText(6, str(sgData["shotCode"] )  )
        self.set_my_bacgroundColor()
        self.do_hidding()

        self.setExpanded(False)

        self.textBox = False
        self.editing_text = None

    #@decorateur_try_except
    def setEditableMode(self, editable) :

        if editable :
            print "edit"
            self.textBox = QtGui.QTextEdit()
            self.textBox.setPlainText(self.text(0) )
            self.treeWidget().setItemWidget( self, 0 , self.textBox )
            self.editing_text = self.text(0)
            self.setText(0, "")
        
        else :
            print "close"

            if self.textBox :
                text = self.textBox.toPlainText()
                self.treeWidget().removeItemWidget( self, 0 )
                self.setText( 0,  text )

                if self.editing_text != self.text(0) :
                    print "change"
                    if not isinstance(text, unicode):
                        text =  unicode ( text.toUtf8(), "utf-8" )

                    self.treeWidget().SIGNAL_updateNoteContent.emit( [text, self.sgData['id'] ] )
                else :
                    print "no change"


    
    def setTextColor(self, color, bold = False):
        font = QtGui.QFont("" , 9 , QtGui.QFont.Bold )
        b = QtGui.QBrush(color)
        self.setForeground( 5 , b );
        
        if bold :
            self.setFont( 5, font );


    def set_my_bacgroundColor(self ): 


        backColor = QtGui.QColor(0, 191, 255, 25)

        if self.sgData["sg_status_list"] == "opn" : # rouge
            #backColor = QtGui.QColor(255, 0, 0, 45)
            backColor = QtGui.QColor(115,195,255, 100)
        elif self.sgData["sg_status_list"] == "ip" : # orange
            #backColor = QtGui.QColor(255, 191, 0, 55)
            backColor = QtGui.QColor(223,210,122, 100)
            self.setHidden(True)

        elif self.sgData["sg_status_list"] == "clsd" : # vert
            #backColor = QtGui.QColor(0, 255, 0, 45)
            backColor = QtGui.QColor(95, 95, 95, 100)
        
        if str(self.text(11)) == "False" :
            self.setTextColor(QtGui.QColor(250,250,210), bold = True)
        else :
            self.setTextColor(QtGui.QColor(210,210,210))


        self.setBackground(0, backColor)
        self.setBackground(1, backColor)
        self.setBackground(2, backColor)
        self.setBackground(3, backColor)
        self.setBackground(4, backColor)
        self.setBackground(5, backColor)
        self.setBackground(6, backColor)
        self.setBackground(7, backColor)
        self.setBackground(8, backColor)

    #@decorateur_try_except
    def updateData(self, dataDict ):
        self.sgData.update( dataDict )
        self.set_my_bacgroundColor()
        self.do_hidding()

    @decorateur_try_except
    def __lt__(self, otherItem):
        column = self.treeWidget().sortColumn()


        if column == 0 :
            orig  = self.sgData["sg_status_list"]      + str(self.sgData["created_at"])
            other = otherItem.sgData["sg_status_list"] + str(otherItem.sgData["created_at"])
            return orig < other
        elif column == 2 :
            orig  = str(self.sgData["sg_note_type"])      + self.sgData["sg_status_list"] + str(self.sgData["created_at"])
            other = str(otherItem.sgData["sg_note_type"]) + otherItem.sgData["sg_status_list"] + str(otherItem.sgData["created_at"])
            return orig < other

        elif column == 3 :
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


    #@decorateur_try_except
    def do_hidding(self, getState = False) :

        status  = self.checkFilterStatus()
        user    = self.checkFilterUser() 
        content = self.checkFilterContent()
        assignedTo = self.checkFilterAssigned()

        if not status and not user and not content and not assignedTo:
            self.setHidden(False)
            return False
        else :
            self.setHidden(True)
            return True

        

class groupNoteWidget(QtGui.QTreeWidgetItem) :

    def __init__(self, parent, sgData ):
        super(groupNoteWidget, self).__init__(parent )

        self.sgData = sgData

        self.setText(10, "bookmark_%i"%sgData["id"] )
        self.setText(0, str(sgData["name"])  )

        self.setIcon(0, QtGui.QIcon( getRessources(u"bookmark.png" ) ) )
        self.setExpanded(False)




class typeNoteWidget(QtGui.QTreeWidgetItem) :
    #@decorateur_try_except
    def __init__(self, parent, sgData, filterWidget, group ):

        super(typeNoteWidget, self).__init__(parent )


        self.sgData = sgData
        self.filterWidget = filterWidget

        self.typeStr = "NoType"
        
        if sgData["name"]:
            self.typeStr = sgData["name"]


        if group :
            self.setText(10, "type_%s"%sgData["name"] )

        else :
            self.setText(10, "type_")
            self.typeStr = "all Type"
            self.setMysizeHint()


        self.setText(0, str( self.typeStr)  )

        ressources = QtGui.QPixmap( getRessources( self.filterWidget.typeDict["icon"] ) )
        for dataEntries in self.filterWidget.entriesDictList :
            if self.typeStr in dataEntries["values"] :
                   ressources = QtGui.QPixmap( getRessources(dataEntries["icon"]) )

        ressources =  ressources.scaled (16, 16, QtCore.Qt.KeepAspectRatio)

        self.setIcon(0, QtGui.QIcon(ressources ) )
        self.setExpanded(False)
    
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
    def __lt__(self, otherItem):
        return 0


    def do_hidding(self) :


        if not self.filterWidget.getfilterList() :
           self.setHidden(True)
           self.setExpanded(True)
           return False 
        else :
            if self.typeStr == "all Type" :

                self.setHidden(False)
                self.setExpanded(True)

                for child_idx in range(self.childCount()) :
                    childItem = self.child(child_idx) 

                    if str(childItem.text(2)) in self.filterWidget.getfilterList() :
                        childItem.setHidden(False)
                        childItem.do_hidding()
                    else : 
                        childItem.setHidden(True)

                return True

            elif self.typeStr in self.filterWidget.getfilterList() :
                self.setHidden(False)
                self.setExpanded(True)
                return False

            else :
                self.setHidden(True)
                self.setExpanded(False)
                return True


class taskWidget(QtGui.QTreeWidgetItem) :

    #@decorateur_try_except
    def __init__(self, parent, sgData, filterWidget ):


        super(taskWidget, self).__init__(parent )

        self.filterWidget = filterWidget

        self.sgData = sgData

        self.setText(10, "task_%s"%sgData["name"] )
        
        

        


        self.setText(0, str(sgData["name"])  )
        self.setText(1, str(0) )


        ressources = QtGui.QPixmap(  getRessources( self.filterWidget.typeDict["icon"] ) )
        
        for dataEntries in self.filterWidget.entriesDictList :
            if self.sgData["name"] in dataEntries["values"] :
                   ressources = QtGui.QPixmap( getRessources(dataEntries["icon"])    )  




        ressources =  ressources.scaled (32, 32, QtCore.Qt.KeepAspectRatio)


        self.setIcon(0, QtGui.QIcon(  ressources ) )
        self.setExpanded(False)
        self.do_hidding()


    #@decorateur_try_except
    def findItems(self, text, method,col) :
        matchItem = []
        for child_idx in range(self.childCount()) :
            childItem = self.child(child_idx) 
            if str(childItem.text(col)).startswith( text ) :
                matchItem.append(childItem)

        return matchItem

    def __lt__(self, otherItem):
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
        """
        if self.text(0) == "NoTask" :
            self.setHidden(False)
            self.setExpanded(True)
            return False 
        """
        if not self.filterWidget.getfilterList() :
           self.setHidden(True)
           self.setExpanded(True)
           return False 
        else :
            if self.sgData["name"] in self.filterWidget.getfilterList() :
                self.setHidden(False)
                self.setExpanded(True)
                return False
            else :
                self.setHidden(True)
                self.setExpanded(False)
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



class shotAssetWidget(QtGui.QTreeWidgetItem) :
    x = 128
    y = 128
    def __init__(self, parent, sgData ):
        super(shotAssetWidget, self).__init__(parent )

        self.sgData = sgData

        self.setText(10, "shotAsset_%i"%sgData["id"]  )
        self.setText(0, str(sgData["code"])  )


    def findItems(self, text, method,col) :
        matchItem = []
        for child_idx in range(self.childCount()) :
            childItem = self.child(child_idx) 
            if childItem.text(col) == text :
                matchItem.append(childItem)

        return matchItem


