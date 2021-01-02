import sys
import threading
import ipdb; trace=ipdb.set_trace



class CrawlThreadPrototype(threading.Thread): 

    def __init__(self):

        super(CrawlThreadPrototype, self).__init__()
        self.thread = threading.Thread(target=self.run, args=())
        self.thread.deamon = True
        self.killed = False


    def __run(self): 
        sys.settrace(self.globaltrace) 
        self.__run_backup() 
        self.run = self.__run_backup 


    def start(self): 
        self.__run_backup = self.run 
        self.run = self.__run       
        threading.Thread.start(self) 


    def globaltrace(self, frame, event, arg): 
        if event == 'call': 
            return self.localtrace 
        else: 
            return None
    

    def localtrace(self, frame, event, arg): 
        if self.killed: 
            if event == 'line':
                self.interrupt_cb()
                print("Exiting Thread") 
                raise SystemExit() 
        return self.localtrace 
    

    def kill(self): 
        self.killed = True