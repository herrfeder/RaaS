class Error(Exception):
    '''
    Base class for other Exceptions
    '''
    pass

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
