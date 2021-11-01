from ThreadManager import ScopeThreadManager, AppThreadManager
import threading
from IPython.core.debugger import Tracer
#from exceptions import DomainNoIp
from utils.RaasLogger import RaasLogger
import uuid


app_id = uuid.uuid4()


debughere=Tracer()

env = {"dftype":"","project":"eurid.eu"}

if __name__ == '__main__':

    stm = ScopeThreadManager("deezer.com")
    stm.newPathAnalyzer("https://deezer.com")

    """
    logger = RaasLogger("main")

    stm = ScopeThreadManager("deezer.com")
    

    pc = stm.newPathCollector("https://deezer.com", "gau")
    pc_02 = stm.newPathCollector("https://deezer.com", "gospider")

    for thread in threading.enumerate(): 
        print(thread.name)
        debughere()
    """
    
