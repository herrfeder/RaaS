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

    logger = RaasLogger("main")

    stm = ScopeThreadManager("deezer.com")
    #stm_new = ScopeThreadManager("deezerkack.com")
    #stm_new2 = ScopeThreadManager("deezerkack2.com")
    #atm = AppThreadManager(app_id)

    pc = stm.newPathCollector("https://deezer.com", "gau")
    pc.start()
    pc_02 = stm.newPathCollector("https://deezer.com", "gospider")
    pc_02.start()

    for thread in threading.enumerate(): 
        print(thread.name)
        debughere()

    
