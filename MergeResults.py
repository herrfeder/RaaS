import pandas as pd
from test_data import result_list
import threading
from IPython.core.debugger import Tracer; debughere = Tracer()
import datetime
from DataObject import DataObject
from itertools import chain
from exceptions import NoScanAvailable
import json
from datasupport import *

def popL(inlist):
    try:
        return inlist.pop()
    except IndexError:
        return ""



class MergeResults(threading.Thread):

    def __init__(self, env, columns="", result_list="", load=False):
        super(MergeResults, self).__init__()
        self.thread = threading.Thread(target=self.run, args=())
        self.thread.deamon = True
        self.result_list = result_list
        self.fin = 0
        self.env = env
        self.do = DataObject(columns, env)
        print(load)
        if load:
            self.do.load_from_csv()
 
    def run(self):
        if self.env['dftype'] == "subdomain":
            print("[*] Running Module: MergeResults for Subdomains")
            self.MergeSubDomain(self.result_list)
        if self.env['dftype'] == "portscan":
            print("[*] Running Module: MergeResults for Portscan")
            self.MergePortscan(self.result_list)
        if self.env['dftype'] == "dirtraversal":
            print("[*] Running Module: MergeResults for DirectoryTraversal")
            self.MergeDirTraversal(self.result_list)

    def getFin(self):
        return self.fin

    ############# DirTraversal ##########
    def MergeDirTraversal(self, result_list):

        self.do.CreateFromDictList(result_list)

    ############ Spider #################

    def MergeSpider(self, result_list):
        jpg_df = df[df[0].str.endswith("jpg")]
        jpg_df.apply(lambda x: "/".join(x[0].split("/")[:-1])+"/",axis=1)

    ############# Subdomain #############
    def DomainToIP(self,domain):
        try:
            return self.do.df[self.do.df['domain'] == domain]['ip4_1'].item()
        except:
            return ""

    def getIPList(self):

        ip_list = [(x1,x2) for x1,x2 in zip(self.do.df.ip4_1,self.do.df.ip4_2)]
        ip_list = pd.Series(sum(ip_list, ()))
        ip_list = ip_list[ip_list != ""]
        return ip_list[~ip_list.duplicated()].reset_index().drop(columns=['index'])

    def getDomainList(self):

        domain_list = self.do.df.domain
        domain_list = [x for x in domain_list if x != ""]
        return domain_list


    def MergeSubDomain(self, result_list):

        self.extractSubDict(result_list)

    def SubAppend(self, domain='', ip4_1='', ip4_2='', ip6_1='', ip6_2='', checkdup=True):

        new_entry_df = pd.Series({'domain':domain,
                                  'ip4_1':ip4_1, 'ip4_2':ip4_2,
                                  'ip6_1':ip6_1, 'ip6_2':ip6_2})
        if checkdup:
            duplicated = self.do.df[self.do.df.domain == domain]
            if duplicated.shape[0] > 0:
                ip4_2 = [x for x in duplicated['ip4_1']]
                ip6_2 = [x for x in duplicated['ip6_1']]

                if  ((duplicated.ip4_1.empty) and (not new_entry_df.ip4_1.empty)) or\
                    ((duplicated.ip4_2.empty) and (not new_entry_df.ip4_2.empty)) or\
                    ((duplicated.ip6_1.empty) and (not new_entry_df.ip6_1.empty)) or\
                    ((duplicated.ip6_2.empty) and (not new_entry_df.ip6_2.empty)):
                        self.do.append(new_entry_df)
                        self.do.dropIndex(duplicated.index)
                        return 1
                else:
                    return 2
            else:

                self.do.append(new_entry_df)
                return 0

    def extractSubDict(self, result_list):
        for dic in result_list:
            for key, value in dic.items():
                if (isinstance(value, list)) and (len(value) > 1):
                    ip4 = []
                    ip6 = []
                    for val in value:
                        if ":" in val:
                            ip6.append(val)
                        if "." in val:
                            ip4.append(val)
                    self.SubAppend(key, ip4_1=popL(ip4), ip4_2=popL(ip4),
                                   ip6_1=popL(ip6), ip6_2=popL(ip6))
                elif (isinstance(value, list)):

                    if ":" in "".join(value):
                        self.SubAppend(key, ip4_1="", ip6_1="".join(value))
                    if "." in "".join(value):
                        self.SubAppend(key, ip4_1="".join(value), ip6_1="")

                else:
                    if ":" in value:
                        self.SubAppend(key, ip4_1="", ip6_1=value)
                    if "." in value:
                        self.SubAppend(key, ip4_1=value, ip6_1="")


        return 1


    ################ Portscan ###################

    def MergePortscan(self, result_list):
        for entry in result_list:
            self.PortScanAppend(entry['ip'],entry['hoststatus'],entry['tcp'],entry['udp'])

        self.validatePortscan()

    def PortScanAppend(self, ip='', hoststatus='', tcp='', udp=''):

        new_entry_df = pd.Series({'ip':ip, 
                                  'hoststatus':hoststatus, 
                                  'tcp':tcp, 
                                  'udp':udp})

        self.do.append(new_entry_df)

    def validatePortscan(self):
        self.do.df = self.do.df.apply(ap_validate_scan,axis=1)
        self.do.df.fillna("",inplace=True)
        try:
            self.do.df.drop(columns=['Unnamed: 0'], inplace=True)
        except:
            pass
        self.do.df = self.do.df[~self.do.df.ip.duplicated()]
 
    def returnPortscan(self, ip):
        try:
            return extract_scan(self.do.df, ip)
        except NoScanAvailable:
            return ""

    def returnData(self, ip):
        output = self.do.df[self.do.df.ip == ip]
        return output
    ############### Directory Traversal #########


if __name__ == '__main__':

    mg = MergeResults(result_list)
    mg.MergeSubDomain(mg.result_list)

    df= mg.sub_df

    debug_here()

