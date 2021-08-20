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
from prototypes.CrawlPrototype import CrawlPrototype




PATH={ "gau":"/home/theia/tools/bin/gau",
       "gospider":"/home/theia/tools/bin/gospider"
    }

CMD={"gau":[PATH["gau"]],
     "gospider":[PATH["gospider"], "-a", "-c1", "--json", "--delay", "1", "-s"]}


tool_regex = {}

class PathCollector(CrawlPrototype):

    def __init__(self, domain_name, data_object, tool):

        super(self.__class__, self).__init__("pathinput", data_object, tool)
        self.domain_name = domain_name
        


    def compile_regex(self, tool=""):
        input_reg_dict = {}
        output_reg_dict = {}
        try:
            if tool== "generic_tool":
                input_reg_dict = tool_regex
        except:
            self.log.debug("Special Regex Syntax")    
            
        for key in input_reg_dict.keys():
            output_reg_dict[re.compile(input_reg_dict[key])] = key
        
        return output_reg_dict


    @name_thread_crawl
    def run(self):
        self.log.info("Running Module: Pathcollector")
        # TOOL LOOP
        cmd = CMD[self.tool]
        cmd.append(self.domain_name)
        for output in self.run_tool(toolcmds=cmd):
            self.extract_output(output)
        
        # GRACEFUL FINISH ACTION
        if self.finish_cb is not None:
            self.finish_cb()

    
    def extract_output(self, output_line):
        self.append_results(output_line)
        


