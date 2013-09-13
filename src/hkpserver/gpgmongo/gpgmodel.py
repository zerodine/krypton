__author__ = 'thospy'

from mongobackend import MongoBackend
from src.hkpserver.gpgjsonparser import JsonParser

class GpgModel(MongoBackend):

    collection = "publicKeys"

    def uploadKey(self, asciiArmoredKey):
        j = JsonParser(asciiData=asciiArmoredKey)
        keyId = j.dump(raw=True)["fingerprint"]

        data = {
            "keytext": asciiArmoredKey
        }

        if self.exists(id=keyId, collection=self.collection):
            return self.update(data=data, collection=self.collection, id=keyId)
        return self.create(data=data, collection=self.collection, id=keyId)

    def retrieveKey(self, keyId):
        x = self.read(id=keyId, collection=self.collection,fields=['keytext'])
        if "keytext" in x:
            return x["keytext"]
        return None

    def searchKeyId(self, keyId):
        pass

    def searchKey(self, searchString):
        pass