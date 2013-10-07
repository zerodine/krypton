__author__ = "Thomas Spycher, Philipp Spinnler"
__copyright__ = "Copyright 2013, Zerodine GmbH (zerodine.com) "
__credits__ = ["Thomas Spycher", "Philipp Spinnler"]
__license__ = "Apache-2.0"
__version__ = "0.0.1"
__maintainer__ = "Thomas Spycher"
__email__ = "me@tspycher.com"
__status__ = "Development"


class ReconPartner(object):

    _url = None
    _hashes = None
    _model = None

    def __init__(self, url, hashes, model = None):
        self._url = url
        self._hashes = hashes
        self._model = model

    def getHashes(self):
        return set(self._hashes)

    def getKey(self, hash= None, keyId=None):
        if self._model:
            if hash:
                return self._model.retrieveKey(hash=hash)
            else:
                return self._model.retrieveKey(keyId=keyId)

        # TODO: handle http key retrieval

    def storeKey(self, asciiArmoredKey):
        if self._model:
            self._model.uploadKey(asciiArmoredKey=asciiArmoredKey, force=True, externalUpload=True)
            return

        # TODO: handle http key upload
