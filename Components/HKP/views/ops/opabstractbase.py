import abc


class OpAbstractBase(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def do(self, search = None, options = [], fingerprint = False, exact = False):
        return