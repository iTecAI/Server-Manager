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

class Server:
    def __init__(self):
        self.ssock,self.msock = socket.socketpair()
        self.running = True
        pthread = Thread(target=self.mprinter)
        pthread.start()
        sproc = Thread(target=self.server_instance)
        sproc.start()
    
    def mprinter(self):
        while self.running:
            dat = self.get_all(self.msock)
            if dat:
                dat = dat[2:len(dat)-3]
                dat = dat.replace("\\\\r\\\\n'b'",'\n')
                print(dat)
    
    def command(self,command):
        self.msock.send(bytes(command,'utf-8'))
        if command == 'stop':
            self.running = False

    def get_all(self,sock):
        try:
            dat = str(sock.recv(5120)).strip()
            dat = dat[2:len(dat)-5]
            return dat
        except IndexError:
            return b''

    def run_server_comm(self):
        while self.running:
            dat = self.ssock.recv(5120)
            #dat = str(dat).strip()
            #dat = dat[2:len(dat)-1]
            if dat:
                self.serv.stdin.write(dat + b"\r\n")
                self.serv.stdin.flush()

    def server_instance(self):
        self.serv = Popen(settings().serverCommand,stdin=PIPE,stdout=PIPE,stderr=STDOUT)
        self.commT = Thread(target=self.run_server_comm)
        self.commT.start()
        while self.running:
            line = str(self.serv.stdout.readline())
            self.serv.stdout.flush()
            while line:
                line.replace('\r\n','\n')
                self.ssock.send(bytes(line,'utf-8'))
                line = str(self.serv.stdout.readline())
                self.serv.stdout.flush()
    
    def stop(self):
        self.command('stop')

serv = Server()
while True:
    serv.command(input())


    

