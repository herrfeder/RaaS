#import crawlers.SubdomainCollector as SubdomainCollector
#import MergeResults
#import PortScanner
#import crawlers.DirectoryTraversal as DirectoryTraversal
import signal
import threading
import crawlers.PathCollector as PathCollector
import crawlers.WebSpider as WebSpider



class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

#class SingletonThreadManager(object, metaclass=Singleton):
#
#
#    def newMergeResults(self, env, columns="", result_list="", load=False):
#        return MergeResults.MergeResults(env, columns, result_list, load)

    

#    def threadFinished(self, thread, data, finishedHandler=None):
#        print(thread, data)
#        if finishedHandler != None:
#            finishedHandler.setFinishedData(data)
#        # TODO build nice POPUP for more information
#        #routes.updateStatus(True, data)


class ThreadManager(object):

    def __init__(self):
        self.exit_event = threading.Event()
        signal.signal(signal.SIGINT, self.signal_handler)


    def signal_handler(signum, frame):
        self.exit_event.set()



#    def newPortScanner(self, env=""):
#        return PortScanner.PortScanner(env)

#    def newDirectoryTraversal(self, env=""):
#        return DirectoryTraversal.DirectoryTraversal(env)

#    def newSubdomainCollector(self, domain_name, env=""):
#        return SubdomainCollector.SubdomainColl( domain_name, env)

    def finish_callback(self):
        # put data into database
        print("I'm finished")


    def interrupt_callback(self, threadobj):
        print("I'm terminated")
        threadobj.process.kill()



    def interrupt_callback(self):
        print("I'm terminated but finished")


    def newPathCollector(self, domain_name, env=""):
        
        return PathCollector.PathCollector( domain_name, env, 
                                            finish_cb=self.finish_callback,
                                            interrupt_cb=self.interrupt_callback)


    def newWebSpider(self, domain_name, env=""):
        return WebSpider.WebSpider( domain_name, env, 
                                    finish_cb=self.finish_callback,
                                    interrupt_cb=self.interrupt_callback)


ThreadManager = ThreadManager()
#SingletonThreadManager = SingletonThreadManager()
