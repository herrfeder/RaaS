import sys
import threading
import subprocess
from utils.RaasLogger import RaasLogger




class CrawlThreadPrototype(threading.Thread): 

    def __init__(self):
        super(CrawlThreadPrototype, self).__init__()
        self.thread = threading.Thread(target=self.run, args=())
        self.thread.deamon = True
        self.killed = False
        self.result_list = []

        self.log = RaasLogger(self.__class__.__name__)


    def __run(self): 
        sys.settrace(self.globaltrace) 
        self.__run_backup() 
        self.run = self.__run_backup 


    def finish_cb(self):
        self.log.info("Thread finished gracefully")
        return self.result_list


    def interrupt_cb(self, obj):
        self.log.info("Thread got killed and will be finished gracefully")
        #print(self.result_list)
        return self.result_list


    def start(self): 
        self.__run_backup = self.run 
        self.run = self.__run       
        threading.Thread.start(self)


    def run_tool(self, toolcmds):

        ##############################
        ### TODO add cmd build utility
        ##############################

        cmd = toolcmds
        self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
        
        for stdout_line in iter(self.process.stdout.readline, ""):
            yield stdout_line

        self.process.stdout.close()
        return_code = self.process.wait()
        
        if return_code:
            raise subprocess.CalledProcessError(return_code, cmd)

        
    def append_result_list(self, append_item):
        self.result_list.append(append_item)


    def globaltrace(self, frame, event, arg): 
        if event == 'call': 
            return self.localtrace 
        else: 
            return None
    

    def localtrace(self, frame, event, arg): 
        if self.killed: 
            if event == 'line':
                self.interrupt_cb(self)
                self.log.debug("Exiting Thread") 
                raise SystemExit() 
        return self.localtrace 
    

    def kill(self): 
        self.killed = True