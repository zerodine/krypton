import gnupg

from gpgabstractinterface import GpgAbstractInterface

class Gpg(GpgAbstractInterface):

    _gpg = None

    def __init__(self):
        self._gpg = gnupg.GPG(gnupghome='/tmp', gpgbinary="/usr/local/bin/gpg")

    def loadPublicKey(self, asciiarmoredkey):
        self._gpg.import_keys(key_data=asciiarmoredkey)

    def getIdentities(self):  # -> list
        return

    def getKeydetails(self):  # -> dict
        x = self._gpg.list_keys()
        result = {"keyid": None,
                  "expires": None,
                  "length": None,
                  "algo": None,
                  "fingerprint": None,
                  "date": None,
                  "type": None}

        for k in result.iterkeys():
            if k in dict(x[0]):
                result[k] = x[0][k]
        return result

    def getSubkeys(self):  # -> list
        return

    def receiveKeyFromServer(self, keyid, server):
        return
