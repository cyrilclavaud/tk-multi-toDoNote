# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk
import os
import sys
import threading

# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.
from sgtk.platform.qt import QtCore, QtGui
from .ui.dialog import Ui_Dialog

from .ui import noteManager



def show_dialog(app_instance):
    """
    Shows the main dialog window.
    """
    # in order to handle UIs seamlessly, each toolkit engine has methods for launching
    # different types of windows. By using these methods, your windows will be correctly
    # decorated and handled in a consistent fashion by the system. 
    
    # we pass the dialog class to this method and leave the actual construction
    # to be carried out by toolkit.

    AppDialog = noteManager.noteManager.Example


    
    app_instance.engine.show_dialog("To-Do Note App", app_instance, AppDialog )    

    dialog = QtGui.QApplication.activeWindow()
    flags = QtCore.Qt.Window

    flags |= QtCore.Qt.WindowTitleHint
    flags |= QtCore.Qt.WindowSystemMenuHint   
    flags |= QtCore.Qt.WindowMinimizeButtonHint
    flags |= QtCore.Qt.WindowMaximizeButtonHint
    flags |= QtCore.Qt.WindowCloseButtonHint
    flags |= QtCore.Qt.WindowContextHelpButtonHint
    flags |= QtCore.Qt.WindowShadeButtonHint
    flags |= QtCore.Qt.WindowStaysOnTopHint
    
    dialog.setWindowFlags(flags) 
    dialog.show()
