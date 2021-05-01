import pathlib
import sys
APP_PATH = pathlib.Path(__file__).parent.resolve()
sys.path.append(APP_PATH)

from utils.threadutil import *
from prototypes.CrawlThreadPrototype import CrawlThreadPrototype

import time
import re
import logging
import threading
import re
from IPython.core.debugger import Tracer; debughere=Tracer()



PATH={ "gau":"/home/theia/tools/bin/gau",
        }


tool_regex = {}

class PathCollector(CrawlThreadPrototype):

    def __init__(self, domain_name, env ):

        super(CrawlThreadPrototype, self).__init__()
        super(self.__class__, self).__init__()
        self.choosen = ["gau"]
        self.domain_name = domain_name
        self.env = env



    def compile_regex(self, tool=""):
        input_reg_dict = {}
        output_reg_dict = {}
        try:
            if tool== "generic_tool":
                input_reg_dict = tool_regex
        except:
            # add logging and exit
            pass
        for key in input_reg_dict.keys():
            output_reg_dict[re.compile(input_reg_dict[key])] = key
        
        return output_reg_dict


    @name_time_thread
    def run(self):
        self.log.info("[*] Running Module: Pathcollector")
        if "gau" in self.choosen:
            # TOOL LOOP
            for output in self.run_tool(toolcmds=["/home/theia/tools/bin/gau", self.domain_name]):
                self.extract_output(output)
        
        # GRACEFUL FINISH ACTION
        if self.finish_cb is not None:
            self.finish_cb()

    
    def extract_output(self, output_line):
        self.append_results(output_line)
        

            

if __name__ == "__main__":

    pc = PathCollector("https://deezer.com", {})
    pc.run()

