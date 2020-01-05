import pandas as pd
import threading
from IPython.core.debugger import Tracer; debughere = Tracer()
import datetime
from DataObject import DataObject
from itertools import chain
from exceptions import NoScanAvailable
import json
from datasupport import *
from misc.settings import raas_dictconfig
from logging.config import dictConfig
import logging

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
        dictConfig(raas_dictconfig)
        self.lgg = logging.getLogger("RAAS_mergeresults")
        self.result_list = result_list
        self.fin = 0
        self.env = env
        if do:
            self.do = do
            self.do.project = env["project"]
            self.do.dftype = env["dftype"]
        else:
            self.do = DataObject(env,)
        if load:
            self.do.load_from_sqlite()
            self.init_hosts(env["dftype"])


    def run(self):
        if self.env['dftype'] == "subdomain":
            self.lgg.info("[*] Running Module: MergeResults for Subdomains")
            self.merge_subdomain()
        if self.env['dftype'] == "portscan":
            self.lgg.info("[*] Running Module: MergeResults for Portscan")
            self.merge_portscan()
        if self.env['dftype'] == "dirtraversal":
            self.lgg.info("[*] Running Module: MergeResults for DirectoryTraversal")
            self.merge_dirtraversal()
        if self.env['dftype'] == "spider":
            self.lgg.info("[*] Running Module: MergeResults for Spider")
            self.merge_spider()

    def get_fin(self):
        return self.fin


    ################ Hosts ######################

    def init_hosts(self, dftype):
        if dftype == "subdomain":
            self.do.ddf["subdomain"].apply(self.add_host_sub_apply,axis=1)

        self.do.ddf["hosts"].fillna(value="none", inplace=True)

    def add_host_sub_apply(self, row):
        self.add_host_sub(row["ip4_1"],row["ip4_2"],row["domain"])

    def add_host_sub(self, ip4_1, ip4_2, domain):
        df = self.do.ddf["hosts"]
        if (ip4_1 == None) and (ip4_2 == None):
            if df[df["domain"] == domain].shape[0] == 0:
                self.do.ddf["hosts"] = df.append({"domain":domain,"purpose":""}, ignore_index=True)
        elif (ip4_2 == None):
            if df[df["ip"] == ip4_1].shape[0] == 0:
                self.do.ddf["hosts"] = df.append({"ip":ip4_1,"domain":domain,"purpose":""}, ignore_index=True)
        if (ip4_2 != None):
            if df[df["ip"] != ip4_2].shape[0] == 0:
                self.do.ddf["hosts"] = df.append({"ip":ip4_2,"domain":domain,"purpose":""}, ignore_index=True)

    def validate_portscan(self):
        port_df = self.do.return_df("portscan")
        ip_list = port_df.ip.unique()
        for ip in ip_list:
            df = port_df[port_df["ip"] == ip]
            if 1*(df['state'] == "open").sum() > 0:
                self.do.ddf['hosts'].loc[self.do.ddf['hosts'].ip == ip, "state"] = "up"
            else:
                self.do.ddf['hosts'].loc[self.do.ddf['hosts'].ip == ip, "state"] = "verify"

        # check for port type
        webfilt = port_df[port_df['port'].isin(["80","81","8080","8081","443","4443"])]
        if not webfilt.empty:
            self.do.ddf['hosts'].loc[self.do.ddf['hosts'].ip == ip, "purpose"] += ",web"
 
        sshfilt = port_df[port_df['port'].isin(["22"])]
        if not sshfilt.empty:
            self.do.ddf['hosts'].loc[self.do.ddf['hosts'].ip == ip, "purpose"] += ",ssh"

    def get_host_state(self,ip):
        return self.do.ddf['hosts'].loc[self.do.ddf['hosts'].ip == ip, "state"]

    ############# DirTraversal ##########

    def merge_dirtraversal(self):
        self.do.create_from_dict_list(self.result_list)

    ############# Subdomain #############
    
    def domain_to_ip(self,domain):
        df = self.do.return_df("subdomain")
        try:
            return df[df['domain'] == domain]['ip4_1'].iloc[0]
        except:
            return ""

    def get_ip_list(self):
        df = self.do.return_df("subdomain")
        ip_list = [(x1,x2) for x1,x2 in zip(df.ip4_1,df.ip4_2)]
        ip_list = pd.Series(sum(ip_list, ()))
        ip_list = ip_list[ip_list != ""]
        return ip_list[~ip_list.duplicated()].reset_index().drop(columns=['index'])

    def get_domain_list(self):
        df = self.do.return_df("subdomain")
        domain_list = df.domain
        domain_list = [x for x in domain_list if x != ""]
        return domain_list


    def merge_subdomain(self):

        self.extract_sub_dict(self.result_list)
        #self.update_hosts("subdomain")

    def sub_append(self, domain='', ip4_1='', ip4_2='', ip6_1='', ip6_2='', checkdup=True):

        df = self.do.ddf["subdomain"]
        new_entry_df = pd.Series({'domain':domain,
                                  'ip4_1':ip4_1, 'ip4_2':ip4_2,
                                  'ip6_1':ip6_1, 'ip6_2':ip6_2})
        if df.empty:
            self.do.append_row(new_entry_df)
            return 1

        if checkdup:
            duplicated = df[df.domain == domain]
            if duplicated.shape[0] > 0:
                ip4_2 = [x for x in duplicated['ip4_1']]
                ip6_2 = [x for x in duplicated['ip6_1']]

                if  ((duplicated.ip4_1.empty) and (not new_entry_df.ip4_1.empty)) or\
                    ((duplicated.ip4_2.empty) and (not new_entry_df.ip4_2.empty)) or\
                    ((duplicated.ip6_1.empty) and (not new_entry_df.ip6_1.empty)) or\
                    ((duplicated.ip6_2.empty) and (not new_entry_df.ip6_2.empty)):
                        self.add_host_sub(ip4_1=new_entry_df['ip4_1'],
                                      ip4_2=new_entry_df['ip4_2'],
                                      domain=new_entry_df['domain'])
                        self.do.append_row(new_entry_df)
                        self.do.drop_index(duplicated.index)
                        return 1
                else:
                    return 2
            else:

                self.do.append_row(new_entry_df)
                self.add_host_sub(ip4_1=new_entry_df['ip4_1'],
                              ip4_2=new_entry_df['ip4_2'],
                              domain=new_entry_df['domain'])
                return 0

    def extract_sub_dict(self, result_list):
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
                    self.sub_append(key, ip4_1=popL(ip4), ip4_2=popL(ip4),
                                   ip6_1=popL(ip6), ip6_2=popL(ip6))
                elif (isinstance(value, list)):

                    if ":" in "".join(value):
                        self.sub_append(key, ip4_1="", ip6_1="".join(value))
                    if "." in "".join(value):
                        self.sub_apend(key, ip4_1="".join(value), ip6_1="")

                else:
                    if ":" in value:
                        self.sub_append(key, ip4_1="", ip6_1=value)
                    if "." in value:
                        self.sub_append(key, ip4_1=value, ip6_1="")


        return 1


    ################ Spider #####################

    def merge_spider(self):
        result_list, forms, form_comps = self.result_list
        for dict_entry in result_list:
            self.spider_link_append(dict_entry)
        self.do.ddf["spider"]["cookies"] = self.do.ddf["spider"]["cookies"].astype("str")
        self.do.ddf["spider"]["headers"] = self.do.ddf["spider"]["headers"].astype("str")
        self.do.init_update_dftype("forms")
        for dict_entry in forms:
            self.spider_link_append(dict_entry, "forms")
        self.do.ddf["forms"]["class"] = self.do.ddf["forms"]["class"].astype("str")
        self.do.init_update_dftype("formcomps")
        for dict_entry in form_comps:
            self.spider_link_append(dict_entry, "formcomps")
        self.do.ddf["formcomps"]["class"] = self.do.ddf["forms"]["class"].astype("str")

    def spider_link_append(self,  dict_entry, dftype=""):
        new_entry = pd.Series(dict_entry)
        self.do.append_row(new_entry, dftype)


    ################ Portscan ###################

    def merge_portscan(self, result_list, ip):
        if result_list:
            for port in result_list:
                dict_entry = result_list[port]
                dict_entry["port"] = port
                dict_entry["ip"] = ip
                self.portscan_append(dict_entry)


    def portscan_append(self, dict_entry):

        new_entry_df = pd.Series(dict_entry)
        self.do.append_row(new_entry_df)


    def extract_portscan(self):
        self.do.df = self.do.df.apply(w_extract_scan,axis=1)
        self.do.df.fillna("",inplace=True)
        try:
            self.do.df.drop(columns=['Unnamed: 0'], inplace=True)
        except:
            pass
        self.do.df = self.do.df[~self.do.df.ip.duplicated()]


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

