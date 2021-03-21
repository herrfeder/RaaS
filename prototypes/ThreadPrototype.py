from IPython.core.debugger import Tracer; debughere = Tracer()



class SingletonBase(object):
    pass



class AppSingleton(SingletonBase):
    # from https://stackoverflow.com/questions/31875/is-there-a-simple-elegant-way-to-define-singletons/33201#33201
    def __new__(cls, *args, **kwds):
        it = cls.__dict__.get("__it__")
        if it is not None:
            pass
            #return it
        cls.__it__ = it = object.__new__(cls)
        it.init(*args, **kwds)
        return it

    def init(self, *args, **kwds):
        pass


class ScopeSingleton(SingletonBase):
    def __new__(cls, *args, **kwds):
        it = cls.__dict__.get("__it__")
        if (it != None) and (it.scope == args[0]):
            return it
        elif (it.scope != args[0]):
            cls.__it__ = it = object.__new__(cls)
            it.init(*args, **kwds)
            return it

    def init(self, *args, **kwds):
        pass
