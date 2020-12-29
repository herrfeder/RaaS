import pathlib
import sys
APP_PATH = pathlib.Path(__file__).parent.resolve()
sys.path.append(APP_PATH)

from utils.threadutil import *

import subprocess
import re
import logging
import threading
import re
import ipdb; trace=ipdb.set_trace

PATH={ "gau":"/home/theia/tools/bin/gau",
        }


tool_regex = {}

class PathCollector(threading.Thread):

    def __init__(self, domain_name, env, callback=None):

        super(PathCollector, self).__init__()
        self.thread = threading.Thread(target=self.run, args=())
        self.thread.deamon = True
        self.callback = callback

        self.choosen = ["test"]

        self.domain_name = domain_name
        self.result_list = []
        self.fin = 0
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
        print("[*] Running Module: Pathcollector")
        if "gau" in self.choosen:
            for output in self.run_gau(self.domain_name):
                self.extract_gau_output(output)
        elif "test" in self.choosen:
            print("run test")
        
        if self.callback is not None:
            self.callback()


    def get_result_list(self):
        return self.result_list


    def get_fin(self):
        return self.fin


    def run_gau(self,domain):

        ##############################
        ### TODO add cmd build utility
        ##############################

        cmd = [PATH["gau"],domain]
        popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
        for stdout_line in iter(popen.stdout.readline, ""):
            yield stdout_line
        popen.stdout.close()
        return_code = popen.wait()
        if return_code:
            raise subprocess.CalledProcessError(return_code, cmd)

    
    def extract_gau_output(self, output_line):
        pass
        print("gau")
        print(output_line)
            


        pass

if __name__ == "__main__":

    websp = PathCollector("https://deezer.com", {})
    websp.run()

