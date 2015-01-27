#!/usr/bin/python
# -*- coding: utf-8 -*-

import _strptime
import os
import sys
import re
import urllib

try :
    from sgtk.platform.qt import QtCore, QtGui
    #from PySide  import QtCore, QtGui
    _signal = QtCore.Signal 
    outFileName = "side"

except :
    from PyQt4 import QtGui, QtCore
    _signal = QtCore.pyqtSignal
    outFileName = "cute"





import utils
from utils import *



############### THREADING CLASS ################# 

class sg_query(QtCore.QThread) :
    queue = None

    SERVER_PATH = "https://nozon.shotgunstudio.com"
    SCRIPT_NAME = 'noteManager'     
    SCRIPT_KEY = '3fbb2a5f180457af709fcad231c96ac8a916711427af5a06c47eb1758690f6e4'

    SIGNAL_queryAllShot = _signal(object)
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

    th_id = 0
    @decorateur_try_except
    def __init__(self, app ):
        plog("sg_query.__init__\n")
        super(sg_query, self).__init__()


        self.sg_userDict = None

        if not app :
            sys.path.append("Z:/Dev/cyril/python/PACKAGES")

            from shotgun_api3 import Shotgun
            self.sg = Shotgun(self.SERVER_PATH, self.SCRIPT_NAME, self.SCRIPT_KEY)
        
        else :
            #self.sg = app.engine.tank.shotgun # too slow
            
            sys.path.append("Z:/Dev/cyril/python/PACKAGES")
            from shotgun_api3 import Shotgun
            self.sg = Shotgun(self.SERVER_PATH, self.SCRIPT_NAME, self.SCRIPT_KEY)

            self.sg_userDict = app.context.user
            pprint( "Thread User :" + str(self.sg_userDict))

        self.project = None
        self.tempPath = None       
        self.tempPathAttachement = None
        self.tempPath_uploadAttachment = None


        # set default project id 



    def setProjectId(self, projectId = 191 ):
        self.project = projectId


    def setTempPath(self) :
        self.tempPath = os.path.join( getTempPath(), u"tk_shotgun_toDoApp_%i"%self.project)
        
        self.tempPathAttachement = os.path.join( getTempPath(), u"tk_shotgun_toDoApp_%i"%self.project, u"attachment")
        #self.tempPath_uploadAttachment = os.path.join( getTempPath(), u"tk_shotgun_toDoApp_%i"%self.project, u"upload_attachment")

        if not os.path.isdir( self.tempPath ) :
            print u"Creating temp folder ",  self.tempPath
            os.makedirs(self.tempPath)
    
        if not os.path.isdir( self.tempPathAttachement ) :
            print u"Creating temp folder ",  self.tempPathAttachement
            os.makedirs(self.tempPathAttachement)


    @decorateur_try_except
    def setRunThreadCommand(self, stringCommandSwitch= u"downloadThumbnail", threadCommandArgs = None , threadCommandCallBack= None) :

        if stringCommandSwitch == u"downloadThumbnail" :
            self.downloadThumbnail(threadCommandArgs, threadCommandCallBack)

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



    def queryTaskAssigned(self, shotSgData_taskList_noteId, callBack = None ) :

        projectFilter = ['project','is', { 'type':'Project', 'id':self.project} ]
        taskFilter =   [ 'content','in', shotSgData_taskList_noteId[1] ]
        entityFilter = ['entity', 'is',  { 'type': shotSgData_taskList_noteId[0]['type'] , 'id':shotSgData_taskList_noteId[0]['id']}   ]
        perr(str( taskFilter )+"\n")
        perr(str( entityFilter )+"\n\n")
        assigneesNameList = []
        result = self.sg.find_one("Task", [projectFilter,taskFilter,entityFilter ], ["task_assignees"] )
        if result :
            for assignessDict in  result["task_assignees"] :
                assigneesNameList.append(assignessDict["name"])
        else :
            assigneesNameList = ["NoTask"]

        if not assigneesNameList:
            assigneesNameList = ["Nobody"]
        self.SIGNAL_queryNoteTaskAssigned.emit([ shotSgData_taskList_noteId[2], assigneesNameList ] )

    @decorateur_try_except
    def editNoteContent(self, list_note, callback = None ) :
        #[0] note content
        #[1] note id
        noteContent = list_note[0]
        self.sg.update("Note", list_note[1], {"content" :noteContent })



    @decorateur_try_except
    def queryAllShot(self, args = None,  callback = None): 
        pprint("#     query All Shot\n")
        projectFilter = ['project','is', { 'type':'Project', 'id':self.project} ]
        
        shotList = self.sg.find("Shot", [projectFilter], [u"code", u"image", u"sg_sequence" ])

        self.SIGNAL_queryAllShot.emit( shotList )
    
    @decorateur_try_except
    def downloadThumbnail(self, args = None, callback = None) :
        pprint("#     Get Thumbnail\n")
        i = 0
        for entityDict in args :
            thumbNameFile = os.path.join( self.tempPath, u"thumbnail_%s_%i.jpg"%( entityDict['type'] , entityDict['id'] ) )
            if entityDict['image'] :
                if not os.path.isfile(thumbNameFile ):
                    urllib.urlretrieve(entityDict['image'], thumbNameFile)
                    pprint("#         Downloading\n")

                self.SIGNAL_setThumbnail.emit( [  "shotAsset_%i"%entityDict["id"], thumbNameFile ] )

    @decorateur_try_except
    def downloadVersionThumbnail(self, entityDict) :
        pprint("#     get version thumbnail\n")
        thumbNameFile = os.path.join( self.tempPath, u"Version_thumbnail_%s_%i.jpg"%( entityDict['type'] , entityDict['id'] ) )   
        if entityDict['image'] :
            if not os.path.isfile(thumbNameFile ):
                pprint("#         Downloading\n")
                urllib.urlretrieve(entityDict['image'], thumbNameFile)
        return thumbNameFile

    @decorateur_try_except
    def queryNotes(self, args = None, parentWidget = None):


        projectFilter = ['project','is', { 'type':'Project', 'id':self.project} ]
        shotFilter    = ['note_links','is', { 'type':'Shot', 'id':args['id'] } ]

        noteList = self.sg.find("Note", [ projectFilter, shotFilter ] , ["sg_status_list","tag_list","sg_note_type","tasks", "subject", "created_at", "user", "content"] )


        self.SIGNAL_setNoteList.emit(  [ [ "shotAsset_%i"%args["id"] , args['code'], args['id']]  ,noteList, parentWidget ] )
        pprint("#     queryNotes END \n")

    @decorateur_try_except
    def queryNoteContent(self, args = None, args2 = None) :

        pprint( "#     queryNoteContent \n")

        projectFilter = ['project','is', { 'type':'Project', 'id':self.project} ]
        idNoteList = []
        for noteDict in args :
            idNoteList.append(noteDict["id"])
        noteFilter    = ['id','in', idNoteList ]

        sg_notecontent_List = []
        if idNoteList :
            sg_notecontent_tempList = self.sg.find("Note", [ projectFilter, noteFilter ] , ["attachments", "subject", "content", "user", "created_at", "updated_at", "sg_status_list", "replies", "note_links"] )
            
            for sgNote in sg_notecontent_tempList :

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
                for noteLink in sgNote["note_links"] : 
                    if noteLink["type"] == "Version" :
                        versionDict = self.sg.find_one( "Version", [ projectFilter, ['id','is', noteLink['id'] ] ] , ["user", "created_at", "image", "sg_path_to_movie", "code"] )
                        versionDict["downloadedImage"] = self.downloadVersionThumbnail(versionDict)
                        versionLinkList.append( versionDict  )
                
                sgNote["note_links"] = versionLinkList
                


                sg_notecontent_List.append(sgNote)
      


        self.SIGNAL_queryNoteContent.emit(  [sg_notecontent_List] )

    @decorateur_try_except
    def queryNoteVersion(self, threadCommandArgs, threadCommandCallBack) :
        pprint( "#     Query Version and Replies number\n")

        projectFilter = ['project','is', { 'type':'Project', 'id':self.project} ]
        idNoteFilter = ['id','is', threadCommandArgs ]
        linkIsVersionFilter = ['note_links', 'type_is' , ['Version'] ]
        pprint( "#        Query SG\n")

        value = self.sg.find_one("Note", [projectFilter , idNoteFilter ], ['note_links', 'replies'] )



        pprint( "#        Query SG DONE\n")
        if value :
            versionString =""
            for noteLink in value["note_links"] :
                if noteLink["type"] == "Version" :
                    versionString = noteLink["name"] 
                    splits = re.findall(r' v\d+', noteLink["name"] )
                    if splits :
                        versionString = splits[-1]
                    
                    break
            pprint("EMIT to UI queryNoteVersion \n")    
            self.SIGNAL_queryNoteVersion.emit( [threadCommandArgs,versionString, len( value["replies"] )])
        pprint( "#     Query Version and Replies number END\n\n")
        #print threadCommandArgs, threadCommandCallBack

    @decorateur_try_except
    def downloadAttachement(self, attachementDict ) :
        pprint( "#     Get Note attachement \n")

        attachmentFileName = os.path.join( self.tempPathAttachement, u"attachment_%i_%s"%(  attachementDict['id'], attachementDict['filename']  ) )
        if not os.path.isfile(attachmentFileName ) :
            pprint( "#         Downloading")
            self.sg.download_attachment(attachementDict, attachmentFileName ) 
        
        attachementDict["fileOnDisk"] = attachmentFileName

        return attachementDict

    @decorateur_try_except
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

    @decorateur_try_except
    def setNoteStatus(self, NoteData, threadCommandCallBack):
        pprint( "#     Set note status")
        self.sg.update("Note",NoteData[0]['id'], { 'sg_status_list':NoteData[0]["new_sg_status_list"] } )
        self.SIGNAL_replyNote.emit(  [NoteData[0], False ] )


    @decorateur_try_except
    def setNoteType(self, NoteData , threadCommandCallBack):
        pprint("#      Set note type")
        self.sg.update("Note",NoteData[0]['id'], { 'sg_note_type' : NoteData[0]["new_sg_note_type"] } )
        self.SIGNAL_refreshNote.emit( [NoteData[0], False ] )

    def deleteNote(self, noteId, callback = None ) :
        self.sg.delete("Note", noteId[0] )
        self.SIGNAL_refreshNote.emit( [ {"id" : noteId[0] } , u"Delete" ] )


    @decorateur_try_except
    def replyNote(self, replyNoteData, threadCommandCallBack ) :
        pprint( "#     Single Reply to Note") 

        dReply = {
                 'entity': {'type':'Note','id':replyNoteData[1]['id'] },
                 'content': replyNoteData[0]['content']
                 } 
        
        if  replyNoteData[0]['content']  != "" :       
            pprint( "#         create Reply")
            self.sg.create("Reply", dReply )

            pprint( "Creating reply \n" )


        for attachToUpload in replyNoteData[0]["uploads"] :
            pprint( "#         Uploading attachement")
            self.sg.upload("Note", replyNoteData[1]['id'], attachToUpload )

            pprint( "uploading " + str(  attachToUpload ) + "\n")

        if replyNoteData[1].has_key("new_sg_status_list") :
            #if replyNoteData[1]["new_sg_status_list"] != replyNoteData[1]["sg_status_list"] :
            pprint( "#         Updating Status")

            self.sg.update("Note",replyNoteData[1]['id'], { 'sg_status_list':replyNoteData[1]["new_sg_status_list"] } )

        self.SIGNAL_replyNote.emit(  [replyNoteData[1], True ] )


    @decorateur_try_except
    def multiReplyNote(self, multiReplyNoteData, threadCommandCallBack ) :
        pprint( "#     Multi Reply to Note") 
        
        for replyNoteData in multiReplyNoteData[1] :
            if  multiReplyNoteData[0]['content']  != "" :
                dReply= {'entity' : {'type':'Note','id':replyNoteData['id'] } , "content" : multiReplyNoteData[0]['content']  }           
                self.sg.create("Reply", dReply )

        
            for attachToUpload in multiReplyNoteData[0]["uploads"] :
                pprint( "#         Uploading attachement")
                self.sg.upload("Note", replyNoteData['id'], attachToUpload )


            if multiReplyNoteData[1][0].has_key("new_sg_status_list") :
                pprint( "#         Updating Status")
                self.sg.update("Note",replyNoteData['id'], { 'sg_status_list':multiReplyNoteData[1][0]["new_sg_status_list"] } )

            
            self.SIGNAL_replyNote.emit(  [ replyNoteData, False ] )


    @decorateur_try_except
    def getVersion(self, shotObj, threadCommandCallBack ) :

        projectFilter = ['project','is', { 'type':'Project', 'id':self.project} ]
        shotFilter    = ['entity','is', {'type': 'Shot', 'id':shotObj[0]} ]
        taskFilter = []
        for taskName in shotObj[1] :
            taskFilter.append( ['sg_task', 'name_contains', taskName  ] )
        #shotObj[1]
        Complex_TaskFilter    ={
            "filter_operator": "any",
            "filters": taskFilter
            }


        lastVersionList = self.sg.find("Version", [projectFilter, shotFilter, Complex_TaskFilter ],["sg_task","user", "created_at", "image", "sg_path_to_movie", "code"] )[-5:]


        for versionDict in lastVersionList :
            versionDict["downloadedImage"] = self.downloadVersionThumbnail(versionDict)

        plog("EMIT to UI => updateDraw note Version \n")
        self.SIGNAL_queryVersion.emit( [ lastVersionList[::-1],shotObj[2]  ] )
        

    def createNote(self, noteDictList, threadCommandCallBack = None) :

        for noteDict in noteDictList :

            # 0 the note dict
            # 1 the uploads
            # 2 the shot sgData
            # 3 taskList link
            subjectTaskStr = ""

            if noteDict[3] :
                taskDict = self.sg.find_one("Task", [ [ "content",'in', noteDict[3] ], ["entity", "is", [{"type" : "Shot", "id": noteDict[2]["id"] }]  ] ], ["content"] )
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

            for k,v in noteDict[0].iteritems() :
                print k,v
            print "\n"
            resultNote =  self.sg.create("Note", noteDict[0], ["sg_status_list","tag_list","sg_note_type","tasks", "subject", "created_at", "user", "content"] ) 
            
            if noteDict[1] : 
                for fileName in noteDict[1] :
                    pprint( "#         Uploading attachement")
                    self.sg.upload("Note", resultNote['id'], fileName )

                    pprint( "uploading " + str(  fileName ) + "\n")           


            resultNote.update({"shotCode" : noteDict[2]['code'], "shotId" : noteDict[2]['id'] } )
            self.SIGNAL_addNote.emit( [ resultNote ] )




    def getNote_link(self, noteId ) :
        projectFilter = ['project','is', { 'type':'Project', 'id':self.project} ]
        noteFilter = ['id','is', noteId]
        noteDict = self.sg.find_one("Note", [ projectFilter, noteFilter ], [ "note_links" ]   )

        for link in noteDict["note_links"] :
            if link["type"] == "Shot" : 
                return link

        return None


    def setNoteTask(self, noteSgData_taskValues_list,  threadCommandCallBack = None) :
        #print noteSgData_taskValues_list[0]
        #print noteSgData_taskValues_list[1]

        sg_task = self.sg.find_one("Task", [ [ "content",'in', noteSgData_taskValues_list[1]], ["entity", "is", [{"type" : "Shot", "id": noteSgData_taskValues_list[0]["shotId"] }]  ] ] )


        if sg_task or "NoTask" in noteSgData_taskValues_list[1] :

            shotLink =  self.getNote_link(noteSgData_taskValues_list[0]["id"])

            sg_task_value = []
            if sg_task :
                sg_task_value = [sg_task]


            self.sg.update("Note", noteSgData_taskValues_list[0]["id"], {"tasks" : sg_task_value , "note_links" : [shotLink] } )

            projectFilter = ['project','is', { 'type':'Project', 'id':self.project} ]
            noteFilter = ['id','is', noteSgData_taskValues_list[0]["id"] ]
            noteDict = self.sg.find_one("Note", [ projectFilter, noteFilter ], ["sg_status_list","tag_list","sg_note_type","tasks", "subject", "created_at", "user", "content", "note_links" ]   )

            for link in noteDict["note_links"] :
                if link["type"] == "Shot" : 
                    noteDict["shotCode"] = link["name"]
                    noteDict["shotId"] = link["id"]

                    

            self.SIGNAL_refreshNote.emit( [ noteDict , True ] )

    # RUN THREADING
    def run(self):
        while True:
            pprint(  str(self.th_id) + "\n")
            host = self.queue.get()
            self.setRunThreadCommand( host[1], host[2], host[3] )
            self.queue.task_done()
