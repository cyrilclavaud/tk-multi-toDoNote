#!/usr/bin/python
# -*- coding: utf-8 -*-

import traceback
import os
import sys

try :
    from sgtk.platform.qt import QtCore, QtGui
    _signal = QtCore.Signal 
    outFileName = "side"

except :
    from PyQt4 import QtGui, QtCore
    _signal = QtCore.pyqtSignal
    outFileName = "cute"




def decorateur_try_except(fonction_a_decorer):
    
    def wrapper_fonction_a_decorer( *args, **kwargs ):
        try :
            return fonction_a_decorer( *args, **kwargs )

        except :
            perr( "########  %s ######\n%s\n\n"%(fonction_a_decorer.__name__,str(traceback.format_exc())) )

    return wrapper_fonction_a_decorer


def plog(text, clear = None):
    a = None
    filename = os.path.join(getTempPath(),"LOG_"+outFileName+".txt" ) 
    if clear : 
        a = open(filename, "w")
    else :     
        a = open(filename, "a")

    a.write(text)
    a.close()


def perr(text, clear = None):

    a = None
    filename = os.path.join(getTempPath(),"ERR_"+outFileName+".txt" ) 
    if clear : 
        a = open(filename, "w")
    else :     
        a = open(filename, "a")

    a.write(text)
    a.close()


def pprint(text, clear = None) :

    a = None
    filename = os.path.join(getTempPath(),"PR_"+outFileName+".txt" ) 
    if clear : 
        a = open(filename, "w")
    else :     
        a = open(filename, "a")
 
    a.write(text)
    a.close()



def getExec(filename):
    return os.path.join(os.path.dirname(__file__),u"bin",filename)

def getRessources(filename):
    return os.path.join(os.path.dirname(__file__),u"ressources",filename)

def getTempPath():
    return os.environ[u'TEMP']

def getPathToImagePlugins():
    return "Z:/sharedPython2.6/site-packages_win64/PyQt4/plugins"

def getPathToShotgunApi():
    return "Z:/Dev/cyril/python/PACKAGES"

def OS_convertPath(path):
    if sys.platform == "darwin":
        return path


    elif sys.platform == "linux2":
        return path


    elif sys.platform == "win32":
        return path.replace( "//server01/shared2/"  , "S:\\")


