#import crawlers.SubdomainCollector as SubdomainCollector
#import MergeResults
#import PortScanner
#import crawlers.DirectoryTraversal as DirectoryTraversal
import crawlers.PathCollector as PathCollector

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

#    def newPortScanner(self, env=""):
#        return PortScanner.PortScanner(env)

#    def newDirectoryTraversal(self, env=""):
#        return DirectoryTraversal.DirectoryTraversal(env)

#    def newSubdomainCollector(self, domain_name, env=""):
#        return SubdomainCollector.SubdomainColl( domain_name, env)

    def newPathCollector(self, domain_name, env=""):
        return PathCollector.PathCollector(domain_name, env)


ThreadManager = ThreadManager()
#SingletonThreadManager = SingletonThreadManager()
