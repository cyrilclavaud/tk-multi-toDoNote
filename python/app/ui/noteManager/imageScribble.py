#!/usr/bin/python
# -*- coding: utf-8 -*-

import utils
from utils import *

try :
    from sgtk.platform.qt import QtCore, QtGui
    _signal = QtCore.Signal 
    QtCore.QCoreApplication.addLibraryPath( getPathToImagePlugins() )

except :
    from PyQt4 import QtGui, QtCore
    _signal = QtCore.pyqtSignal





class ScribbleArea(QtGui.QWidget):


    def __init__(self, parent=None):
        super(ScribbleArea, self).__init__(parent)

        self.setAttribute(QtCore.Qt.WA_StaticContents)
        self.modified = False
        self.scribbling = False
        self.myPenWidth = 3
        self.myPenColor = QtCore.Qt.red
        
        imageSize = QtCore.QSize(500, 500)

        
        self.image = QtGui.QImage(imageSize,  QtGui.QImage.Format_RGB32)

        
        self.lastPoint = QtCore.QPoint()

    @decorateur_try_except
    def openImage(self, fileName):
        loadedImage = QtGui.QImage()
        if not loadedImage.load(fileName):
            return False


        self.image = loadedImage

        if not self.image.format() == QtGui.QImage.Format_RGB32 :
            self.image = self.image.convertToFormat( QtGui.QImage.Format_RGB32 )
            #print "converting "

        imWidth  = self.image.width()
        imHeight = self.image.height()
        print imWidth, imHeight
        if imHeight  > 1080 :
            ratio = float(imHeight)/1080.0
            #print ratio
            self.resizeImage(self.image, QtCore.QSize(  imWidth/ratio, 1080 ) )
            #print imWidth/ratio, 1080


        w = self.image.width()
        h = self.image.height()    
        self.mainWindow.resize(w, h)
        self.mainWindow.setMinimumSize(w,h)
        self.mainWindow.setMaximumSize(w,h)

        self.modified = False
        self.update()
        return True


    def overWrite(self, fileName) :
        visibleImage = self.image
        self.resizeImage(visibleImage, self.size())

        if visibleImage.save(fileName, quality = 100) :
            return True
        else:
            return False

    def saveImage(self, fileName, fileFormat):
        visibleImage = self.image
        self.resizeImage(visibleImage, self.size())

        if visibleImage.save(fileName, fileFormat):
            self.modified = False
            return True
        else:
            return False

    def setPenColor(self, newColor):
        self.myPenColor = newColor

    def setPenWidth(self, newWidth):
        self.myPenWidth = newWidth

    def clearImage(self):
        self.image.fill(QtGui.qRgb(255, 255, 255))
        self.modified = True
        self.update()

    def mousePressEvent(self, event):

        if event.button() == QtCore.Qt.LeftButton:
            self.lastPoint = event.pos()
            self.scribbling = True

    def mouseMoveEvent(self, event):
        if (event.buttons() & QtCore.Qt.LeftButton) and self.scribbling:
            self.drawLineTo(event.pos())

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.scribbling:
            self.drawLineTo(event.pos())
            self.scribbling = False

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawImage(QtCore.QPoint(0, 0), self.image)


    def drawLineTo(self, endPoint):
        painter = QtGui.QPainter(self.image)
        painter.setPen(QtGui.QPen(self.myPenColor, self.myPenWidth,
                QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        painter.drawLine(self.lastPoint, endPoint)
        self.modified = True

        rad = self.myPenWidth / 2 + 2
        self.update(QtCore.QRect(self.lastPoint, endPoint).normalized().adjusted(-rad, -rad, +rad, +rad))
        self.lastPoint = QtCore.QPoint(endPoint)

    def resizeImage(self, image, newSize):
        if image.size() == newSize:
            return


        newImage = QtGui.QImage(newSize, QtGui.QImage.Format_RGB32)
        newImage.fill(QtGui.qRgb(255, 255, 255))
        painter = QtGui.QPainter(newImage)
        painter.drawImage(QtCore.QPoint(0, 0), image)



        self.image = newImage

    def print_(self):
        printer = QtGui.QPrinter(QtGui.QPrinter.HighResolution)

        printDialog = QtGui.QPrintDialog(printer, self)
        if printDialog.exec_() == QtGui.QDialog.Accepted:
            painter = QtGui.QPainter(printer)
            rect = painter.viewport()
            size = self.image.size()
            size.scale(rect.size(), QtCore.Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(self.image.rect())
            painter.drawImage(0, 0, self.image)
            painter.end()

    def isModified(self):
        return self.modified

    def penColor(self):
        return self.myPenColor

    def penWidth(self):
        return self.myPenWidth


class MainWindow(QtGui.QMainWindow):
    SIGNAL_imageUpdate = _signal()
    
    def __init__(self, parent = None):
        super(MainWindow, self).__init__(parent )

        self.saveAsActs = []

        self.scribbleArea = ScribbleArea(self)
        self.scribbleArea.clearImage()
        self.scribbleArea.mainWindow = self  # maybe not using this?


        self.setCentralWidget(self.scribbleArea)

        self.createActions()
        self.createMenus()

        self.setWindowTitle("Scribble")
        self.resize(500, 500)

        self.imageFileName = None

    def closeEvent(self, event):
        event.accept()
        

    def open(self):
        if self.maybeSave():
            fileName = QtGui.QFileDialog.getOpenFileName(self, "Open File",
                QtCore.QDir.currentPath())
            if fileName:
                self.scribbleArea.openImage(fileName)

    def openImage(self, imageFileName) :
        self.imageFileName = imageFileName
        self.scribbleArea.openImage(self.imageFileName)


    def save(self):
        action = self.sender()
        fileFormat = action.data()
        self.saveFile(fileFormat)


    def saveOver(self):
        if self.scribbleArea.overWrite(self.imageFileName) :
            print "scribble saved"
            self.close()
            self.SIGNAL_imageUpdate.emit()


    def penColor(self):
        newColor = QtGui.QColorDialog.getColor(self.scribbleArea.penColor())
        if newColor.isValid():
            self.scribbleArea.setPenColor(newColor)

    def penWidth(self):
        newWidth, ok = QtGui.QInputDialog.getInteger(self, "Scribble",
            "Select pen width:", self.scribbleArea.penWidth(), 1, 50, 1)
        if ok:
            self.scribbleArea.setPenWidth(newWidth)

    def about(self):
        QtGui.QMessageBox.about(self, "About Scribble",
            "<p>The <b>Scribble</b> example shows how to use "
            "QMainWindow as the base widget for an application, and how "
            "to reimplement some of QWidget's event handlers to receive "
            "the events generated for the application's widgets:</p>"
            "<p> We reimplement the mouse event handlers to facilitate "
            "drawing, the paint event handler to update the application "
            "and the resize event handler to optimize the application's "
            "appearance. In addition we reimplement the close event "
            "handler to intercept the close events before terminating "
            "the application.</p>"
            "<p> The example also demonstrates how to use QPainter to "
            "draw an image in real time, as well as to repaint "
            "widgets.</p>")

    def createActions(self):
        self.openAct = QtGui.QAction("&Open...", self, shortcut="Ctrl+O",
            triggered=self.open)

        
        for format in QtGui.QImageWriter.supportedImageFormats():
            format = str(format)

            text = format.upper() + "..."

            action = QtGui.QAction(text, self, triggered=self.save)
            action.setData(format)
            self.saveAsActs.append(action)
        

        self.printAct = QtGui.QAction("&Print...", self,
            triggered=self.scribbleArea.print_)

        self.exitAct = QtGui.QAction("E&xit", self, shortcut="Ctrl+Q",
            triggered=self.close)
        
        self.saveOverAct = QtGui.QAction("Save and Exit", self, shortcut="Ctrl+S",
            triggered=self.saveOver)


        self.penColorAct = QtGui.QAction("&Pen Color...", self,
            triggered=self.penColor)

        self.penWidthAct = QtGui.QAction("Pen &Width...", self,
            triggered=self.penWidth)

        self.clearScreenAct = QtGui.QAction("&Clear Screen", self,
            shortcut="Ctrl+L", triggered=self.scribbleArea.clearImage)

        self.aboutAct = QtGui.QAction("&About", self, triggered=self.about)

        self.aboutQtAct = QtGui.QAction("About &Qt", self,
            triggered=QtGui.qApp.aboutQt)

    def createMenus(self):

        self.saveAsMenu = QtGui.QMenu("&Save As", self)
        for action in self.saveAsActs:
            self.saveAsMenu.addAction(action)

        fileMenu = QtGui.QMenu("&File", self)
        #fileMenu.addAction(self.openAct)
        #fileMenu.addMenu(self.saveAsMenu)
        #fileMenu.addAction(self.printAct)
        fileMenu.addAction(self.saveOverAct)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAct)

        optionMenu = QtGui.QMenu("&Options", self)
        optionMenu.addAction(self.penColorAct)
        optionMenu.addAction(self.penWidthAct)
        #
        optionMenu.addSeparator()
        #optionMenu.addAction(self.clearScreenAct)

        helpMenu = QtGui.QMenu("&Help", self)
        helpMenu.addAction(self.aboutAct)
        #helpMenu.addAction(self.aboutQtAct)

        self.menuBar().addMenu(fileMenu)
        self.menuBar().addMenu(optionMenu)
        self.menuBar().addMenu(helpMenu)

    def maybeSave(self):
        if self.scribbleArea.isModified():
            ret = QtGui.QMessageBox.warning(self, "Scribble",
                "The image has been modified.\n"
                "Do you want to save your changes?",
                QtGui.QMessageBox.Save | QtGui.QMessageBox.Discard |
                QtGui.QMessageBox.Cancel)
            if ret == QtGui.QMessageBox.Save:
                return self.saveFile('png')
            elif ret == QtGui.QMessageBox.Cancel:
                return False

        return True


    def saveFile(self, fileFormat):
        initialPath = QtCore.QDir.currentPath() + '/untitled.' + fileFormat

        fileName = QtGui.QFileDialog.getSaveFileName(self, "Save As",
            initialPath,
            "%s Files (*.%s);;All Files (*)" % (fileFormat.upper(), fileFormat))
        if fileName:
            return self.scribbleArea.saveImage(fileName, fileFormat)

        return False

"""
if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.openImage("c:/temp/ok.jpg")
    window.show()
    sys.exit(app.exec_())
"""