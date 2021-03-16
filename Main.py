import ThreadManager
import threading
from IPython.core.debugger import Tracer
#from exceptions import DomainNoIp
from utils.raaslogging import RaasLogger

debughere=Tracer()

env = {"dftype":"","project":"eurid.eu"}

if __name__ == '__main__':

    logger = RaasLogger()

    logger.info("Start new job")
    pc = ThreadManager.ThreadManager.newPathCollector("https://deezer.com",{})
    pc.start()

    for thread in threading.enumerate(): 
        print(thread.name)
        debughere()

    
