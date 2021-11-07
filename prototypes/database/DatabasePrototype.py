import uuid
from utils.RaasLogger import RaasLogger
from utils.threadutil import *

from sqlalchemy import create_engine, inspect, insert, select
from sqlalchemy.orm import scoped_session, sessionmaker

from utils.datasupport import *
from prototypes.thread.ThreadPrototype import ThreadPrototype
from datatools.dataprototypes.datastructures import create_schema, URLInputTable

from IPython.core.debugger import Tracer; debughere=Tracer()


data_model_mapping_dict = {"pathinput": URLInputTable}


class DatabaseInitPrototype(ThreadPrototype):
    """
    Threading Class that will create the connector to the dataase
    For each running RAAS scope will be created a unique DatabaseConnector Thread. 
    
    Attributes
    ----------
    db_session : sqlalchemy.orm
        database connection that supports bulk input and orm
    scope : str
        scope domain will identify the scope database
    dbtype : str
        database backend (sqlite or postgres)
    sqlitefile : str
        string with the location of sqlite file
    postgre_ip : str
        IP address for postgres database
    interval: int
        how often the data is fetched from the tool

    Methods
    -------
    init_db():
        will connect to database and initialize if empty
    check_sqlite_file_empty():
        check if scope database is empty
    connect_sqlite():
        connect to sqlite scope database
    insert_bulk():
        bulk insert data into database
    """

    def __init__(self, scope, db, sqlitefile, postgre_ip, postgre_port):
        #super(DatabaseInitPrototype, self).__init__(scope, db, sqlitefile, postgre_ip, postgre_port)
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


class DatabaseInputPrototype(DatabaseInitPrototype):

    def insert_bulk(self, table_name, data_dict):
        table_model = None
        try:
            table_model = data_model_mapping_dict[table_name]
        except:
            print("not found model_name")
        self.db_session.bulk_insert_mappings(table_model, pop_all(data_dict))
        self.db_session.commit()


class DatabaseOutputPrototype(DatabaseInitPrototype):
    
    def get_table(self, table_name):
        table_model = None
        try:
            table_model = data_model_mapping_dict[table_name]
        except:
            print("not found model_name")
        debughere()
        q = select([table_model])
        table_iterator = self.dbe.execution_options(stream_results=True).execute(q)
        while 'batch not empty': 
            batch = table_iterator.fetchmany(10000)
            if not batch:
                break
            
            yield [row for row in batch]

        table_iterator.close()
        #whole_table = self.db_session.query(table_model).all()


class DatabasePrototype(DatabaseInputPrototype, DatabaseOutputPrototype):
    def __init__(self, scope, db, sqlitefile, postgre_ip, postgre_port):
        super(self.__class__, self).__init__(scope, db, sqlitefile, postgre_ip, postgre_port)


    