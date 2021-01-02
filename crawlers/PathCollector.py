import pathlib
import sys
APP_PATH = pathlib.Path(__file__).parent.resolve()
sys.path.append(APP_PATH)

from utils.threadutil import *
from prototypes.CrawlThreadPrototype import CrawlThreadPrototype

import subprocess
import time
import re
import logging
import threading
import re
import ipdb; trace=ipdb.set_trace

PATH={ "gau":"/home/theia/tools/bin/gau",
        }


tool_regex = {}

class PathCollector(CrawlThreadPrototype):

    def __init__(self, domain_name, env, 
                finish_cb=None, interrupt_cb=None):

        super(PathCollector, self).__init__()
        self.process = None
        self.finish_cb = finish_cb
        self.interrupt_cb = interrupt_cb

        self.choosen = ["gau"]

        self.domain_name = domain_name
        self.result_list = []
        self.fin = 0
        self.env = env


    def exit_thread(self):
        self.process.kill()
        self.kill()


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
        print("[*] Running Module: Pathcollector")
        if "gau" in self.choosen:
            for output in self.run_gau(self.domain_name):
                self.extract_gau_output(output)
        elif "test" in self.choosen:
            print("run test")
        
        if self.finish_cb is not None:
            self.finish_cb()



    def get_result_list(self):
        return self.result_list


    def run_gau(self,domain):

        ##############################
        ### TODO add cmd build utility
        ##############################

        cmd = [PATH["gau"],domain]
        self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
        for stdout_line in iter(self.process.stdout.readline, ""):
            yield stdout_line
        self.process.stdout.close()
        return_code = self.process.wait()
        if return_code:
            raise subprocess.CalledProcessError(return_code, cmd)

    
    def extract_gau_output(self, output_line):
        pass
        #print("gau")
        #print(output_line)
            

if __name__ == "__main__":

    websp = PathCollector("https://deezer.com", {})
    websp.run()

