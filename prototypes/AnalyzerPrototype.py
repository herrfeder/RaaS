import sys
import threading
import subprocess
from prototypes.thread.ThreadPrototype import ThreadPrototype
from utils.RaasLogger import RaasLogger
import time



class AnalyzerPrototype(ThreadPrototype): 

    def __init__(self, datatype_input, data_input_object, data_output_object, datatype_output, sm_write_lock):
        super(AnalyzerPrototype, self).__init__()
        self.results = []
        self.log = RaasLogger(self.__class__.__name__)
        self.write_lock_setter = sm_write_lock
        self.datatype_input = datatype_input
        self.datatype_output = datatype_output


        datalink_d = data_input_object.get_input_linker(datatype_output, self.results)
        self.datalink = datalink_d["datalinker_object"]
        self.datalink_event = datalink_d["datalinker_event"]
        self.datalink.start()

        self.data_output_con = data_output_object.get_data_output_object()


    def run_analyzer(self):

        self.check_set_lock()

        for output in self.data_output_con.get_table(self.datatype_output):
            print(output)
       

        
    def append_results(self, append_item):
        self.results.append(append_item)

    
    def get_results(self):
        return self.results