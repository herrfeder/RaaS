import re
from IPython.core.debugger import Tracer; debug_here=Tracer()
import logging
import threading
from utility import getIPfromDomain, evalTarget
import nmap
import json

PATH={ "amass":"../amass/amass",
        "subfinder":"../subfinder",
        "fierce":"../fierce/fierce/fierce.py"
        }


class PortScanner(threading.Thread):


    def __init__(self, env="", load=False):

        super(PortScanner, self).__init__()
        self.thread = threading.Thread(target=self.run, args=())
        self.thread.deamon = True
        self.result_list = []
        self.fin = 0


    def run(self, target):
        print("[*] Running Module: PortScanner")
        eval_target,target = evalTarget(target)
        if eval_target != "invalid":
            if eval_target == "ip":
                self.scanHost(target)
            elif eval_target == "range":
                self.scanRange(target)
        else:
           return -1

    def scanHost(self, target):
        final_result = {"host":"","tcp":"","udp":""}
        nm = nmap.PortScanner()
        result = nm.scan(target,arguments='--top-ports 10')
        if result['nmap']['scanstats']['uphosts'] == "0":
            print("\t[+] Host {} seems offline, try to surpress Ping".format(target))
            result = nm.scan(target,arguments='-Pn -p-')
            if result['nmap']['scanstats']['uphosts'] == "0":
                print("\t[+] Host {} seems still offline, maybe it's down".format(target))
                final_result['host'] == "down"
            else:

                print("\t[+] Host {} is online".format(target))
                tcp_ports = 0
                tcp = self.getContent(result, 'tcp')
                if tcp: 
                    tcp_ports = list(tcp.keys())
                    if len(tcp_ports) > 0:
                        result = nm.scan(target,arguments='-Pn -sV -p-')
                        final_result['host'] = "up"
                        final_result['tcp'] = json.dumps(self.getContent(result, 'tcp'))
        else:

            print("\t[+] Host {} is online".format(target))
            result = nm.scan(target, arguments='-sV -p-')
            final_result['host'] = "up"
            final_result['tcp'] = json.dumps(result['scan'][list(result['scan'].keys())[0]]['tcp'])

        print(final_result)
        self.result_list.append((target,final_result))


    def getContent(self, result, key):

        scan = result['scan'][list(result['scan'].keys())[0]]
        
        return scan.get(key,'')


    def getResultList(self):
        return self.result_list

if __name__ == '__main__':

    ps = PortScanner("federland.dnshome.de")
    ps.run()
