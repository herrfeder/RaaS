#import crawlers.SubdomainCollector as SubdomainCollector
from datatools import DataObject
#import PortScanner
#import crawlers.DirectoryTraversal as DirectoryTraversal

from prototypes.thread.SingletonPrototype import AppSingleton, ScopeSingleton
import signal
import threading
from crawlers.PathCollector import PathCollector
import crawlers.WebSpider as WebSpider
from utils.RaasLogger import RaasLogger
import uuid
from IPython.core.debugger import Tracer; debug_here = Tracer()



 

class AppThreadManager(AppSingleton):

    def __init__(self, app_id):
        super(AppSingleton, self).__init__(app_id)
        self.appid = app_id
        

    def newMergeResults(self, env, columns="", result_list="", load=False):
        return MergeResults.MergeResults(env, columns, result_list, load)


class ScopeThreadManager(ScopeSingleton):

    def __init__(self, scope):
        super(ScopeSingleton, self).__init__(scope)
        self.scope = scope
                    
        self.logger.debug(f"Creating DataObject for Scope {scope}")
        self.daob = DataObject.DataObject(self.scope)
        self._write_lock = False


    @property
    def write_lock(self):
        return self._write_lock


    def write_lock_setter(self, lockvalue=""):
        if self._write_lock and (lockvalue == False):
            self.logger.info("Unlocking the Write Lock")
            self._write_lock = lockvalue
        elif not self._write_lock and (lockvalue == True):
            self.logger.info("Locking the Crawler Lock")
            self._write_lock = lockvalue
        else:
            return self.write_lock

    def newPathCollector(self, domain_name, tool):
        self.logger.debug(f"Created new Pathcollector for Scope {domain_name}")
        return PathCollector(domain_name, self.daob, tool, self.write_lock_setter)


    def newWebSpider(self, domain_name):
        return WebSpider.WebSpider(domain_name)

