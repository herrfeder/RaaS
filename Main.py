import ThreadManager
import threading
from IPython.core.debugger import Tracer
#from exceptions import DomainNoIp
from utils.RaasLogger import RaasLogger

debughere=Tracer()

env = {"dftype":"","project":"eurid.eu"}

if __name__ == '__main__':

    logger = RaasLogger("main_logger")

    logger.warning("Start new job")
    logger.mainlogger.info("blahhhhh")
    pc = ThreadManager.ThreadManager.newPathCollector("https://deezer.com",{})
    pc.start()

    for thread in threading.enumerate(): 
        print(thread.name)
        debughere()

    
