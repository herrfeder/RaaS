import subprocess
import re
from IPython.core.debugger import Tracer
import socket
import logging
import threading
from subdomainutil import extractFierceDict
from utility import get_ip_from_domain

PATH={ "amass":"../amass/amass",
        "subfinder":"../subfinder",
        "fierce":"../fierce/fierce/fierce.py"
        }


class SubdomainColl(threading.Thread):


    def __init__(self, domain_name, env):

        super(SubdomainColl, self).__init__()
        self.thread = threading.Thread(target=self.run, args=())
        self.thread.deamon = True
        self.domain_name = domain_name
        self.result_list = []
        self.fin = 0
        self.env = env


    def run(self):
        print("[*] Running Module: Subdomain Collector")
        self.runSubfinder(self.domain_name)
        self.runAmass(self.domain_name)
        self.runFierce(self.domain_name)
        self.cleanDict()
        self.fin = 1

    def get_result_list(self):
        return self.result_list

    def getFin(self):

        return self.fin


    def runAmass(self,domain):
        print("\t[+] Starting Amass")
        p = subprocess.run([PATH["amass"],'-d',domain,'-ip'], stdout=subprocess.PIPE)

        result_list = {}
        domain_list = str(p.stdout).split("b'")[1].split('\\n')
        domain_list.pop(-1)
        for entry in domain_list:
            entry_split = entry.split(',')

            result_list[entry_split[0]]=[x for x in entry_split[1:len(entry_split)]]

        self.result_list.append(result_list)


    def runSubfinder(self,domain):
        print("\t[+] Starting Subfinder")
        p = subprocess.run([PATH["subfinder"],'-d',domain], stdout=subprocess.PIPE)

        result_list = {}
        domain_list = str(p.stdout).split('\n\n')[0]
        index = list(re.finditer('Unique subdomains',domain_list))[0].span()[1]
        domain_list = domain_list[index+1:].split('\\n')

        for entry in domain_list:

            result_list[entry] = ''

        self.result_list.append(result_list)


    def runFierce(self, domain):
        print("\t[+] Starting Fierce")
        p = subprocess.run([PATH["fierce"], '--domain', domain, '--wide'], stdout=subprocess.PIPE)

        result_list = {}
        domain_list = str(p.stdout).split('\\n')
        for line in domain_list:
            if line.startswith("Found"):
                ip_domain_d = line.split("Found: ")[1].split(". (")
                domain = ip_domain_d[0]
                ip = ip_domain_d[1].rstrip(")")
                result_list[domain] = ip

        result_list.update(extractFierceDict(domain_list))

        self.result_list.append(result_list)

    def cleanDict(self):

        for index, dic in enumerate(self.result_list):

            temp_dict = { k:v for k,v in dic.items() if ("." in k) or
                                                        (" " not in k) }

            for key,value in temp_dict.items():
                if value == '':
                    temp_dict[key] = get_ip_from_domain(key)

            self.result_list[index] = temp_dict


