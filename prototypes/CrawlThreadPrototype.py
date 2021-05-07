import sys
import threading
import subprocess
from prototypes.ThreadPrototype import ThreadPrototype
from utils.RaasLogger import RaasLogger
import time



class CrawlThreadPrototype(ThreadPrototype): 

    def __init__(self, datatype, data_object):
        super(CrawlThreadPrototype, self).__init__()
        self.results = []
        self.log = RaasLogger(self.__class__.__name__)

        datalink_d = data_object.get_crawl_linker(datatype, self.results)
        self.datalink = datalink_d["datalinker_object"]
        self.datalink_event = datalink_d["datalinker_event"]
        self.datalink.start()


    def finish_cb(self):
        self.log.debug("Thread finished gracefully, sending Data and quit.")
        while not self.results and not self.datalink.target_data:
            time.sleep(1)
        

    def interrupt_cb(self, force):
        if not force:
            self.log.info("Thread got killed and will be finished gracefully, sending Data and quit.")
            while not self.results and not self.datalink.target_data:
                time.sleep(1)
        else:
            self.log.info("Thread got killed got forced to exit, kill without rescuing data.")


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