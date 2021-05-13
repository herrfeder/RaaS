import pandas as pd
import sqlite3
from prototypes.DataThreadPrototype import DataThreadPrototype

import glob
import time
import datetime
from IPython.core.debugger import Tracer; debug_here = Tracer()
from utils.RaasLogger import RaasLogger

class DataObject(DataThreadPrototype):
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

    def append(self, new_entry):
        self.df = self.df.append(new_entry, ignore_index=True)

    def drop_index(self, index):
        self.df.drop(index, inplace=True)

    def save_to_csv(self):

        timedate = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        self.df.to_csv("data/"+timedate+self.project+"_"+self.dftype+".csv")

    def save_to_sqlite(self,append=False):

        try:
            conn = sqlite3.connect("data/"+self.project)
            if append:
                self.df.to_sql(self.dftype, con=conn, if_exists='append')
            else:
                self.df.to_sql(self.dftype, con=conn)

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

    def load_from_sqlite(self,append=False):

        try:
            conn = sqlite3.connect("data/"+self.project)
            self.df = pd.read_sql_table(self.dftype, con=conn)

        except Error as e:
            print(e)

    def check_existance(self, filtercol, filterval, checkcol='', checkval=''):

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



if __name__ == "__main__":
    do = DataObject(["blah"],"blah","blah")
    for i in range(1,10):
        do.saveToCSV()
        time.sleep(2)
    debug_here()
    '''
