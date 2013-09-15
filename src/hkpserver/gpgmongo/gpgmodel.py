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
        if "keytext" in x:
            return x["keytext"]
        return None

    def search(self, searchString):
        hex = "0x"
        if str(searchString).lower().startswith(hex):
            return self.searchKeyId(searchString[len(hex):])
        return self.searchKey(searchString)

    def searchKeyId(self, keyId):
        print "Search for keyid: %s" % keyId
        query = {
            "$or": [
                {'fingerprint': {'$regex': keyId} },
                {'PublicSubkeyPacket.fingerprint': {'$regex': keyId}}
            ]
        }
        return self.runQuery(collection="%sDetails" % self.collection, query=query)

    def searchKey(self, searchString):
        print "Search for String: %s" % searchString
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