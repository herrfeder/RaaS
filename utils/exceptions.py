from utils.RaasLogger import RaasLogger

class Error(Exception):
    '''
    Base class for other Exceptions
    '''
    def __init__(self):
        self.logger = RaasLogger(self.__class__.__name__)


class SingletonAlreadyExists(Error):
    def __init__(self):
        super(SingletonAlreadyExists, self).__init__()
        self.logger.error("This Singleton already exists and cannot created twice")

class WrongProjectEnvironment(Error):
    pass

class WrongDomainSyntax(Error):
    #print("You need to use at least this syntax. Example: http://url.com")
    pass

class DomainNoIp(Error):
    #print("This domain doesn't have an IP address, maybe typo?")
    pass

class NoScanAvailable(Error):
    pass

class WrongDataFrameSize(Error):
    pass

class SpiderError(Error):
    pass

class ServerBlocked(Error):
    pass
