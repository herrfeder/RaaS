#import crawlers.SubdomainCollector as SubdomainCollector
from datatools import MergeResults
#import PortScanner
#import crawlers.DirectoryTraversal as DirectoryTraversal

from prototypes.ThreadPrototype import *
import signal
import threading
import crawlers.PathCollector as PathCollector
import crawlers.WebSpider as WebSpider
from utils.RaasLogger import RaasLogger
import uuid


#@Singleton
#class SingletonDatabaseConnector(self, database_host="127.0.0.1", database_port=5432, database_name="raas")
#    #    return DatabaseConnector.DatabaseConnector(database_host, database_port, database_name)


 

class AppThreadManager(AppSingleton):

    def __init__(self, app_id):
        super(AppSingleton, self).__init__(app_id)
        self.appid = app_id   


    def newMergeResults(self, env, columns="", result_list="", load=False):
        return MergeResults.MergeResults(env, columns, result_list, load)


class ScopeThreadManager(ScopeSingleton):

    def __init__(self, scope_name):
        super(ScopeSingleton, self).__init__(scope_name)
        self.scope = scope_name


    def newPathCollector(self, domain_name, env=""):
        self.logger.debug(f"Created new Pathcollector with {domain_name}")
        return PathCollector.PathCollector( domain_name, env )


    def newWebSpider(self, domain_name, env=""):
        return WebSpider.WebSpider( domain_name, env )

