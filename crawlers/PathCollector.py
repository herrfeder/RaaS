import subprocess
import re
import socket
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


class PathCollector(threading.Thread):

    def __init__(self, domain_name, env):

        super(PathCollector, self).__init__()
        self.thread = threading.Thread(target=self.run, args=())
        self.thread.deamon = True
        self.domain_name = domain_name
        self.result_list = []
        self.fin = 0
        self.env = env


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


    def run(self, choosen=["gospider"]):
        print("[*] Running Module: Webspider")
        if "gospider" in choosen:
            for output in self.run_gospider(self.domain_name):
                self.extract_gospider_output(output)

        self.fin = 1


    def get_result_list(self):
        return self.result_list


    def get_fin(self):
        return self.fin


    def run_gospider(self,domain):
        self.reg_dict = self.compile_regex("gospider")

        ##############################
        ### TODO add cmd build utility
        ##############################

        cmd = [PATH["gospider"],'-k','2','-d','5','-s',domain]
        popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
        for stdout_line in iter(popen.stdout.readline, ""):
            yield stdout_line
        popen.stdout.close()
        return_code = popen.wait()
        if return_code:
            raise subprocess.CalledProcessError(return_code, cmd)

    
    def extract_gospider_output(self, output_line):
        if any((match := regex.match(output_line)) for regex in self.reg_dict.keys()):
            print(self.reg_dict[match.re], output_line[match.span()[1]:])
            


        pass

if __name__ == "__main__":

    websp = PathCollector("https://deezer.com", {})
    websp.run()

