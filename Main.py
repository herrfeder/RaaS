import ThreadManager
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
    atm = ThreadManager.AppThreadManager(app_id)



    stm = ThreadManager.ScopeThreadManager("deezer.com")
    stm_new = ThreadManager.ScopeThreadManager("deezerkack.com")


    #pc = stm.newPathCollector("https://deezer.com",{})
    #pc.start()

    for thread in threading.enumerate(): 
        print(thread.name)
        debughere()

    
