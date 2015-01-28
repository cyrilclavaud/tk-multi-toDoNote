#!/usr/bin/python
# -*- coding: utf-8 -*-

import subprocess
import tempfile
import os
import sys

import utils
from utils import *

try :
    from sgtk.platform.qt import QtCore, QtGui
    _signal = QtCore.Signal 
    QtCore.QCoreApplication.addLibraryPath( getPathToImagePlugins() )

except :
    from PyQt4 import QtGui, QtCore
    _signal = QtCore.pyqtSignal



class ScreenshotThread(QtCore.QThread):
        """
        Wrap screenshot call in a thread just to be on the safe side!  
        This helps avoid the os thinking the application has hung for 
        certain applications (e.g. Softimage on Windows)
        """
        def __init__(self, path):
            QtCore.QThread.__init__(self)
            self._path = path
            self._error = None
            
        def get_error(self):
            return self._error
            
        def run(self):
            try:
                if sys.platform == "darwin":
                    # use built-in screenshot command on the mac
                    os.system("screencapture -m -i -s %s" % self._path)
                elif sys.platform == "linux2":
                    # use image magick
                    os.system("import %s" % self._path)
                elif sys.platform == "win32":
                    # use external boxcutter tool
                    bc = getExec("boxcutter.exe")
                    subprocess.check_call([bc, self._path])
            except Exception, e:
                self._error = str(e)


def take_a_screenShot() :
    path = None
    pm = None
    try:
        # get temporary file to use:
        # to be cross-platform and python 2.5 compliant, we can't use
        # tempfile.NamedTemporaryFile with delete=False.  Instead, we
        # use tempfile.mkstemp which does practically the same thing!
        tf, path = tempfile.mkstemp(suffix=".png", prefix="tanktmp")
        if tf:
            os.close(tf)

        # do screenshot with thread so we don't block anything
        screenshot_thread = ScreenshotThread(path)
        screenshot_thread.start()
        while not screenshot_thread.isFinished():
            screenshot_thread.wait(100)
            QtGui.QApplication.processEvents()

        er = screenshot_thread.get_error()
        if er:
            raise Exception("Failed to capture screenshot: %s" % er)
        

    finally :
        # remove the temporary file:
        if not path or not os.path.exists(path):

            path = None


    return path


