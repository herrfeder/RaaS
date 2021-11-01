import sys
import threading
import subprocess
from utils.RaasLogger import RaasLogger

class ThreadPrototype(threading.Thread): 

    def __init__(self):
        super(ThreadPrototype, self).__init__()
        self.thread = threading.Thread(target=self.run, args=())
        self.thread.deamon = True
        self.killed = False
        self.force = False
        self.__flag = threading.Event() # The flag used to pause the thread
        self.__flag.set() # Set to True
        self.__running = threading.Event() # Used to stop the thread identification
        self.__running.set() # Set running to True

    def __run(self): 
        sys.settrace(self.globaltrace) 
        self.__run_backup() 
        self.run = self.__run_backup 


    def pause(self):
        self.__flag.clear() # Set to False to block the thread

    def resume(self):
        self.__flag.set() # Set to True, let the thread stop blocking


    def start(self): 
        self.__run_backup = self.run 
        self.run = self.__run       
        threading.Thread.start(self)

    
    def globaltrace(self, frame, event, arg): 
        if event == 'call': 
            return self.localtrace 
        else: 
            return None
    

    def localtrace(self, frame, event, arg): 
        if self.killed: 
            if event == 'line':
                self.interrupt_cb(self.force)
                self.log.debug("The Thread got an kill signal. Exiting Thread.") 
                raise SystemExit() 
        return self.localtrace 
    

    def kill(self, force=False): 
        if force:
            self.force = True
        self.killed = True
        

    def finish_cb(self):
        self.log.debug("Thread finished gracefully, sending Data and quit.")
        while not self.results and not self.datalink.target_data:
            time.sleep(1)
        self.remove_lock()
        

    def interrupt_cb(self, force):
        if not force:
            self.log.info("Thread got killed and will be finished gracefully, sending Data and quit.")
            while not self.results and not self.datalink.target_data:
                time.sleep(1)
        else:
            self.log.info("Thread got killed got forced to exit, kill without rescuing data.")
        self.remove_lock()
    
    def check_set_lock(self):
        self.log.info("set lock")
        self.write_lock_setter(True)


    def remove_lock(self):
        self.log.info("Remove lock")
        self.write_lock_setter(False)
        