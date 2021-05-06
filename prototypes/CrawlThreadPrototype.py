import sys
import threading
import subprocess
from prototypes.ThreadPrototype import ThreadPrototype
from utils.RaasLogger import RaasLogger




class CrawlThreadPrototype(ThreadPrototype): 

    def __init__(self):
        super(ThreadPrototype, self).__init__()
        self.results = []
        self.log = RaasLogger(self.__class__.__name__)
       

    def finish_cb(self):
        self.log.debug("Thread finished gracefully, sending Data and quit.")
        return self.results


    def interrupt_cb(self, obj):
        self.log.debug("Thread got killed and will be finished gracefully, sending Data and quit.")
        return self.results


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

        
    def append_results(self, append_item):
        self.results.append(append_item)

    
    def get_results(self):
        return self.results