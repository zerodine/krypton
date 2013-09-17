__author__ = 'thospy'

from mongobackend import MongoBackend
from src.hkpserver.gpgjsonparser import JsonParser

class GpgModel(MongoBackend):

    collection = "publicKeys"

    def uploadKey(self, asciiArmoredKey):
        j = JsonParser(asciiData=asciiArmoredKey)
        jsonAsciiArmoredKey = j.dump(raw=True)
        keyId = jsonAsciiArmoredKey["fingerprint"]

        data = {
            "keytext": asciiArmoredKey
        }

        # Upload the json formated Key
        if self.exists(id=keyId, collection="%sDetails" % self.collection):
            self.update(data=jsonAsciiArmoredKey, collection="%sDetails" % self.collection, id=keyId)
        else:
            self.create(data=jsonAsciiArmoredKey, collection="%sDetails" % self.collection, id=keyId)

        # Upload the asciiArmored Key
        if self.exists(id=keyId, collection=self.collection):
            return self.update(data=data, collection=self.collection, id=keyId)
        return self.create(data=data, collection=self.collection, id=keyId)

    def retrieveKey(self, keyId):
        x = self.read(id=keyId, collection=self.collection, fields=['keytext'])
        print x
        if x and "keytext" in x:
            return x["keytext"]
        return None

    def search(self, searchString, exact = False):
        hex = "0x"
        if str(searchString).lower().startswith(hex):
            return self.searchKeyId(searchString[len(hex):], exact)
        return self.searchKey(searchString, exact)

    def searchKeyId(self, keyId, exact=False):
        if exact:
            search = keyId
        else:
            search = {'$regex': keyId}
        query = {
            "$or": [
                {'fingerprint': search},
                {'key_id': search},
                {'PublicSubkeyPacket.fingerprint': search},
                {'PublicSubkeyPacket.key_id': search}
            ]
        }
        return self.runQuery(collection="%sDetails" % self.collection, query=query)

    def searchKey(self, searchString, exact=False):
        # in keyword search we simply ignore the exact parameter
        if exact:
            pass

        query = {
            "$or": [
                {'UserIDPacket.user': {'$regex': searchString}}
            ]
        }
        return self.runQuery(collection="%sDetails" % self.collection, query=query)


    def cleanTestCollections(self):
        if self.collection.lower().startswith("test"):
            self.removeCollection(self.collection)
            self.removeCollection("%sDetails" % self.collection)
            return True
        return False