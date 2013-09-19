import hashlib

__author__ = 'thospy'

from src.hkpserver.libs.gpgmongo.mongobackend import MongoBackend
from src.hkpserver.libs.gpgjsonparser import JsonParser
from src.hkpserver.libs.gossip import GossipTask

class GpgModel(MongoBackend):
    """

    """

    collection = "publicKeys"
    queue = None
    gossipServers = None

    def listAllKeys(self):
        return self.runQuery(collection=self.collection,query=None,fields=["_id", "hash", "hash_algo"])

    def uploadKey(self, asciiArmoredKey):
        """

        :param asciiArmoredKey:
        :return:
        """
        j = JsonParser(asciiData=asciiArmoredKey)
        jsonAsciiArmoredKey = j.dump(raw=True)
        keyId = str(jsonAsciiArmoredKey["fingerprint"]).upper()

        h = hashlib.new('sha1')
        h.update(asciiArmoredKey)
        hexValue = h.hexdigest()
        data = {
            "keytext": asciiArmoredKey,
            #"inSync": False,
            "hash": hexValue,
            "hash_algo": "sha1",
        }

        # Upload the asciiArmored Key, but first check if key has been changed
        existing = self.exists(id=keyId, collection=self.collection, fields=["hash", "hash_algo"])
        if existing and hexValue == existing["hash"]:
            self.logger.info("Key %s is unchanged, no db operations are performed" % keyId)
            return True

        if existing:
            self.update(data=data, collection=self.collection, id=keyId)
        else:
            self.create(data=data, collection=self.collection, id=keyId)

        # Upload the json formatted Key
        if self.exists(id=keyId, collection="%sDetails" % self.collection):
            self.update(data=jsonAsciiArmoredKey, collection="%sDetails" % self.collection, id=keyId)
        else:
            self.create(data=jsonAsciiArmoredKey, collection="%sDetails" % self.collection, id=keyId)

        # Add Task to Queue for the Synchronisation
        server = self.gossipServers.getRandom()
        if server:
            self.logger.info("Created Synchronisation Task for Key %s to Server %s:%s" % (keyId, server["host"], server["port"]))
            self.queue.put(GossipTask(
                keyId=keyId,
                gossipServers=self.gossipServers,
                asciiArmoredKey=asciiArmoredKey
                )
            )
        else:
            self.logger.info("I do not syncronize the key %s due to no sks servers are configured" % keyId)
        return True

    def retrieveKey(self, keyId=None, hash=None):
        """

        :param keyId:
        :return:
        """
        x = None
        if keyId:
            x = self.read(id=keyId, collection=self.collection, fields=['keytext'])
        elif hash:
            y = self.runQuery(collection=self.collection, query={'hash': hash}, fields=['keytext'])
            if y and len(y):
                x = y[0]

        if x and "keytext" in x:
            return x["keytext"]
        return None

    def search(self, searchString, exact=False):
        """

        :param searchString:
        :param exact:
        :return:
        """
        hexIndicator = "0x"
        if str(searchString).lower().startswith(hexIndicator):
            return self.searchKeyId(searchString[len(hexIndicator):], exact)
        return self.searchKey(searchString, exact)

    def searchKeyId(self, keyId, exact=False):
        """

        :param keyId:
        :param exact:
        :return:
        """
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
        """

        :param searchString:
        :param exact:
        :return:
        """
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
        """


        :return:
        """
        if self.collection.lower().startswith("test"):
            self.removeCollection(self.collection)
            self.removeCollection("%sDetails" % self.collection)
            return True
        return False