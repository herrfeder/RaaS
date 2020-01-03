import re
from IPython.core.debugger import Tracer; debug_here=Tracer()
import logging
import threading
from utility import get_ip_from_domain, eval_target
import nmap
import json
from misc.settings import raas_dictconfig
from logging.config import dictConfig

PATH={ "amass":"../amass/amass",
        "subfinder":"../subfinder",
        "fierce":"../fierce/fierce/fierce.py"
        }


class PortScanner(threading.Thread):


    def __init__(self, env="", load=False):

        super(PortScanner, self).__init__()
        self.thread = threading.Thread(target=self.run, args=())
        self.thread.deamon = True
        dictConfig(raas_dictconfig)
        self.lgg = logging.getLogger("RAAS_portscan")
        self.result_list = []
        self.fin = 0


    def run(self, target):
        self.lgg.info("[*] Running Module: PortScanner")
        evaltarget,target = eval_target(target)
        if evaltarget != "invalid":
            if evaltarget == "ip":
                return self.scan_host(target)
            elif evaltarget == "range":
                return self.scan_range(target)
        else:
           return -1

    def scan_host(self, target):
        nm = nmap.PortScanner()
        result = nm.scan(target,arguments='--top-ports 10')
        if result['nmap']['scanstats']['uphosts'] == "0":
            self.lgg.debug("[+] Host {} seems offline, try to surpress Ping".format(target))
            result = nm.scan(target,arguments='-Pn -p-')
            if result['nmap']['scanstats']['uphosts'] == "0":
                self.lgg.debug("[+] Host {} seems still offline, maybe it's down".format(target))
                return ""
            else:

                self.lgg.info("[+] Host {} is online".format(target))
                tcp_ports = 0
                tcp = self.get_content(result, 'tcp')
                if tcp:
                    tcp_ports = list(tcp.keys())
                    if len(tcp_ports) > 0:
                        result = nm.scan(target,arguments='-Pn -sV -p-')
                        final_result = self.get_content(result, 'tcp')
        else:

            self.lgg.info("[+] Host {} is online".format(target))
            result = nm.scan(target, arguments='-sV -p-')
            final_result = self.get_content(result, 'tcp')

        self.result_list.append((target,final_result))

        return final_result


    def get_content(self, result, key):

        scan = result['scan'][list(result['scan'].keys())[0]]
        return scan.get(key,'')


    def return_resultlist(self):
        return self.result_list

if __name__ == '__main__':

    ps = PortScanner("federland.dnshome.de")
    ps.run()
