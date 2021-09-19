import pandas as pd
import sqlite3
from prototypes.DataPrototype import DataPrototype

import glob
import time
import datetime
from IPython.core.debugger import Tracer; debug_here = Tracer()
from utils.RaasLogger import RaasLogger


class DataObject(DataPrototype):
    def __init__(self, scope, db="sqlite", sqlitefile="/home/project/raas", postgre_ip="127.0.0.1", postgre_port=5432):

        super(self.__class__, self).__init__(scope, db, sqlitefile, postgre_ip, postgre_port)



    


    '''
    def dictlist_to_df(self,result_list):
        self.df = pd.DataFrame()
        for result in result_list:
            if isinstance(result,list) and (len(result) > 1):
                for entry in result:
                    self.df = self.df.append(entry, ignore_index=True)
            elif isinstance(result,list) and (len(result) == 1):
                self.df = self.df.append(result, ignore_index=True)
        debug_here()

    @property
    def project(self):
        return self._project

    def drop_index(self, index):
        self.df.drop(index, inplace=True)

    def save_to_csv(self):

    @dftype.setter
    def dftype(self, dftype):
        self._dftype = dftype
        self.init_update_dftype()

    def save_to_sqlite(self,append=False):


    def init_update_dftype(self, dftype=""):
        if dftype:
            now_dftype = dftype
        else:
            now_dftype = self._dftype
        try:
            if not self.ddf.get("now_dftype",""):
                self.ddf[now_dftype] = pd.DataFrame()
        except:
            if self.ddf["now_dftype"].empty:
                self.ddf[now_dftype] = pd.DataFrame()


    def check_dftype(self, new_dftype):
        if new_dftype:
            # needs further validation
            return new_dftype
        else:
            return self._dftype


    def update_hosts(self, col, value, ip="", subdomain=""):
        pass


    def append_row(self, new_entry, df_type=""):
        df_t = self.check_dftype(df_type)
        self.ddf[df_t] = self.ddf[df_t].append(new_entry, ignore_index=True)

    def load_from_csv(self):


    def create_from_dict_list(self, result_list, df_type=""):
        df_t = self.check_dftype(df_type)
        self.ddf[df_t] = pd.DataFrame()
        for result in result_list:
            if isinstance(result,list) and (len(result) > 1):
                for entry in result:
                    self.ddf[df_t] = self.ddf[df_t].append(entry, ignore_index=True)
            elif isinstance(result,list) and (len(result) == 1):
                self.ddf[df_t] = self.ddf[df_t].append(result, ignore_index=True)


    def save_to_csv(self, dftype=""):
        df_t = self.check_dftype(dftype)
        timedate = datetime.datetime.now().strftime(self.time_stamp)
        self.ddf[df_t].to_csv(self.csv_path.format(dftype=df_t,
                                                   timestamp=timedate))
 

    def load_from_csv(self, dftype=""):
        df_t = self.check_dftype(dftype)
        files = sorted(glob.glob("data/"+self.project+"_"+df_t+"*.csv"))
        if len(files) < 1:
            self.lgg.exception("No CSV files to load from")
            return

    def load_from_sqlite(self,append=False):

    def delete_table(self, table_name):
        table = Table(table_name, self.meta)
        table.drop()


    def save_to_sqlite(self, dftype="", tabletype="master", append=False, ovwr_master=False):
        df_t = self.check_dftype(dftype)
        try:
            table_name = self.table_name_tpl.format(dftype=df_t,
                                                    tabletype=tabletype,
                                                    timestamp=u.create_timestamp())
            ret_val = self.return_tablename(dftype=df_t, tabletype=tabletype)
            if ret_val == None:
                self.ddf[df_t].to_sql(table_name, con=self.conn, if_exists='fail')
            elif ovwr_master and (ret_val != None):
                self.ddf[df_t].to_sql(table_name, con=self.conn, if_exists='fail')
                self.delete_table(ret_val)
            elif append and (ret_val != None):
                self.ddf[df_t].to_sql(ret_val, con=self.conn, if_exists='append')

        except:
            self.lgg.exception("Got Error:")


    def check_existance(self, filtercol, filterval, checkcol='', checkval=''):

    def check_existence(self, filtercol, filterval, dftype="", checkcol="", checkval=""):
        df_t = self.check_dftype(df_type)
        if checkval == '':
            if self.ddf[df_t][filtercol == filterval][checkcol] == None:
                return False
            else:
                return True
        else:
            if self.ddf[df_t][filtercol == filterval][checkcol] == checkval:
                return True
            else:
                return False

    def remove_duplicates_col(self,row, column):

        duplicates = self.df[self.sub_df[column] == row[column]]

    def remove_duplicates_col(self,row, column, dftype=""):
        df_t = self.check_dftype(df_type)
        duplicates = self.ddf[df_t][self.sub_df[column] == row[column]]
        for dup in duplicates.iterrows():
            pass


    def return_tablename(self, dftype="", tabletype=""):
        df_t = self.check_dftype(dftype)
        if tabletype:
            tablename = df_t+"_"+tabletype
        else:
            tablename = df_t+"_"+"master"
        return self.return_table(tablename, only_check=True)

    def return_df(self, dftype="", tabletype = ""):
        df_t = self.check_dftype(dftype)
        if not self.ddf[df_t].empty:
            return self.ddf[df_t]
        else:
            # apply logic for ddf as well after implementing ddf into own class
            if tabletype:
                tablename = df_t+"_"+tabletype
            else:
                tablename = df_t+"_"+"master"
            return self.return_table(tablename)


    def return_table(self, table_name, only_check=False):
        if table_name not in self.conn.table_names():
            possible_names = [x for x in self.conn.table_names() if x.startswith(table_name)]
            if len(possible_names) < 1:
                self.lgg.exception("No table with the name {}".format(table_name))
                if only_check:
                    return None
                else:
                    return pd.DataFrame()
            else:
                newest_table = u.return_newest_string(possible_names)
                if only_check:
                    return newest_table
                else:
                    return pd.read_sql_table(newest_table, self.conn)
        else:
            if only_check:
                return table_name
            else:
                return pd.read_sql_table(table_name, self.conn)


    def return_dirtraversal(self, domain):
        
        Returns a directory traversal scan for one or multiple Domains. As a single IP could be used for multiple domains.
        
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


if __name__ == "__main__":
    do = DataObject(["blah"],"blah","blah")
    for i in range(1,10):
        do.saveToCSV()
        time.sleep(2)
    debug_here()
    '''
