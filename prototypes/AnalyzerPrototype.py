import sys
import threading
import subprocess
from prototypes.thread.ThreadPrototype import ThreadPrototype
from utils.RaasLogger import RaasLogger
import time



class AnalyzerPrototype(ThreadPrototype): 

    def __init__(self, datatype_input, data_object, datatype_output, sm_write_lock):
        super(self.__class__, self).__init__()
        self.results = []
        self.log = RaasLogger(self.__class__.__name__)
        self.write_lock_setter = sm_write_lock

        datalink_d = data_object.get_input_linker(datatype_output, self.results, self.tool)
        
        self.datalink = datalink_d["datalinker_object"]
        self.datalink_event = datalink_d["datalinker_event"]
        self.datalink.start()


    def run_analyzer(self, toolcmds):

        self.check_set_lock()
       

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