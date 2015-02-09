#!/usr/bin/python
# -*- coding: utf-8 -*-

import traceback
import os
import sys

try :
    import sgtk
    app =  sgtk.platform.current_bundle() 
    from sgtk.platform.qt import QtCore, QtGui

    _signal = QtCore.Signal 
    outFileName = "side"

    tempPath = app.cache_location
    userName = app.context.user
    if not userName :
        userName = "user_unknown"
    else :
        userName = "user_"+str(userName["id"])

    userTempPath = os.path.join(tempPath, userName  )

except :
    from PyQt4 import QtGui, QtCore
    _signal = QtCore.pyqtSignal
    outFileName = "cute"

    tempPath = os.environ["TEMP"]
    userTempPath =  os.path.join(tempPath, "user_dev" )



def decorateur_try_except(fonction_a_decorer):
    
    def wrapper_fonction_a_decorer( *args, **kwargs ):
        #plog(str(args[0].__class__.__name__ +"."+ fonction_a_decorer.__name__) + "\n")
        try :
            return fonction_a_decorer( *args, **kwargs )

        except :
            perr( "########  %s ######\n%s\n\n"%(fonction_a_decorer.__name__,str(traceback.format_exc())) )

    return wrapper_fonction_a_decorer


def plog(text, clear = None):
    a = None
    filename = os.path.join(getUserTempPath(),"LOG_"+outFileName+".txt" ) 
    if clear : 
        a = open(filename, "w")
    else :     
        a = open(filename, "a")

    a.write(text)
    a.close()


def perr(text, clear = None):

    a = None
    filename = os.path.join(getUserTempPath(),"ERR_"+outFileName+".txt" ) 
    if clear : 
        a = open(filename, "w")
    else :     
        a = open(filename, "a")

    a.write(text)
    a.close()


def pprint(text, clear = None) :

    a = None
    filename = os.path.join(getUserTempPath(),"PR_"+outFileName+".txt" ) 
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
    if not os.path.isdir(tempPath) :
        os.makedirs(tempPath)
    return tempPath


def getUserTempPath():
    if not os.path.isdir(userTempPath) :
        os.makedirs(userTempPath)
    return userTempPath



def getPathToImagePlugins():
    return "Z:/sharedPython2.6/site-packages_win64/PyQt4/plugins"

def getPathToShotgunApi():

    path = ""
    if sys.platform == "darwin":
        path = "/mnt/shared/Dev/cyril/python/PACKAGES"

    elif sys.platform == "linux2":
        path = "Z:/Dev/cyril/python/PACKAGES"

    elif sys.platform == "win32":
        path = "Z:/Dev/cyril/python/PACKAGES"

    if os.path.exists(path) :
        return path
    else : 
        None




def OS_convertPath(path):
    if sys.platform == "darwin":
        return path

    elif sys.platform == "linux2":
        return path

    elif sys.platform == "win32":
        return path.replace( "//server01/shared2/"  , "S:\\")


