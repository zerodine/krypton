import gnupg

from gpgabstractinterface import GpgAbstractInterface

class Gpg(GpgAbstractInterface):

    _gpg = None

    def __init__(self):
        self._gpg = gnupg.GPG(gnupghome='/tmp', gpgbinary="/usr/local/bin/gpg")

    def loadPublicKey(self, asciiarmoredkey):
        self._gpg.import_keys(key_data=asciiarmoredkey)

    def getIdentities(self):  # -> list
        x = self._gpg.list_keys()
        self._gpg.
        [{'dummy': u'', 'keyid': u'E273AC6458A2DF4F', 'expires': u'1505023118', 'subkeys': [[u'BF0F9E16247FA64F', u'esa']], 'length': u'4096', 'ownertrust': u'-', 'algo': u'1', 'fingerprint': u'06284050297955B8D37238B0E273AC6458A2DF4F', 'date': u'1378792718', 'trust': u'-', 'type': u'pub', 'uids': [u'Thomas Spycher 2 (This is an comment) <me@tspycher.com>']}]
        return x[0]['uids']

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
        x = self._gpg.list_keys()
        [{'dummy': u'', 'keyid': u'E273AC6458A2DF4F', 'expires': u'1505023118', 'subkeys': [[u'BF0F9E16247FA64F', u'esa']], 'length': u'4096', 'ownertrust': u'-', 'algo': u'1', 'fingerprint': u'06284050297955B8D37238B0E273AC6458A2DF4F', 'date': u'1378792718', 'trust': u'-', 'type': u'pub', 'uids': [u'Thomas Spycher 2 (This is an comment) <me@tspycher.com>']}]

        return x[0]['subkeys']

    def receiveKeyFromServer(self, keyid, server):
        return
