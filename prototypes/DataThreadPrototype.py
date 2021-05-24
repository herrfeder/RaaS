import sys
from threading import Event
import subprocess
from prototypes.ThreadPrototype import ThreadPrototype
import uuid
from utils.RaasLogger import RaasLogger
from utils.threadutil import *

from sqlalchemy import create_engine, inspect, insert
from sqlalchemy.orm import scoped_session, sessionmaker


from datatools.dataprototypes.datastructures import create_schema, URLInputTable
import json
from IPython.core.debugger import Tracer; debug_here = Tracer()



def pop_all(l):
    r, l[:] = l[:], []
    return r



class DataLinker(ThreadPrototype):
    def __init__(self, datatype, source_data, event, source_tool="generic",  interval=5):
        #super(ThreadPrototype, self).__init__()
        super(self.__class__, self).__init__()

        self.log = RaasLogger(self.__class__.__name__)
        self.datatype = datatype
        self.source_data = source_data
        self.interval = interval
        self.stopped = event
        self.source_tool = source_tool

        self.target_data = []

    @name_thread_datalinker
    def run(self):
        while not self.stopped.wait(self.interval):
            if self.source_data:
                #self.log.info(f"Getting {len(self.source_data)} data elements")
                self.parse_datatype_dict()
                

    def parse_datatype_dict(self):
        if self.datatype == "pathinput":
            if self.source_tool == "gau":
                for dataline in pop_all(self.source_data):
                    self.target_data.append({"url":dataline.rstrip(), 
                                             "source":self.source_tool, 
                                             "urltype":"generic"})
            if self.source_tool == "gospider":
                for dataline in pop_all(self.source_data):
                    source_dict = json.loads(dataline)
                    self.target_data.append({"url":source_dict["output"].rstrip(),
                                             "source":self.source_tool,
                                             "urltype":source_dict["type"]})




class DataLinkerObserver(ThreadPrototype):
    def __init__(self, database_con):
        super(self.__class__, self).__init__()
        self.log = RaasLogger(self.__class__.__name__)

        self.db_con = database_con

    def register(self, dl_dict):
        self.dl_dict = dl_dict

    def run(self):
        while True:
            for el in list(self.dl_dict.keys()):
                if self.dl_dict[el]["datalinker_object"].target_data:
                    print(len(self.dl_dict[el]["datalinker_object"].target_data))
                    target_data = self.dl_dict[el]["datalinker_object"].target_data
                    self.log.info(f"Inserting {len(target_data)} data elements")
                    self.db_con.insert_bulk(pop_all(target_data))
                    print(len(self.dl_dict[el]["datalinker_object"].target_data))




class DataLinkerDict(ThreadPrototype):
    def __init__(self):
        
        self._datalinker_d = {}
        self._observers = []

    @property
    def datalinker_d(self):
        return self._datalinker_d
    

    def add_linker(self, dl_id, dl_object, dl_event, datatype):
        # observer here
        self.datalinker_d[dl_id] = {"datalinker_object": dl_object,
                                    "datalinker_event": dl_event,
                                    "datatype": datatype}

    
    def create_linker(self, datatype, source_data, tool,interval):
        datalinker_event = Event()
        datalinker_id = uuid.uuid4().hex
        datalinker_object = DataLinker(datatype, source_data, datalinker_event, tool, interval)

        self.add_linker(datalinker_id, 
                        datalinker_object,
                        datalinker_event, 
                        datatype)

        return self.datalinker_d[datalinker_id]



class DatabaseConnector(ThreadPrototype):
    def __init__(self, scope, db, sqlitefile, postgre_ip, postgre_port):
        self.log = RaasLogger(self.__class__.__name__)
        if db not in ["sqlite", "postgre"]:
            self.log.error(f"We have to quit, your given DB {db} isn't supported")

        self.db_session = scoped_session(sessionmaker())
        self.scope = scope
        self.dbtype = db
        self.sqlitefile = sqlitefile + "_" + scope + ".db"
        self.postgre_ip = postgre_ip
        self.init_db()


    def init_db(self):
        if self.dbtype == "sqlite":
            self.dbe = self.connect_sqlite()

        if self.check_sqlite_file_empty():
            self.log.info(f"SQLite Database for {self.scope} doesn't exist or is empty, initialize now.")
            create_schema(self.dbe)

        self.db_session.configure(bind=self.dbe, autoflush=False, expire_on_commit=False)



    def check_sqlite_file_empty(self):
        dbe_inspect = inspect(self.dbe)
        tables = dbe_inspect.get_table_names()
        if not tables:
            return True
        else:
            return False


    def connect_sqlite(self):
        sqlite_path = f"sqlite:///{self.sqlitefile}"
        dbe = create_engine(sqlite_path)
        self.log.info(f"Connected Successfully to SQLite Database with path {sqlite_path}")
        return dbe


    def insert_bulk(self, data_dict):
        self.db_session.bulk_insert_mappings(URLInputTable, pop_all(data_dict))
        self.db_session.commit()



class DataThreadPrototype(ThreadPrototype): 
    def __init__(self, scope, db, sqlitefile, postgre_ip, postgre_port):
        super(ThreadPrototype, self).__init__()
        self.log = RaasLogger(self.__class__.__name__)

        self.scope = scope
        self.datacon = DatabaseConnector(scope, db, sqlitefile, postgre_ip, postgre_port)

        self.DLDict = DataLinkerDict()
        self.DLObserver = DataLinkerObserver(self.datacon)

        self.DLObserver.register(self.DLDict.datalinker_d)
        self.DLObserver.start()


   


    def finish_cb(self):
        self.log.debug("Thread finished gracefully, writing everything important to DB and exit")
        return self.results


    def interrupt_cb(self, obj):
        self.log.debug("Thread got killed and will be finished gracefully, writing everything important to DB and exit.")
        return self.results


    def get_input_linker(self, datatype, source_data, source_tool="generic", interval=5):
        return self.DLDict.create_linker(datatype, source_data, source_tool, interval)









