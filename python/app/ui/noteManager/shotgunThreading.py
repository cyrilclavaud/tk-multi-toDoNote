#!/usr/bin/python
# -*- coding: utf-8 -*-

import _strptime
import os
import sys
import re
import urllib
import copy
import hashlib

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

import time

############### THREADING CLASS ################# 

class sg_query(QtCore.QThread) :

    queue = None

    SERVER_PATH = "https://nozon.shotgunstudio.com"
    SCRIPT_NAME = 'noteManager'     
    SCRIPT_KEY = '3fbb2a5f180457af709fcad231c96ac8a916711427af5a06c47eb1758690f6e4'

    SIGNAL_queryAllShot = _signal(object)
    SIGNAL_queryAllAsset = _signal(object)

    SIGNAL_setNoteList = _signal(object)
    SIGNAL_setThumbnail = _signal(object)
    SIGNAL_clearTree = _signal(object)
    SIGNAL_queryNoteContent = _signal(object)
    SIGNAL_replyNote = _signal(object)
    SIGNAL_queryNoteVersion = _signal(object)
    SIGNAL_queryNoteTaskAssigned = _signal(object)
    SIGNAL_queryVersion = _signal(object)
    SIGNAL_addNote = _signal(object)
    SIGNAL_refreshNote = _signal(object)
    SIGNAL_setShotAsset_taskAssigned = _signal(object)

    SIGNAL_getAvailableTasks = _signal()


    SIGNAL_updateLaunchAppWidget = _signal(object)



    SIGNAL_pbar = _signal(int)

    th_id = 0



    ## @decorateur_try_except
    def __init__(self, app, parent = None ):

        super(sg_query, self).__init__( parent )


        self.sg_userDict = None

        if not app :
            sys.path.append( getPathToShotgunApi() )

            from shotgun_api3 import Shotgun
            self.sg = Shotgun(self.SERVER_PATH, self.SCRIPT_NAME, self.SCRIPT_KEY)
        
        else :
            #self.sg = app.engine.tank.shotgun # too slow
            path_to_shotgunApi = getPathToShotgunApi()
            if path_to_shotgunApi :
                sys.path.append( path_to_shotgunApi )
                from shotgun_api3 import Shotgun
                self.sg = Shotgun(self.SERVER_PATH, self.SCRIPT_NAME, self.SCRIPT_KEY)
                pprint("thread init \n" )
            else :
              
                self.sg = app.engine.tank.shotgun # too slow

            self.sg_userDict = app.context.user
            

        self.appLauncherDict = None
        self.project = None
        self.tempPath = None       
        self.tempPathAttachement = None
        self.tempPath_uploadAttachment = None
        self.typeFilterWidget = None


    def setTypeFilterWidget(self, typeFilterWidget ) :
        self.typeFilterWidget=typeFilterWidget 
        

        # set default project id 
    def setAppLauncher(self, appLauncherDict ) :
        self.appLauncherDict = appLauncherDict

    def setProjectId(self, projectId = 191 , useSGTK = True) :
        self.project = projectId
        
        sgTank = None
        if useSGTK :
            try :
                import sgtk
                sgTank= sgtk.sgtk_from_entity(  "Project", projectId)
                print "Tank Ok"
            except :
                pass
        self.tk =  sgTank

    def setTempPath(self) :
        self.tempPath = os.path.join( getTempPath(), u"tk_shotgun_toDoApp_%i"%self.project)
        
        self.tempPathAttachement = os.path.join( getTempPath(), u"tk_shotgun_toDoApp_%i"%self.project, u"attachment")


        if not os.path.isdir( self.tempPath ) :
            os.makedirs(self.tempPath)
    
        if not os.path.isdir( self.tempPathAttachement ) :
            os.makedirs(self.tempPathAttachement)



    def get_projectTaskList(self, task_entriesDictList ) :
        projectFilter = ['project','is', { 'type':'Project', 'id':self.project} ]
        print "\nRemoving tasks which doesnt belongs to this project..."
        tasksList = self.sg.find("Task", [projectFilter], ["content"] ) 
        taskContentList = []
        for  task in tasksList :
            if not task["content"] in taskContentList :
                taskContentList.append(task["content"])
        

        allTaskContentHandled = []
        new_task_entriesDictList = []

        for task_entriesDict in task_entriesDictList :
            foundValue = False
            foundValueName = None 
            if task_entriesDict["text"] == "All" or task_entriesDict["text"] == "NoTask":
                foundValue = True
            else :
                allTaskContentHandled.extend( task_entriesDict["values"] )
                for value in task_entriesDict["values"] :
                    if value in taskContentList :
                        foundValue = True
                        foundValueName = value
                

            if foundValue :

                new_task_entriesDictList.append(task_entriesDict)    
            else : 
                print "   " + task_entriesDict["text"] + " Removed "
        
        for sg_task in taskContentList :
            if not sg_task in allTaskContentHandled :
                print " /!\\ this sg_task : " + sg_task + " isnt handled by the toDo-Note configuration"


        print "OK\n"
        return new_task_entriesDictList


    ## @decorateur_try_except
    def setRunThreadCommand(self, stringCommandSwitch= u"downloadThumbnail", threadCommandArgs = None , threadCommandCallBack= None) :

        if stringCommandSwitch == u"downloadThumbnail" :
            self.downloadThumbnail(threadCommandArgs, threadCommandCallBack)

        if stringCommandSwitch == u"deleteEmptySpawnLink" :
            self.deleteEmptySpawnLink(threadCommandArgs, threadCommandCallBack)

        elif stringCommandSwitch ==u"queryNotes" :
            self.queryNotes(threadCommandArgs, threadCommandCallBack)

        elif stringCommandSwitch ==u"fillSeqShotTree" :
            self.queryAllShot(threadCommandArgs)

        elif stringCommandSwitch == u"clearTree"  :
            self.SIGNAL_clearTree.emit( [threadCommandArgs] )
        
        elif stringCommandSwitch == u"queryNoteContent" :
            self.queryNoteContent(threadCommandArgs, threadCommandCallBack)

        elif stringCommandSwitch == u"replyNote" :
            self.replyNote(threadCommandArgs, threadCommandCallBack) 

        elif stringCommandSwitch == u"multyReplyNote":
            self.multiReplyNote(threadCommandArgs, threadCommandCallBack)        

        elif stringCommandSwitch == u"queryNoteVersion" :
            self.queryNoteVersion(threadCommandArgs, threadCommandCallBack)

        elif stringCommandSwitch == u"setNoteStatus" :
            self.setNoteStatus(threadCommandArgs, threadCommandCallBack)

        elif stringCommandSwitch == u"setNoteType" : 
            self.setNoteType(threadCommandArgs, threadCommandCallBack)

        elif stringCommandSwitch == u"getVersion" :
            self.getVersion(threadCommandArgs, threadCommandCallBack )

        elif stringCommandSwitch == u"createNote" :
            self.createNote(threadCommandArgs, threadCommandCallBack )            

        elif stringCommandSwitch == u"editNoteContent" :
            self.editNoteContent(threadCommandArgs, threadCommandCallBack )  

        elif stringCommandSwitch == u"queryTaskAssigned" :
            self.queryTaskAssigned(threadCommandArgs, threadCommandCallBack )

        elif stringCommandSwitch == u"deleteNote" :
            self.deleteNote(threadCommandArgs, threadCommandCallBack)

        elif stringCommandSwitch == u"setNoteTask" :
            self.setNoteTask(threadCommandArgs, threadCommandCallBack)

        elif stringCommandSwitch == u"getExecutable" :
            #pass
            self.getExecutable(threadCommandArgs, threadCommandCallBack)

        elif stringCommandSwitch == u"setNoteLink" :
            self.setSpawnNote(threadCommandArgs, threadCommandCallBack)

        elif stringCommandSwitch == u"linkToLastVersion" :
            self.linkToLastVersion(threadCommandArgs, threadCommandCallBack )

        elif stringCommandSwitch == u"breakSpawnLink" :
            self.breakSpawnLink(threadCommandArgs, threadCommandCallBack )

        elif stringCommandSwitch == u"getAvailableTasks" :
            self.getAvailableTasks(threadCommandArgs, threadCommandCallBack )

        # SUB THREAD # called by the threading class
        elif stringCommandSwitch == u"queryNote_Masterspawn":
            self.queryNote_Masterspawn(threadCommandArgs, threadCommandCallBack )

        elif stringCommandSwitch == u"queryNote_spawned":
            self.queryNote_spawned(threadCommandArgs, threadCommandCallBack )



    ## @decorateur_try_except
    def getAvailableTasks(self, args = None, updateTree1_withFilter = None) :


        projectFilter = ['project','is', { 'type':'Project', 'id':self.project} ]
        entityFilter = ['entity', 'is',  { 'type': args[0]['type'] , 'id':args[0]['id']}   ]
        assigneesNameList = []
        result = self.sg.find("Task", [projectFilter,entityFilter ] , ["content", "task_assignees"])
        taskNameList = []
        assigneesList = []

        sgtaskDictWithAssignees = {}
        for task in result :
            perTaskAsignees = []
            taskNameList.append(task["content"])
            for user in task["task_assignees"] :
                assigneesList.append(user["name"] )
                perTaskAsignees.append(user["name"] )
            if not perTaskAsignees :
                perTaskAsignees = ["NoBody"]

            sgtaskDictWithAssignees[task["content"]] = perTaskAsignees



        args[1].sgData["sgAvailableAssignees"] =  assigneesList
        args[1].sgData["sgAvailableTaskList"]  = taskNameList
        args[1].sgData["sgtaskDictWithAssignees"] = sgtaskDictWithAssignees
        self.SIGNAL_getAvailableTasks.emit()


    ## @decorateur_try_except
    def queryTaskAssigned(self, shotSgData_taskList_noteId, callBack = None ) :

        projectFilter = ['project','is', { 'type':'Project', 'id':self.project} ]
        taskFilter =   [ 'content','in', shotSgData_taskList_noteId[1] ]
        entityFilter = ['entity', 'is',  { 'type': shotSgData_taskList_noteId[0]['type'] , 'id':shotSgData_taskList_noteId[0]['id']}   ]
        assigneesNameList = []
        result = self.sg.find_one("Task", [projectFilter,taskFilter,entityFilter ], ["task_assignees"] )
        if result :
            for assignessDict in  result["task_assignees"] :
                assigneesNameList.append(assignessDict["name"])
        else :
            assigneesNameList = ["NoTask"]

        if not assigneesNameList:
            assigneesNameList = ["Nobody"]



        #
        self.SIGNAL_queryNoteTaskAssigned.emit([ shotSgData_taskList_noteId[2], assigneesNameList ] )



    ## @decorateur_try_except
    def editNoteContent(self, list_note, callback = None ) :
        #[0] note content
        #[1] note id
        noteContent = list_note[0]
        self.sg.update("Note", list_note[1], {"content" :noteContent })



    ## @decorateur_try_except
    def queryAllShot(self, args = None,  callback = None): 

        projectFilter = ['project','is', { 'type':'Project', 'id':self.project} ]
        shotList = self.sg.find("Shot", [projectFilter], [u"code", u"image", u"sg_sequence" ])
        self.SIGNAL_queryAllShot.emit( shotList )

        
        assetList = self.sg.find("Asset", [projectFilter], [u"code", u"image", u"sg_asset_type" ])    
        self.SIGNAL_queryAllAsset.emit( assetList )
        

    ## @decorateur_try_except
    def downloadThumbnail(self, args = None, callback = None) :

        i = 0
        for entityDict in args :
            
            if entityDict['image'] :

                hash_object = hashlib.sha1(entityDict['image'].split("?")[0])
                hex_dig = hash_object.hexdigest()

                thumbNameFile = os.path.join( self.tempPath, u"thumbnail_%s_%i_%s.jpg"%( entityDict['type'] , entityDict['id'], hex_dig ) )

                if not os.path.isfile(thumbNameFile ):
                    urllib.urlretrieve(entityDict['image'], thumbNameFile)

                self.SIGNAL_setThumbnail.emit( [  "shotAsset_%i"%entityDict["id"], thumbNameFile ] )
            else :
                if entityDict.has_key("sg_asset_type") :
                    self.SIGNAL_setThumbnail.emit( [  "shotAsset_%i"%entityDict["id"], getRessources("emptyAsset.png") ] )
                else :
                    self.SIGNAL_setThumbnail.emit( [  "shotAsset_%i"%entityDict["id"], getRessources("emptyShot.png") ] )

    ## @decorateur_try_except
    def downloadVersionThumbnail(self, entityDict) :

        thumbNameFile = os.path.join( self.tempPath, u"Version_thumbnail_%s_%i.jpg"%( entityDict['type'] , entityDict['id'] ) )   
        if entityDict['image'] :
            if not os.path.isfile(thumbNameFile ):

                urllib.urlretrieve(entityDict['image'], thumbNameFile)
        return thumbNameFile

    ## @decorateur_try_except
    def queryNotes(self, args = None, callBack = None):




        ENTITY_TYPE = args['type']

        projectFilter  = ['project','is', { 'type':'Project', 'id':self.project} ]
        shotFilter     = ['note_links','is', { 'type': ENTITY_TYPE , 'id':args['id'] } ]

        sg_spawnedNotes = self.sg.find("CustomEntity04",[projectFilter, ["code","is", "link_%i"%args['id']], ['sg_note','is_not', None] ] ,    ["sg_note","sg_note_links"] )


        filterList = [projectFilter, shotFilter ]
        if args.has_key("getOnly_Notes") :
            filterList.append( ["id","in", args["getOnly_Notes"]] )

        noteList = []
        typeFilterList = self.typeFilterWidget.getfilterList()
        if typeFilterList  :
            if "NoType" in typeFilterList :
                typeFilter = { "filter_operator": "any", "filters" : [ ['sg_note_type', 'in', typeFilterList ], ['sg_note_type', 'is', None] ] }
            else :
                typeFilter = ['sg_note_type', 'in', typeFilterList ]

            filterList.append(typeFilter) # self.typeFilterWidget.getfilterList() ]) 
        

        noteList = self.sg.find("Note", filterList , ["sg_status_list","tag_list","sg_note_type","tasks", "subject", "created_at", "user", "content"] )

        soloNoteList = []

        for note in noteList :
            isSolo = True

            for sg_spawned in sg_spawnedNotes :
                spawnedDict  = {}

                if note['id'] == sg_spawned["sg_note"]["id"] :
                    note["spawnLinkId"] = sg_spawned["id"]
                    callBack = lambda note :  self.SIGNAL_setNoteList.emit(  [ [ "shotAsset_%i"%args["id"] , args['code'], args['id'], args['type']]  ,  [note] , args.has_key("getOnly_Notes") ] )
                    self.queue.put([ -1000, "queryNote_Masterspawn", [note, sg_spawned["sg_note_links"] ] , callBack ] ) 
                    isSolo = False 

                    break

                elif any(spawned_note['id'] ==  note['id'] for spawned_note in sg_spawned["sg_note_links"]) :
                    note["spawnLinkId"] = sg_spawned["id"]

                    callBack = lambda note :  self.SIGNAL_setNoteList.emit(  [ [ "shotAsset_%i"%args["id"] , args['code'], args['id'], args['type']]  ,  [note] , args.has_key("getOnly_Notes") ] )
                    
                    self.queue.put([ -1000, "queryNote_spawned", [note,  sg_spawned["sg_note"], sg_spawned["sg_note_links"] ] , callBack ] ) 
                    isSolo = False

                    break

            if isSolo :     

                soloNoteList.append(note)


        self.SIGNAL_setNoteList.emit(  [ [ "shotAsset_%i"%args["id"] , args['code'], args['id'], args['type']]  ,  soloNoteList , args.has_key("getOnly_Notes") ] )




    # called by self
    ## @decorateur_try_except
    def queryNote_Masterspawn(self, note_And_SpawnedList, callBack) :

        note = note_And_SpawnedList[0]
        spawnedList = note_And_SpawnedList[1]
        spawnedDict  = { "masterSpawn" : [] }

        for spawned in spawnedList :
            spawnedDict["masterSpawn"].append( self.getNoteWithStatus(spawned["id"]) )
        note["spawnedDict"] = spawnedDict

        callBack(note)

    # called by self
    ## @decorateur_try_except
    def queryNote_spawned(self, note_masterNote_And_SpawnedList, callBack) :
        note = note_masterNote_And_SpawnedList[0]


        masterNote = note_masterNote_And_SpawnedList[1]
        spawnedList = note_masterNote_And_SpawnedList[2]
        spawnedDict  = { "spawnFrom" : self.getNoteWithStatus( masterNote["id"]) , "spawnSiblings" : [] }


        for sibNote in  spawnedList :
            if sibNote["id"] !=  note['id'] :
                spawnedDict["spawnSiblings"].append( self.getNoteWithStatus( sibNote["id"] ) )   
        note["spawnedDict"] = spawnedDict
        callBack(note)

    ## @decorateur_try_except
    def getNoteWithStatus(self, noteId):
        projectFilter = ['project','is', { 'type':'Project', 'id':self.project} ]
        noteFilter = ['id','is',noteId ]
        filterList = [projectFilter, noteFilter]
        note = self.sg.find_one("Note", filterList, ["sg_status_list", "tasks"] )
        return note

    ## @decorateur_try_except
    def queryNoteContent(self, args = None, args2 = None) :


        projectFilter = ['project','is', { 'type':'Project', 'id':self.project} ]
        idNoteList = []
        for noteDict in args :
            idNoteList.append(noteDict["id"])

        noteFilter    = ['id','in', idNoteList ]

        sg_notecontent_List = []
        if idNoteList :
            sg_notecontent_tempList = self.sg.find("Note", [ projectFilter, noteFilter ] , ["attachments", "subject", "content", "user", "created_at", "updated_at", "sg_status_list", "replies", "note_links"] )
            
            for sgNote in sg_notecontent_tempList :

                taskValuesList = [] 
                for noteDict in args :
                    if  noteDict["id"] == sgNote["id"]:
                        taskValuesList = noteDict["taskValues"]


                eventNoteList = []

                replyNoteList = []
                replies_id_list = []
                for reply in sgNote["replies"] :
                    replies_id_list.append(reply['id'])
                if replies_id_list :
                    replyNoteList = self.sg.find("Reply", [ [ 'id','in', replies_id_list] ] , ["created_at", "user", "content" ] ) 

                attachementNoteList = []
                attachment_id_list = []
                for attachment in sgNote["attachments"] :
                    attachment_id_list.append(attachment['id'])
                if attachment_id_list :
                    attachementNoteList = self.sg.find("Attachment", [ [ 'id','in', attachment_id_list ] ] , ["created_at", "filename"]  )


                groupedList = self.merge_AttachementAndReplies(attachementNoteList, replyNoteList)
                sgNote["queriedAttachement"]= groupedList[0]

                if len(groupedList) > 1 :               
                    sgNote["queriedReplies"] = groupedList[1:]
                elif len(groupedList) == 1 :
                    sgNote["queriedReplies"] = []


                versionLinkList = []

                shotId = None
                shotType = None
                versionIdList = []

                for noteLink in sgNote["note_links"] : 
                    if noteLink["type"] == "Version" :
                        versionDict = self.sg.find_one( "Version", [ projectFilter, ['id','is', noteLink['id'] ] ] , ["sg_task","user", "created_at", "image", "sg_path_to_movie", "code"] )
                        versionDict["downloadedImage"] = self.downloadVersionThumbnail(versionDict)
                        versionDict["Title"] = "Version linked to the note"
                        versionLinkList.append( versionDict  )
                        versionIdList.append(versionDict['id'])
                    elif noteLink["type"] == "Shot" :
                        shotId = noteLink["id"]
                        shotType = "Shot" 
                    elif noteLink["type"] == "Asset" :
                        shotId = noteLink["id"]
                        shotType = "Asset"


                if shotId : #↨ and taskValuesList:
                    shotFilter    = ['entity','is', {'type': shotType, 'id':shotId } ]
                    taskFilter = []
                    
                    if not taskValuesList :
                        taskFilter.append( ['sg_task', 'is', None  ] )
                    else :
                        for taskName in taskValuesList:
                            if "NoTask" in taskName :
                                taskFilter.append( ['sg_task', 'is', None  ] )
                            else :
                                taskFilter.append( ['sg_task', 'name_contains', taskName  ] )

                    Complex_TaskFilter    ={
                        "filter_operator": "any",
                        "filters": taskFilter
                        }



                    orderList = [{'field_name':'id','direction':'desc'}]
                    lastVersionDictList = self.sg.find("Version", [projectFilter, shotFilter, Complex_TaskFilter ], fields = ["sg_task","user", "created_at", "image", "sg_path_to_movie", "code"] , limit = 1, order = orderList  )
                    if lastVersionDictList :
                        versionDict = lastVersionDictList[-1]
                        if not versionDict["id"] in versionIdList :            
                            versionDict["downloadedImage"] = self.downloadVersionThumbnail(versionDict)
                            versionDict["Title"] = "Last version"
                            versionLinkList.append(versionDict)             

                sgNote["note_links"] = versionLinkList

                sg_notecontent_List.append(sgNote)
      
        if args :
            if args[0].has_key('mustDisplay') :
                self.SIGNAL_queryNoteContent.emit(  [sg_notecontent_List, True] )                
            else :
                self.SIGNAL_queryNoteContent.emit(  [sg_notecontent_List, False] )

    ## @decorateur_try_except
    def queryNoteVersion(self, threadCommandArgs, threadCommandCallBack) :

        projectFilter = ['project','is', { 'type':'Project', 'id':self.project} ]

        shotId = threadCommandArgs[0]
        taskValuesList = threadCommandArgs[1]
        noteId = threadCommandArgs[2]
        shotType = threadCommandArgs[3]

        shotFilter    = ['entity','is', {'type': shotType, 'id':shotId } ]
        taskFilter = []
        for taskName in taskValuesList:
            if "NoTask" in taskName :
                taskFilter.append( ['sg_task', 'is', None  ] )
            else :
                taskFilter.append( ['sg_task', 'name_contains', taskName  ] )

        Complex_TaskFilter    ={
            "filter_operator": "any",
            "filters": taskFilter
            }



        orderList = [{'field_name':'id','direction':'desc'}]
        lastVersionDictList = self.sg.find("Version", [projectFilter, shotFilter, Complex_TaskFilter ], fields = ["sg_task","user", "created_at", "image", "sg_path_to_movie", "code"] , limit = 1, order = orderList  )
        lastVersionId = False
        if lastVersionDictList :
            lastVersionId = lastVersionDictList[0]["id"]



        projectFilter = ['project','is', { 'type':'Project', 'id':self.project} ]
        idNoteFilter = ['id','is', threadCommandArgs[2] ]
        linkIsVersionFilter = ['note_links', 'type_is' , ['Version'] ]


        value = self.sg.find_one("Note", [projectFilter , idNoteFilter ], ['note_links', 'replies'] )


        if value :
            versionString =""
            for noteLink in value["note_links"] :
                if noteLink["type"] == "Version" :
                    versionString = noteLink["name"] 
                    splits = re.findall(r' v\d+', noteLink["name"] )
                    if splits :
                        versionString = splits[-1]
                    

                    break

            if versionString :
                if noteLink["id"] == lastVersionId :
                    lastVersionId = True
                else :
                    lastVersionId = False
            else :
                lastVersionId = True

            self.SIGNAL_queryNoteVersion.emit( [threadCommandArgs[2],versionString, len( value["replies"]), lastVersionId ])

        #print threadCommandArgs, threadCommandCallBack

    ## @decorateur_try_except
    def downloadAttachement(self, attachementDict ) :


        attachmentFileName = os.path.join( self.tempPathAttachement, u"attachment_%i_%s"%(  attachementDict['id'], attachementDict['filename']  ) )
        if not os.path.isfile(attachmentFileName ) :
            self.sg.download_attachment(attachementDict, attachmentFileName ) 
        
        attachementDict["fileOnDisk"] = attachmentFileName

        return attachementDict

    ## @decorateur_try_except
    def merge_AttachementAndReplies(self, attachementNoteList, replyNoteList ) :
        mergeDict =  dict()
        for attachement in attachementNoteList :
            mergeDict[attachement["created_at"]] = attachement 
        for reply in replyNoteList :
            mergeDict[reply["created_at"]] = reply 


        groupList = []
        groupList.append( [] )

        eventType = None

        count = 0
        for dateKey in sorted(mergeDict.keys() ) :
            if eventType == None :
                if mergeDict[dateKey]["type"] == "Reply" :
                    groupList.append( mergeDict[dateKey] )
                    groupList[-1]["queriedAttachement"] = []
                    eventType = "Reply"                    
                else :
                    attachementDict = mergeDict[dateKey]
                    attachementDict = self.downloadAttachement(attachementDict)

                    groupList[0].append( attachementDict ) 

            else :
                if mergeDict[dateKey]["type"] == "Reply" :
                    groupList.append( mergeDict[dateKey] )
                    groupList[-1]["queriedAttachement"] = []
                else :
                    attachementDict = mergeDict[dateKey]
                    attachementDict = self.downloadAttachement(attachementDict)

                    groupList[-1]["queriedAttachement"].append(attachementDict)


        return groupList

    ## @decorateur_try_except
    def setNoteStatus(self, NoteData, threadCommandCallBack):


        projectFilter = ['project','is', { 'type':'Project', 'id':self.project} ]
        refresh_id_list = [ ]
        if NoteData[1].has_key("spawnLinkId") :

            spawnLink = self.sg.find_one("CustomEntity04",[projectFilter, ["id","is", NoteData[1]["spawnLinkId"] ]  ],  ["sg_note","sg_note_links"] )
            refresh_id_list= [spawnLink["sg_note"]["id"] ]
            for spawnedNote in spawnLink["sg_note_links"] :
                refresh_id_list.append(spawnedNote["id"])
        else :
            refresh_id_list = [ NoteData[0]['id'] ]


        self.sg.update("Note",NoteData[0]['id'], { 'sg_status_list':NoteData[0]["new_sg_status_list"] } )

        
        sgDataShot = {"id" : NoteData[1]["shotId"] , "code" : NoteData[1]["shotCode"] , "getOnly_Notes" : refresh_id_list, "type":NoteData[1]["shotType"] } 
        self.queue.put( [1, u"queryNotes"  , sgDataShot, None ] )


    ## @decorateur_try_except
    def setNoteType(self, NoteData , threadCommandCallBack):

        self.sg.update("Note",NoteData[0]['id'], { 'sg_note_type' : NoteData[0]["new_sg_note_type"] } )
        self.SIGNAL_refreshNote.emit( [NoteData[0], False ] )

    ## @decorateur_try_except
    def deleteNote(self, noteId, callback = None ) :
        self.sg.delete("Note", noteId[0] )
        self.SIGNAL_refreshNote.emit( [ {"id" : noteId[0] } , u"Delete" ] )

    ## @decorateur_try_except
    def linkToLastVersion(self, data, callBack = None):
        projectFilter = ['project','is', { 'type':'Project', 'id':self.project} ]

        shotId = data[0]
        taskValuesList = data[1]
        noteId = data[2]
        shotType = data[3]
        shotCode = data[4]
        statusState = data[5]


        shotFilter    = ['entity','is', {'type': shotType, 'id':shotId } ]
        lastVersionDictList = []
        if taskValuesList :
            taskFilter = []
            for taskName in taskValuesList:
                if "NoTask" in taskName :
                    taskFilter.append( ['sg_task', 'is', None  ] )
                else :
                    taskFilter.append( ['sg_task', 'name_contains', taskName  ] )

            Complex_TaskFilter    ={
                "filter_operator": "any",
                "filters": taskFilter
                }

            orderList = [{'field_name':'id','direction':'desc'}]
            lastVersionDictList = self.sg.find("Version", [projectFilter, shotFilter, Complex_TaskFilter ], fields = ["sg_task","user", "created_at", "image", "sg_path_to_movie", "code"] , limit = 1, order = orderList  )
        
        if lastVersionDictList :

            versionDict = lastVersionDictList[-1]
            shotDict = self.sg.find_one("Shot", [projectFilter, ["id",'is', shotId] ] )
            updateDataDict =  {"note_links" : [versionDict, shotDict ] }
            if statusState :
                updateDataDict['sg_status_list'] = statusState  
         
            self.sg.update("Note", noteId,  updateDataDict )
            
            sgDataShot = {"id" : shotId , "code" : shotCode , "getOnly_Notes" : [ noteId ], "type":data[3] } 
            self.queue.put( [1, u"queryNotes"  , sgDataShot, None ] )

        else :
   
            if statusState :

                updateDataDict = { 'sg_status_list': statusState } 

                self.sg.update("Note", noteId,  updateDataDict )
                sgDataShot = {"id" : shotId , "code" : shotCode , "getOnly_Notes" : [ noteId ], "type":data[3] } 
                self.queue.put( [1, u"queryNotes"  , sgDataShot, None ] )

                #self.SIGNAL_refreshNote.emit( [ {"id" : noteId} , False ] )
    ## @decorateur_try_except
    def replyNote(self, replyNoteData, threadCommandCallBack ) :

        dReply = {
                 'entity': {'type':'Note','id':replyNoteData[1]['id'] },
                 'content': replyNoteData[0]['content']
                 } 
        
        if self.sg_userDict :
            dReply.update({'user' : self.sg_userDict } )

        if  replyNoteData[0]['content']  != "" :       

            self.sg.create("Reply", dReply )




        for attachToUpload in replyNoteData[0]["uploads"] :

            self.sg.upload("Note", replyNoteData[1]['id'], attachToUpload )



        if replyNoteData[1].has_key("new_sg_status_list") :
            self.sg.update("Note",replyNoteData[1]['id'], { 'sg_status_list':replyNoteData[1]["new_sg_status_list"] } )





        self.SIGNAL_replyNote.emit(  [replyNoteData[1], True ] )


    ## @decorateur_try_except
    def multiReplyNote(self, multiReplyNoteData, threadCommandCallBack ) :

        
        for replyNoteData in multiReplyNoteData[1] :
            if  multiReplyNoteData[0]['content']  != "" :
                dReply= {'entity' : {'type':'Note','id':replyNoteData['id'] } , "content" : multiReplyNoteData[0]['content']  } 
                if self.sg_userDict :
                    dReply.update({'user' : self.sg_userDict } )          
                self.sg.create("Reply", dReply )

        
            for attachToUpload in multiReplyNoteData[0]["uploads"] :
                self.sg.upload("Note", replyNoteData['id'], attachToUpload )


            if multiReplyNoteData[1][0].has_key("new_sg_status_list") :
                self.sg.update("Note",replyNoteData['id'], { 'sg_status_list':multiReplyNoteData[1][0]["new_sg_status_list"] } )

            


            self.SIGNAL_replyNote.emit(  [ replyNoteData, False ] )


    ## @decorateur_try_except
    def getVersion(self, shotObj, threadCommandCallBack ) :

        projectFilter = ['project','is', { 'type':'Project', 'id':self.project} ]
        shotFilter    = ['entity','is', {'type': shotObj[0][1], 'id':shotObj[0][0]} ]
        taskFilter = []
        for taskName in shotObj[1] :
            if "NoTask" in taskName :
                taskFilter.append( ['sg_task', 'is', None  ] )
            else :
                taskFilter.append( ['sg_task', 'name_contains', taskName  ] )


        Complex_TaskFilter    ={
            "filter_operator": "any",
            "filters": taskFilter
            }



 
        lastVersionList = self.sg.find("Version", [projectFilter, shotFilter, Complex_TaskFilter ],["sg_task","user", "created_at", "image", "sg_path_to_movie", "code"] )[-5:]


        for versionDict in lastVersionList :
            versionDict["downloadedImage"] = self.downloadVersionThumbnail(versionDict)


        self.SIGNAL_queryVersion.emit( [ lastVersionList[::-1],shotObj[2]  ] )
    
    ## @decorateur_try_except
    def getExecutable(self, shotObjAndTaskValues_List, threadCommandCallBack ) :
        


        if not self.tk :
            return



        self.SIGNAL_updateLaunchAppWidget.emit( [{"clear" : True}, shotObjAndTaskValues_List[0], shotObjAndTaskValues_List[2], shotObjAndTaskValues_List[3], []] ) 

        projectFilter = ['project','is', { 'type':'Project', 'id':self.project} ]
        shotFilter    = ['entity','is', {'type': shotObjAndTaskValues_List[4], 'id': shotObjAndTaskValues_List[0]} ]

        taskDict = []
        if shotObjAndTaskValues_List[1] :
            taskDict = self.sg.find_one("Task", [ [ "content",'in', shotObjAndTaskValues_List[1] ], shotFilter ] ,  ["content", "step"] )


        new_appLauncherDict = copy.deepcopy( self.appLauncherDict )

        if taskDict and shotObjAndTaskValues_List[2] in new_appLauncherDict.keys() :

            
            for launcherApp in new_appLauncherDict[shotObjAndTaskValues_List[2]].keys() :

                template =  new_appLauncherDict[shotObjAndTaskValues_List[2]][launcherApp]["template"]


                sgshot_Code = self.sg.find_one(shotObjAndTaskValues_List[4], [ ['id','is',shotObjAndTaskValues_List[0]] ],  ["code"] )
                sgstep = self.sg.find_one("Step", [ ['id','is',taskDict['step']["id"]] ],  ["code","short_name"] )

                step = sgstep['short_name']

                
                work_template = self.tk.templates[template]
                # ' scenes/{Shot}/{Step}/work/{Shot}[_{name}]_v{version}.{maya_ext_work}'

                fields = {shotObjAndTaskValues_List[4] : sgshot_Code["code"], "Step": step }

                work_file_paths = self.tk.paths_from_template(work_template, fields, ["version" ], skip_missing_optional_keys=True)

                work_file_paths_withName_dict = {}
                work_file_paths_list = []
                for input_path in sorted( work_file_paths ) :

                    input_fields =  work_template.get_fields(input_path)
                    if input_fields.has_key("name") :
                        if work_file_paths_withName_dict.has_key(input_fields["name"]) :
                            work_file_paths_withName_dict[input_fields["name"]].append( input_path )
                        else :
                            work_file_paths_withName_dict[input_fields["name"]] = [ input_path ]
                    else :
                        work_file_paths_list.append(input_path)
                
                fileNameDictList = {}

                for k,v in work_file_paths_withName_dict.iteritems():
                    fileNameDictList[k] = sorted(v)[-5:][::-1]
                

                new_appLauncherDict[shotObjAndTaskValues_List[2]][launcherApp]["files"] = [ sorted(work_file_paths_list)[-5:][::-1], fileNameDictList,  taskDict['id'] ] 

            
        self.SIGNAL_updateLaunchAppWidget.emit( [new_appLauncherDict,shotObjAndTaskValues_List[0], shotObjAndTaskValues_List[2], shotObjAndTaskValues_List[3], taskDict ] ) 

    ## @decorateur_try_except
    def createNote(self, noteDictList, threadCommandCallBack = None) :

        for noteDict in noteDictList :

            # 0 the note dict
            # 1 the uploads
            # 2 the shot sgData
            # 3 taskList link
            subjectTaskStr = ""

            objectType = noteDict[2]["type"]

            if noteDict[3] :
                taskDict = self.sg.find_one("Task", [ [ "content",'in', noteDict[3] ], ["entity", "is", [{"type" : objectType, "id": noteDict[2]["id"] }]  ] ], ["content"] )
                if taskDict :
                    noteDict[0].update({"tasks" : [taskDict] }  )
                    subjectTaskStr = " on " + taskDict["content"]
                    
                    #noteDict[0].pop("note_links", None)

            noteDict[0].update( {'project' : {'type' : "Project" , 'id' : self.project } })

            if self.sg_userDict :
                noteDict[0].update({'user' : self.sg_userDict } )


            if not noteDict[0].has_key("subject" ) :
                if self.sg_userDict :
                    noteDict[0]["subject"] = self.sg_userDict["name"]+"'s note on " + noteDict[2]['code'] + subjectTaskStr 
                else :
                    noteDict[0]["subject"] = "Note on " + noteDict[2]['code'] + subjectTaskStr


            resultNote =  self.sg.create("Note", noteDict[0], ["sg_status_list","tag_list","sg_note_type","tasks", "subject", "created_at", "user", "content"] ) 
            
            if noteDict[1] : 
                for fileName in noteDict[1] :
                    self.sg.upload("Note", resultNote['id'], fileName )



            resultNote.update({"shotCode" : noteDict[2]['code'], "shotId" : noteDict[2]['id'], "shotType" : noteDict[2]['type'] } )
            self.SIGNAL_addNote.emit( [ resultNote ] )


    def deleteEmptySpawnLink(self, data = None, threadCommandCallBack = None ):
        print "checking improper spawned link entries..." 
        projectFilter = ['project','is', { 'type':'Project', 'id':self.project} ]
        Complex_TaskFilter    ={ "filter_operator": "any",  "filters": [['sg_note','is', None], ['sg_note_links', 'is', None]  ]   }
        spawnLinkList = self.sg.find("CustomEntity04",[projectFilter, Complex_TaskFilter  ] )
        for spawLink in spawnLinkList :
            self.sg.delete("CustomEntity04", spawLink['id'])
            print "deleting improper spawned link entries"
        
        if not spawnLinkList :
            print "OK\n" 


    ## @decorateur_try_except
    def breakSpawnLink(self, spawnLinkId_shotData, threadCommandCallBack = None) :
        projectFilter = ['project','is', { 'type':'Project', 'id':self.project} ]
        spawnLinkId = spawnLinkId_shotData[0]
        shotId = spawnLinkId_shotData[1]
        shotCode = spawnLinkId_shotData[2]
        shotType =  spawnLinkId_shotData[3]

        spawnLink = self.sg.find_one("CustomEntity04",[projectFilter, ["id","is", spawnLinkId ]  ],  ["sg_note","sg_note_links"] )
        refresh_id_list= [spawnLink["sg_note"]["id"] ]
        for spawnedNote in spawnLink["sg_note_links"] :
            refresh_id_list.append(spawnedNote["id"])


        self.sg.delete("CustomEntity04", spawnLinkId)
        
        sgDataShot = {"id" : shotId , "code" : shotCode , "getOnly_Notes" : refresh_id_list , "type": shotType  }  

        self.queue.put( [1, u"queryNotes"  , sgDataShot, None ] ) 

    ## @decorateur_try_except
    def setSpawnNote(self, noteSgData_taskValues_list,  threadCommandCallBack = None) :
        



        sg_task = self.sg.find_one("Task", [ [ "content",'in', noteSgData_taskValues_list[1]], ["entity", "is", [{"type" : noteSgData_taskValues_list[0]["shotType"], "id": noteSgData_taskValues_list[0]["shotId"] }]  ] ], ["content"] )
        
        subjectTaskStr = "NoTask"
        if sg_task :
            subjectTaskStr = sg_task["content"]

        from_subjectTaskStr = "NoTask"
        if noteSgData_taskValues_list[2] :
            if noteSgData_taskValues_list[2]["tasks"] :
                from_subjectTaskStr = noteSgData_taskValues_list[2]["tasks"][0]["name"]
        elif noteSgData_taskValues_list[0]["tasks"]:
           from_subjectTaskStr = noteSgData_taskValues_list[0]["tasks"][0]["name"]

        newNote = {} 
        newNote["subject"] = noteSgData_taskValues_list[0]["subject"]
        if self.sg_userDict :
            newNote["subject"] = noteSgData_taskValues_list[0]['shotCode'] + " " + subjectTaskStr + "'s note spawned from " + from_subjectTaskStr + " by " +self.sg_userDict["name"] 
        else :
            newNote["subject"] = noteSgData_taskValues_list[0]['shotCode'] + " " + subjectTaskStr + "'s note spawned from " + from_subjectTaskStr



        newNote["sg_status_list"] = "opn" #noteSgData_taskValues_list[0]["sg_status_list"]
        newNote["tag_list"] = noteSgData_taskValues_list[0]["tag_list"]
        newNote["sg_note_type"] = noteSgData_taskValues_list[0]["sg_note_type"]
        
        if sg_task :
            newNote["tasks"] =  [sg_task]
        
        if noteSgData_taskValues_list[2] :
            newNote["note_links"] = [ self.getNote_link( noteSgData_taskValues_list[2]["id"] ) ]
        else : 
            newNote["note_links"] = [ self.getNote_link( noteSgData_taskValues_list[0]["id"] ) ]


        newNote["user"] = noteSgData_taskValues_list[0]["user"]
        newNote["content"] = noteSgData_taskValues_list[0]["content"]
        newNote["project"] =  {'type' : "Project" , 'id' : self.project }
 


        resultNote =  self.sg.create("Note", newNote) #  ["sg_status_list","tag_list","sg_note_type","tasks", "subject", "created_at", "user", "content"]   ) 
        #resultNote.update({"shotCode" : noteSgData_taskValues_list[0]["shotCode"] , "shotId" : noteSgData_taskValues_list[0]["shotId"] } )


        projectFilter = ['project','is', { 'type':'Project', 'id':self.project} ]
        filterCode = ["code" , "is", "link_%i"%noteSgData_taskValues_list[0]["shotId"] ]

        noteEntityFilter = None
        if noteSgData_taskValues_list[2] :
            noteEntityFilter = ["sg_note", "is", noteSgData_taskValues_list[2] ]
        else :
            noteEntityFilter = ["sg_note", "is", noteSgData_taskValues_list[0] ]

        


        spawnLink = self.sg.find_one("CustomEntity04", [ projectFilter,filterCode, noteEntityFilter ],  ["sg_note_links","sg_note"] )


        spawnedNoteList = [resultNote]

        refresh_id_list = []
        if spawnLink :
            refresh_id_list.append(spawnLink["sg_note"]["id"])

            spawnedNoteList.extend(spawnLink["sg_note_links"])
            spawnLink = self.sg.update("CustomEntity04",spawnLink["id"], {"sg_note_links": spawnedNoteList} ) 

        else :
            spawnLink = self.sg.create("CustomEntity04", {"code" : "link_%i"%noteSgData_taskValues_list[0]["shotId"], "sg_note":noteSgData_taskValues_list[0], "sg_note_links" : [resultNote], "project" : {'type' : "Project" , 'id' : self.project } }, ["sg_note", "sg_note_links"]   )
            refresh_id_list.append(spawnLink["sg_note"]["id"])

        for spawned_note in spawnLink["sg_note_links"] :
            refresh_id_list.append(spawned_note["id"])

        if not resultNote['id'] in refresh_id_list :
              refresh_id_list.append(resultNote['id'])
        sgDataShot = {"id" : noteSgData_taskValues_list[0]["shotId"] , "code" : noteSgData_taskValues_list[0]["shotCode"] , "type" : noteSgData_taskValues_list[0]["shotType"], "getOnly_Notes" : refresh_id_list }  

        self.queue.put( [1, u"queryNotes"  , sgDataShot, None ] ) 



    ## @decorateur_try_except
    def getNote_link(self, noteId ) :
        projectFilter = ['project','is', { 'type':'Project', 'id':self.project} ]
        noteFilter = ['id','is', noteId]
        noteDict = self.sg.find_one("Note", [ projectFilter, noteFilter ], [ "note_links" ]   )


        shotAssetLink = []
        versionLink = []
        for link in noteDict["note_links"] :
            if link["type"] == "Shot" or link["type"] == "Asset"  : 
                shotAssetLink.append(link) 
            if link["type"] == "Version" :
                versionLink.append(link)

        if versionLink : 
            return versionLink[0]
        elif shotAssetLink :
            return shotAssetLink[0]
        else :
            return None
        return None

    ## @decorateur_try_except
    def setNoteTask(self, noteSgData_taskValues_list,  threadCommandCallBack = None) :


        sg_task = self.sg.find_one("Task", [ [ "content",'in', noteSgData_taskValues_list[1]], ["entity", "is", [{"type" : noteSgData_taskValues_list[0]["shotType"], "id": noteSgData_taskValues_list[0]["shotId"] }]  ] ] )


        if sg_task or "NoTask" in noteSgData_taskValues_list[1] :

            shotLink =  None# self.getNote_link(noteSgData_taskValues_list[0]["id"])

            sg_task_value = []
            if sg_task :
                sg_task_value = [sg_task]


            self.sg.update("Note", noteSgData_taskValues_list[0]["id"], {"tasks" : sg_task_value }) #  , "note_links" : [shotLink] } )

            projectFilter = ['project','is', { 'type':'Project', 'id':self.project} ]
            noteFilter = ['id','is', noteSgData_taskValues_list[0]["id"] ]
            noteDict = self.sg.find_one("Note", [ projectFilter, noteFilter ], ["sg_status_list","tag_list","sg_note_type","tasks", "subject", "created_at", "user", "content", "note_links" ]   )

            for link in noteDict["note_links"] :
                if link["type"] == "Shot" or link["type"] == "Asset" : 
                    noteDict["shotCode"] = link["name"]
                    noteDict["shotId"]   = link["id"]
                    noteDict["shotType"] = link["type"]
        

            self.SIGNAL_refreshNote.emit( [ noteDict , True ] )

    # RUN THREADING
    def run(self):
        while True:
            host = self.queue.get()

            
            self.SIGNAL_pbar.emit( self.queue.getCount()  )
            self.setRunThreadCommand( host[1], host[2], host[3] )
            self.queue.task_done()
            self.SIGNAL_pbar.emit( self.queue.getCount()  )
