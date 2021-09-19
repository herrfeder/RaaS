import sys
from threading import Event
import subprocess
import uuid
import json
from IPython.core.debugger import Tracer; debug_here = Tracer()

from utils.RaasLogger import RaasLogger
from utils.threadutil import *
from utils.datasupport import *

from prototypes.thread.ThreadPrototype import ThreadPrototype

# TODO: needs to be initiated in a seperated class
from prototypes.database.DatabasePrototype import DatabasePrototype as DatabaseConnector




class DataLinker(ThreadPrototype):
    """
    Threading Class that parses source data from RAAS modules into data dictionary.
    For each running RAAS module will be created a unique DataLinker Thread. 
    
    Attributes
    ----------
    datatype : str
        type of data structure that originates from running module
    source_data : list
        list of individual data payloads from RAAS module output
    stopped : threading.Event
        signal to stop the running thread
    source_tool : str
        name of tool that defines the explicit data fields to catch
    interval: int
        how often the data is fetched from the tool

    Methods
    -------
    run():
        starts thread and will fetch data based on set interval and stop event
    parse_datatype_dict():
        parses source data into target data based on datatype and source_tool

     
    """
    def __init__(self, datatype, source_data, event, source_tool="generic",  interval=5):
        super(self.__class__, self).__init__()
        self.log = RaasLogger(self.__class__.__name__)

        self.datatype = datatype
        self.source_data = source_data
        self.stopped = event
        self.source_tool = source_tool
        self.interval = interval


        self.target_data = []

    @name_thread_datalinker
    def run(self):
        while not self.stopped.wait(self.interval):
            if self.source_data:
                self.log.debug(f"Getting {len(self.source_data)} data elements")
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



class DataLinkerDict(ThreadPrototype):
    """
    Threading class that manages the seperate DataLinker into a single dictionary with event handler.
    For each running scope database one unique DataLinkerDict will be created.

    Attributes
    ----------
    datalinker_d : str
        dictionary with DataLinker objects

    Methods
    -------
    add_linker():
        appending DataLinker object to DataLinker Dictionary
    create_linker():
        creates new DataLinker object and adds it to DataLinker Dictionary


    """
    def __init__(self):
        super(self.__class__, self).__init__()
        self.log = RaasLogger(self.__class__.__name__)
        
        self._datalinker_d = {}


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


class DataLinkerObserver(ThreadPrototype):
    """
    Threading class to check DataLinkerDict with all DataLinker target_data's for existing data and pushing into database.
    For each running scope database one unique DataLinkerObserver will be created. (TODO: Concurrent multiple observers)

     Attributes
    ----------
    db_con : DatabaseConnector
        database connection object
    dl_dict : DataLinkerDict
        dictionary of DataLinkers that will be observed for occuring data 

    Methods
    -------
    register():
        register a Datalinker Dict for observing
    run():
        parses source data into target data based on datatype and source_tool
    is_datalinker_dict_empty():
        checks if any target_data exists and is empty


    """
    def __init__(self, database_con):
        super(self.__class__, self).__init__()
        self.log = RaasLogger(self.__class__.__name__)

        self.db_con = database_con
        self.dl_dict = {}

    def register(self, dl_dict):
        self.dl_dict = dl_dict

    @name_thread_datalinker_observer
    def run(self):
        self.log.info(f"Start DataLinkerObserver for scope {self.db_con.scope}")
        while True:
            for el in list(self.dl_dict.keys()):
                if self.dl_dict[el]["datalinker_object"].target_data:
                    target_data = self.dl_dict[el]["datalinker_object"].target_data
                    self.log.debug(f"Inserting {len(target_data)} data elements")
                    self.db_con.insert_bulk(pop_all(target_data))
        else:
            self.log.debug("The dl_dict isn't registered yet")


    def is_datalinker_dict_empty(self):
        linker_keys = list(self.dl_dict.keys())
        if not len(linker_keys):
            return True
        else:
            if any(len(self.dl_dict[lk]["datalinker_object"].target_data) for lk in linker_keys):
                return False
            else:
                return True


class DataPrototype(ThreadPrototype):
    """
    Threading Class that inits and interfaces all previous Classes in this file.
    For each running RAAS scope will be created a unique DataThreadPrototype. 
    It manages:
        - Database Connection (DatabaseConnector)
        - DataLinker Dictionary (DataLinkerDict)
        - Pushing Data to Database (DataLinkerObserver)
        - Handling Threading Events

    Attributes
    ----------
    scope : str
        scope domain will identify the scope database
    datacon : DatabaseConnector
        Database Connection object
    DLDict : DataLinkerDict
        DataLinker Dictionary, holds all Linker that connects module data
    DLObserver : DataLinkerObserver
        Observes the Datalinker Dictionary and pushes occuring data to the database
   

    Methods
    -------
    finish_cb() :
        When Thread finishes gracefully running post-execution tasks
    interrupt_cb():
        When Thread got killed ungracefully running tasks to prevent loosing data
    get_input_linker():
        adding new DataLinker
    """

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


    def interrupt_cb(self, force):
        if not force:
            self.log.info("Thread got killed and will be finished gracefully, write everything to database and quit.")
            if not DLObserver.is_datalinker_dict_empty():
                time.sleep(1)
        else:
            self.log.info("Thread got killed and got forced to exit, kill without rescuing data.")


    def get_input_linker(self, datatype, source_data, source_tool="generic", interval=5):
        return self.DLDict.create_linker(datatype, source_data, source_tool, interval)









