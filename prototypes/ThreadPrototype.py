from IPython.core.debugger import Tracer; debughere = Tracer()
from utils.exceptions import SingletonAlreadyExists
from utils.RaasLogger import RaasLogger

class SingletonBase(object):

    def __init__(self, *args, **kwds):
        self.logger = RaasLogger(self.__class__.__name__)
        self.logger.info(f"Starting New {self.__class__.__name__} with {self.log_string} {args[0]}")


class AppSingleton(SingletonBase):
    # from https://stackoverflow.com/questions/31875/is-there-a-simple-elegant-way-to-define-singletons/33201#33201
    def __new__(cls, *args, **kwds):
        it = cls.__dict__.get("__it__")
        if it is not None:
            raise SingletonAlreadyExists
        else:
            cls.__it__ = it = SingletonBase.__new__(cls)
            it.log_string = "AppID"
            return it
       

class ScopeSingleton(SingletonBase):
    def __new__(cls, *args, **kwds):
        it = cls.__dict__.get("__it__")
        if (it is not None):
            if (args[0] in cls.__dict__.get("__scopes__")):
                raise SingletonAlreadyExists
            elif (it.scope != args[0]):
                cls.__it__ = it = SingletonBase.__new__(cls)
                cls.__scopes__.append(args[0])
                it.log_string = "Scope"
                return it
        else:
            cls.__it__ = it = SingletonBase.__new__(cls)
            cls.__scopes__ = [args[0]]
            it.log_string = "Scope"
            return it


