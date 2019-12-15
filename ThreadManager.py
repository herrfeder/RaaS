
import SubdomainCollector
import MergeResults
import PortScanner
import DirectoryTraversal
import Spider

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Manager(object, metaclass=Singleton):

        def newSubdomainCollector(self, domain_name, env=""):
            return SubdomainCollector.SubdomainColl( domain_name, env)

        def newMergeResults(self, env, do="", columns="", result_list="", load=False):
            return MergeResults.MergeResults(env, do, columns, result_list, load)

        def newPortScanner(self, env=""):
            return PortScanner.PortScanner(env)

        def newDirectoryTraversal(self, env=""):
            return DirectoryTraversal.DirectoryTraversal(env)

        def newSpider(self, env="", start_url=""):
            return Spider.Spider(env, start_url)

        def threadFinished(self, thread, data, finishedHandler=None):
            print(thread, data)
            if finishedHandler != None:
                finishedHandler.setFinishedData(data)
            # TODO build nice POPUP for more information
            #routes.updateStatus(True, data)

threadManager = Manager()
