import pandas as pd
import sqlite3
import glob
import time
import datetime
import sqlalchemy
from sqlalchemy import MetaData
from IPython.core.debugger import Tracer; debug_here = Tracer()

class DataObject():

    def __init__(self,columns,env, datascope=""):

        if columns:
            self.df = pd.DataFrame(columns=columns)

        self.dftype = env['dftype']
        self.project = env['project']
        pass
        self.conn = sqlalchemy.create_engine("sqlite:///data/"+self.project+".db")
        self.meta = MetaData(self.conn,reflect=True)
        #self.portscan = self.meta.tables['portscan']
        #self.dirtraversal = self.meta.tables['dirtraversal']
        self.table_types = ["master", "new", "temp",]
        self.time_stamp = "%Y%m%d%H%M"
        self.table_name_tpl = "{dftype}_{tabletype}_{timestamp}"

    def create_from_dict_list(self,result_list):
        self.df = pd.DataFrame()
        for result in result_list:
            if isinstance(result,list) and (len(result) > 1):
                for entry in result:
                    self.df = self.df.append(entry, ignore_index=True)
            elif isinstance(result,list) and (len(result) == 1):
                self.df = self.df.append(result, ignore_index=True)
        debug_here()

    def append(self, new_entry):
        self.df = self.df.append(new_entry, ignore_index=True)

    def drop_index(self, index):
        self.df.drop(index, inplace=True)

    def get_table_name(self, name):

        table_names = self.meta.keys()	

    def save_to_csv(self):

        timedate = datetime.datetime.now().strftime(self.time_stamp)
        self.df.to_csv("data/"+timedate+self.project+"_"+self.dftype+".csv")

    def save_to_sqlite(self, name, append=False):

        try:
            conn = sqlite3.connect("data/"+self.project+".db")
            if append:
                self.df.to_sql(self.get_table_name(name), con=conn, if_exists='append')
            else:
                self.df.to_sql(name, con=conn, if_exists='fail')

        except Error as e:
            print(e)

    def load_from_csv(self):

        files = sorted(glob.glob("data/*"+self.project+"_"+self.dftype+".csv"))
        if len(files) < 1:
            print("No CSV files to load from")
            return
        load_file = files.pop() 
        self.df = pd.read_csv(load_file)
        self.df.fillna('',inplace=True)

    def load_from_sqlite(self, name, append=False):

        try:
            conn = sqlite3.connect("data/"+self.project+".db")
            self.df = pd.read_sql_table(self.get_table_name(name), con=conn)

        except Error as e:
            print(e)

    def check_existence(self, filtercol, filterval, checkcol='', checkval=''):

        if checkval == '':
            if self.df[filtercol == filterval][checkcol] == None:
                return False
            else:
                return True
        else:
            if self.df[filtercol == filterval][checkcol] == checkval:
                return True
            else:
                return False

    def remove_duplicates_col(self,row, column):

        duplicates = self.df[self.sub_df[column] == row[column]]

        for dup in duplicates.iterrows():
            pass

    def return_table(self, table_name):
        
        if table_name not in self.conn.table_names():
            return "Wrong tablename"
        else:
            return pd.read_sql_table(table_name, self.conn)
        
    def return_domain_list(self):
        
        return pd.read_sql_table("subdomain", self.conn)['domain'].unique()
    
    def return_ip_list(self):
        
        return pd.read_sql_table("subdomain", self.conn)['ip4_1'].unique()
    
    def return_dirtraversal(self, domain):
        '''
        Returns a directory traversal scan for one or multiple Domains. As a single IP could be used for multiple domains.
        '''
        final_result = {}
        stats_result = {}
        overview_dt = "### <span style='color:#606200'>Dirtraversal Stats\n</span>"

        for single_domain in domain:
            s = select([self.dirtraversal]).where(self.dirtraversal.c.domain == single_domain)
            temp_result = pd.read_sql(s, self.conn)
            if temp_result.shape[0] > 0:
                stats_result[single_domain+'_number'] = temp_result.shape[0]
                stats_result[single_domain+'_200'] = temp_result[temp_result.status == "200"].shape[0]
                stats_result[single_domain+'_401'] = temp_result[temp_result.status == "401"].shape[0]
                stats_result[single_domain+'_403'] = temp_result[temp_result.status == "403"].shape[0]

                final_result[single_domain] = temp_result
                test=single_domain+'_'+'403'
                overview_dt = overview_dt + overview_dt_t.format(single_domain,
                                                                   stats_result[single_domain+'_number'],
                                                                   stats_result[single_domain+'_200'],
                                                                   stats_result[single_domain+'_401'],
                                                                   stats_result[single_domain+'_403'])
        return (final_result, overview_dt)

    
    def return_portscan(self, ip):

        stats_result = {}

        s = select([self.portscan]).where(self.portscan.c.ip == ip)
        result = pd.read_sql(s, self.conn)
        if result.shape[0] > 1:
            df = extract_scan(result.iloc[0])
            stats_result['open'] = df[df.state == "open"].shape[0]
            stats_result['filtered'] = df[df.state == "filtered"].shape[0]
            overview_ps = overview_ps_t.format(ip,
                                               stats_result['open'],
                                               stats_result['filtered'])

            return (df, overview_ps)

        elif result.shape[0] == 0:
            return pd.DataFrame()

        else:
            df = extract_scan(result)

            stats_result['open'] = df[df.status == "open"].shape[0]
            stats_result['filtered'] = df[df.status == "filtered"].shape[0]

            overview_ps = overview_ps_t.format(ip,
                                               stats_result['open'],
                                               stats_result['filtered'])
            return (df, overview_ps)

    def ip_to_domain(self, ip):

        df = self.return_table("subdomain")

        if not df.empty:
            return list(df.query("ip4_1==@ip")["domain"].values)
        else:
            return ""

    def domain_to_ip(self, domain):
        
        df = self.return_table("subdomain")
        
        if not df.empty:
            return df.query("domain==@domain")["ip4_1"].values
        else:
            return ""

if __name__ == "__main__":
    do = DataObject(["blah"],"blah","blah")
    for i in range(1,10):
        do.saveToCSV()
        time.sleep(2)
    debug_here()

