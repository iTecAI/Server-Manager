from subprocess import Popen, PIPE, STDOUT
import socket
from multiprocessing import Process
from threading import Thread
from json import load, dump, JSONDecodeError

def reportError(text,breaking=False):
    print(text)
    if breaking:
        input('Press enter to quit.')
        exit(0)

class JSON:
    def __init__(self,dict={}):
        for i in list(dict.keys()):
            setattr(self,i,dict[i])

def makeSettings():
    settings = {
        'snapshotsSaved':5, #number of snapshots to save
        'snapshotInterval':30, #minutes between snapshots
        'backupsSaved':20, #number of backups saved
        'backupDays':[6], #days on which to make backups (0(Sunday) -> 6(Saturday))
        'restartDays':[0], #days on which to do a server & system restart (0(Sunday) -> 6(Saturday))
        'restartTime':'23:00', #HH:MM to restart on
        'backupPath':'backups', #folder to store backups
        'backupServer':None, #OPTIONAL - external server to send backups to for redundancy
        'serverCommand':'java -jar server.jar nogui' #command to run the server
    }

    dump(settings,open('settings.json','w'))

def settings():
    try:
        return JSON(load(open('settings.json')))
    except OSError:
        makeSettings()
        return JSON(load(open('settings.json')))
    except JSONDecodeError:
        makeSettings()
        return JSON(load(open('settings.json')))


    

