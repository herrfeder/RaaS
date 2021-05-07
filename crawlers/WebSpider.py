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
import inspect
import ipdb; trace=ipdb.set_trace




PATH={ "gospider":"/home/theia/tools/bin/gospider",
        }

gospider_regex = {
    "robots" :         r"\[robots\] - ",
    "subdomains" :     r"\[subdomains\] - ",
    "javascript" :     r"\[javascript\] - ",
    "url" :            r"\[url\] - \[code-[0-9]{3}\] - ",
    "othersources" :   r"\[other-sources\] - ",
    "form" :           r"\[form\] - ",
    "linkfinder" :     r"\[linkfinder\] - ",
}


class WebSpider(threading.Thread):

    def __init__(self, domain_name, env, 
                 finish_cb=None, interrupt_cb=None):

        super(WebSpider, self).__init__()
        self.thread = threading.Thread(target=self.run, args=())
        self.thread.deamon = True
        self.process = None 
        self.finish_cb = finish_cb
        self.interrupt_cb = interrupt_cb
        
        self.choosen = ["gospider"]
        
        self.domain_name = domain_name
        self.result_list = []
        self.fin = 0
        self.env = env

    def exit_thread(self):
        self.process.kill()


    def compile_regex(self, tool=""):
        input_reg_dict = {}
        output_reg_dict = {}
        try:
            if tool=="gospider":
                input_reg_dict = gospider_regex
        except:
            # add logging and exit
            pass
        for key in input_reg_dict.keys():
            output_reg_dict[re.compile(input_reg_dict[key])] = key
        
        return output_reg_dict


    @name_thread_crawl
    def run(self):
        print("[*] Running Module: Webspider")
        if "gospider" in self.choosen:
            for output in self.run_gospider(self.domain_name):
                self.extract_gospider_output(output)


        if self.finish_cb is not None:
            self.finish_cb()


    def get_result_list(self):
        return self.result_list



    def run_gospider(self, domain):
        self.reg_dict = self.compile_regex("gospider")

        ##############################
        ### TODO add cmd build utility
        ##############################

        cmd = [PATH["gospider"],'-k','2','-d','5','-s',domain]
        self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
        for stdout_line in iter(self.process.stdout.readline, ""):
            yield stdout_line
        self.process.stdout.close()
        return_code = self.process.wait()
        if return_code:
            raise subprocess.CalledProcessError(return_code, cmd)

    
    def extract_gospider_output(self, output_line):
        if any((match := regex.match(output_line)) for regex in self.reg_dict.keys()):
            pass
            #print("gospider")
            #print(self.reg_dict[match.re], output_line[match.span()[1]:])
            


        pass

if __name__ == "__main__":

    websp = WebSpider("https://deezer.com", {})
    websp.run()

