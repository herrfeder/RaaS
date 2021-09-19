import sys
import threading
import subprocess
from prototypes.thread.ThreadPrototype import ThreadPrototype
from utils.RaasLogger import RaasLogger
import time



class AnalyzerPrototype(ThreadPrototype): 

    def __init__(self, datatype, data_object, tool, sm_write_lock):
        super(CrawlPrototype, self).__init__()
        self.results = []
        self.log = RaasLogger(self.__class__.__name__)
        self.tool = tool
        self.write_lock_setter = sm_write_lock

        datalink_d = data_object.get_input_linker(datatype, self.results, self.tool)
        self.datalink = datalink_d["datalinker_object"]
        self.datalink_event = datalink_d["datalinker_event"]
        self.datalink.start()


    def finish_cb(self):
        self.log.debug("Thread finished gracefully, sending Data and quit.")
        while not self.results and not self.datalink.target_data:
            time.sleep(1)
        self.remove_lock()
        

    def interrupt_cb(self, force):
        if not force:
            self.log.info("Thread got killed and will be finished gracefully, sending Data and quit.")
            while not self.results and not self.datalink.target_data:
                time.sleep(1)
        else:
            self.log.info("Thread got killed got forced to exit, kill without rescuing data.")
        self.remove_lock()
    
    def check_set_lock(self):
        self.log.info("set lock")
        self.write_lock_setter(True)


    def remove_lock(self):
        self.log.info("Remove lock")
        self.write_lock_setter(False)


    def run_tool(self, toolcmds):

        self.check_set_lock()
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