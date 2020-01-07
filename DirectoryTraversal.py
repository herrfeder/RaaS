import re
from IPython.core.debugger import Tracer; debughere=Tracer()
import logging
import threading
from paths import PATH
import subprocess
import os
import json
import datetime
from utility import eval_url
from exceptions import WrongDomainSyntax, DomainNoIp
from misc.settings import raas_dictconfig
import logging
from logging.config import dictConfig

class DirectoryTraversal(threading.Thread):


    def __init__(self, env="", load=False):

        super(DirectoryTraversal, self).__init__()
        self.thread = threading.Thread(target=self.run, args=())
        self.thread.deamon = True
        dictConfig(raas_dictconfig)
        self.lgg = logging.getLogger("RAAS_spider")
        self.env = env
        self.result_list = []
        self.fin = 0
        self.scanned_hosts = []


    def run(self, target, port=[""]):
        print("[*] Running Module: Directory Traversal")
        if not (target,port) in self.scanned_hosts:
            self.scanned_hosts.append((target,port))
            return self.run_dirsearch(target, port)
        else:
            print("is in scanned hosts")

    def run_dirsearch(self, target, port="", extension="php,js,txt,yml", wordlist=""):
        url = ""
        url_dict = ""
        try:
            url, url_dict = eval_url(target, port)
        except (DomainNoIp, WrongDomainSyntax) as e:
            print(e)
            self.lgg.exception("Got Error:")
            return -1

        if not url:
            return -1

        print("\t[+] Starting Dirsearch for {}".format(url))
        timedate = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S.%f")[:-3]
        report_name = "temp/"+timedate+"_"+self.env['project']+"_"+self.env['dftype']
        print(report_name)
        cmd_arr =  [PATH["dirsearch"],
                   '-u', url,
                   '-e', extension,
                   '--json-report='+report_name]

        if wordlist:
            cmd_arr.append("-w")
            cmd_arr.append(wordlist)

        p = subprocess.run(cmd_arr, stdout=subprocess.PIPE)

        uri = ""

        try:
            with open(report_name,'r') as f:
                output = f.read()
 
            output = json.loads(output)
            uri = list(output.keys())[0]
            resultdata = output[uri]

        except Exception as e:
            print(e)
            self.lgg.exception("Got Error:")
            resultdata = [{"status":"noscan",
                          "content-length":"",
                          "redirect":"",
                          "path":""}]

        resultdata = [dict(item, **{'uri':uri,
                            'port':url_dict['port'],
                            'ssl':url_dict['ssl'],
                            'domain':url_dict['base_url'].split("/")[0]}) for item in resultdata]

        self.result_list.append(resultdata)
 
        try:
            os.remove(report_name)
        except Exception as e:
            print(e)
            pass

        return resultdata

    def get_result_list(self):
        return self.result_list

if __name__ == '__main__':

    dt = DirectoryTraversal(env={'project':'text','dftype':'dirtraversal'})
    dt.run("https://eurid.eu")
    debug_here()
