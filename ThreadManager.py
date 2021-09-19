#import crawlers.SubdomainCollector as SubdomainCollector
from datatools import DataObject
#import PortScanner
#import crawlers.DirectoryTraversal as DirectoryTraversal
import queue
from prototypes.thread.SingletonPrototype import AppSingleton, ScopeSingleton
from prototypes.thread.ThreadPrototype import ThreadPrototype
import signal
import threading
from crawlers.PathCollector import PathCollector
#import crawlers.WebSpider as WebSpider
from utils.RaasLogger import RaasLogger
import uuid
import time
from IPython.core.debugger import Tracer; debughere = Tracer()



 

class AppThreadManager(AppSingleton):

    def __init__(self, app_id):
        super(AppSingleton, self).__init__(app_id)
        self.appid = app_id
        

    def newMergeResults(self, env, columns="", result_list="", load=False):
        return MergeResults.MergeResults(env, columns, result_list, load)


class QueueObserver(ThreadPrototype):
    def __init__(self, write_lock_setter):
        super(self.__class__, self).__init__()
        self.logger = RaasLogger(self.__class__.__name__)
        self.taskqueue = queue.SimpleQueue()
        self.write_lock_setter = write_lock_setter

    def write_lock_setter(self, lockvalue=""):
        self.write_lock_setter(lockvalue)


    def put(self, queue_object):
        self.taskqueue.put(queue_object)
    
    def run(self):
        while True:
            if (not self.write_lock_setter()) and (not self.taskqueue.empty()):
                print(f"Run in QueueObserver {self.write_lock_setter()}")
                self.logger.info("Getting task from queue")
                task = self.taskqueue.get()
                task.start()
                time.sleep(1)
            else:
                time.sleep(1)



class ScopeThreadManager(ScopeSingleton):

    def __init__(self, scope):
        super(ScopeSingleton, self).__init__(scope)
        self.scope = scope
                    
        self.logger.debug(f"Creating DataObject for Scope {scope}")
        self.daob = DataObject.DataObject(self.scope)
        self._write_lock = False
        self.QuOb = QueueObserver(self.write_lock_setter)
        self.QuOb.start()


    @property
    def write_lock(self):
        return self._write_lock


    def write_lock_setter(self, lockvalue=""):
        if self._write_lock and (lockvalue == False):
            self.logger.info("Unlocking the Write Lock")
            self._write_lock = lockvalue
        elif not self._write_lock and (lockvalue == True):
            self.logger.info("Locking the Write Lock")
            self._write_lock = lockvalue
        else:
            return self.write_lock


    def newPathCollector(self, domain_name, tool):
        self.logger.debug(f"Created new Pathcollector for Scope {domain_name}")
        self.QuOb.put(PathCollector(domain_name, self.daob, tool, self.write_lock_setter))
        #self.taskqueue.put(analyzer)


    def newWebSpider(self, domain_name):
        return WebSpider.WebSpider(domain_name)

