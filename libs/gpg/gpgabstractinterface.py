import abc

class GpgAbstractInterface(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def loadPublicKey(self, asciiarmoredkey):
        return

    @abc.abstractmethod
    def getIdentities(self):  # -> list
        return

    @abc.abstractmethod
    def getKeydetails(self):  # -> dict
        return

    @abc.abstractmethod
    def getSubkeys(self):  # -> list
        return

    @abc.abstractmethod
    def receiveKeyFromServer(self, keyid, server):
        return