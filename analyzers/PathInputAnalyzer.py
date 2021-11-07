import pathlib
import sys
APP_PATH = pathlib.Path(__file__).parent.resolve()
sys.path.append(APP_PATH)
import time
import re
import logging
import threading
import re
from IPython.core.debugger import Tracer; debughere=Tracer()

from utils.threadutil import *
from prototypes.AnalyzerPrototype import AnalyzerPrototype


class PathInputAnalyzer(AnalyzerPrototype):

    def __init__(self, domain_name, data_input_object, data_output_object, sm_write_lock):

        super(self.__class__, self).__init__("paths", data_input_object, data_output_object, "pathinput", sm_write_lock)
        self.domain_name = domain_name
        


    @name_thread_analyzer
    def run(self):
        self.log.info(f"Running Module: PathInputAnalyzer with {self.datatype_output}")
        self.run_analyzer()
        
        