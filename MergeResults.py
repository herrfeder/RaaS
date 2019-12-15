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

    def __init__(self, env, do="", columns="", result_list="", load=False):
        super(MergeResults, self).__init__()
        self.thread = threading.Thread(target=self.run, args=())
        self.thread.deamon = True
        self.result_list = result_list
        self.fin = 0
        self.env = env
        if do:
            self.do = do
        else:
            self.do = DataObject(env,)
        if load:
            self.do.load_from_sqlite()
 
    def run(self):
        if self.env['dftype'] == "subdomain":
            print("[*] Running Module: MergeResults for Subdomains")
            self.merge_subdomain(self.result_list)
        if self.env['dftype'] == "portscan":
            print("[*] Running Module: MergeResults for Portscan")
            self.merge_portscan(self.result_list)
        if self.env['dftype'] == "dirtraversal":
            print("[*] Running Module: MergeResults for DirectoryTraversal")
            self.merge_dirtraversal(self.result_list)


    def get_fin(self):
        return self.fin

    ############# DirTraversal ##########
    def merge_dirtraversal(self, result_list):
        self.do.create_from_dict_list(result_list)

    ############ Spider #################

    def merge_spider(self, result_list):
        jpg_df = df[df[0].str.endswith("jpg")]
        jpg_df.apply(lambda x: "/".join(x[0].split("/")[:-1])+"/",axis=1)

    ############# Subdomain #############
    def domain_to_ip(self,domain):
        df = self.do.return_df("subdomain")
        try:
            return df[df['domain'] == domain]['ip4_1'].item()
        except:
            return ""

    def get_ip_list(self):
        df = self.do.return_df("subdomain")
        debughere()
        ip_list = [(x1,x2) for x1,x2 in zip(df.ip4_1,df.ip4_2)]
        ip_list = pd.Series(sum(ip_list, ()))
        ip_list = ip_list[ip_list != ""]
        return ip_list[~ip_list.duplicated()].reset_index().drop(columns=['index'])

    def get_domain_list(self):
        df = self.do.return_df("subdomain")
        domain_list = df.domain
        domain_list = [x for x in domain_list if x != ""]
        return domain_list


    def merge_subdomain(self, result_list):

        self.extract_sub_dict(result_list)

    def sub_append(self, domain='', ip4_1='', ip4_2='', ip6_1='', ip6_2='', checkdup=True):

        df = self.do.return_df("subdomain")

        new_entry_df = pd.Series({'domain':domain,
                                  'ip4_1':ip4_1, 'ip4_2':ip4_2,
                                  'ip6_1':ip6_1, 'ip6_2':ip6_2})
        if checkdup:
            duplicated = df[df.domain == domain]
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

    def extract_subdict(self, result_list):
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

    def merge_portscan(self, result_list):
        for entry in result_list:
            self.portscan_append(entry['ip'],entry['hoststatus'],entry['tcp'],entry['udp'])

        self.validate_portscan()

    def portscan_append(self, ip='', hoststatus='', tcp='', udp=''):

        new_entry_df = pd.Series({'ip':ip, 
                                  'hoststatus':hoststatus, 
                                  'tcp':tcp, 
                                  'udp':udp})

        self.do.append(new_entry_df)

    def extract_portscan(self):
        self.do.df = self.do.df.apply(w_extract_scan,axis=1)
        self.do.df.fillna("",inplace=True)
        try:
            self.do.df.drop(columns=['Unnamed: 0'], inplace=True)
        except:
            pass
        self.do.df = self.do.df[~self.do.df.ip.duplicated()]
 
    def validate_portscan(self):
        df = self.do.return_df("portscan")
        ip_list = df.ip.unique()
        debughere()
        if 1*(df['state'] == "open").sum() > 0:
            row['host'] = "up"
        else:
            row['host'] = "verify"

        #### check for port type ####
        webfilt = scan_df[scan_df['port'].isin(["80","81","8080","8081","443","4443"])]
        if not webfilt.empty:
            row['web'] = ":".join(list(webfilt.port))
        '''
        elif row['port'] in ["22"]:
            row['type'] = "ssh"
        else:
            row['type'] = "verify"
        '''
        return row

    def return_portscan(self, ip):
        try:
            return extract_scan(self.do.df, ip)
        except NoScanAvailable:
            return ""

    def return_data(self, ip):
        output = self.do.df[self.do.df.ip == ip]
        return output
    ############### Directory Traversal #########


if __name__ == '__main__':

    mg = MergeResults(result_list)
    mg.MergeSubDomain(mg.result_list)

    df= mg.sub_df

    debug_here()

