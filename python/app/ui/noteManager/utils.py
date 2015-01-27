#!/usr/bin/python
# -*- coding: utf-8 -*-

import traceback
import os



try :
    #from PySide  import QtCore, QtGui
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
    try  :
        return os.path.join(os.path.dirname(__file__),u"bin",filename)
    except :
        return "c:/temp/ressources/%s"%filename

def getRessources(filename):

    try  :
        return os.path.join(os.path.dirname(__file__),u"ressources",filename)
    except :
        return "c:/temp/ressources/%s"%filename

def getTempPath():
    return os.environ[u'TEMP']


