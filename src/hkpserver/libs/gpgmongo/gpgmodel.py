import hashlib
from time import gmtime, strftime

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

    def numberOfKeys(self):
        """


        :return:
        """
        return self._collection(self.collection).count()

    def listAllKeys(self):
        """


        :return:
        """
        return self.runQuery(collection=self.collection, query=None, fields=["_id", "hash", "hash_algo"])

    def updateStatistics(self, update=False):
        """

        :param update:
        """
        if update:
            toUpdate = {"NewKeys": 0, "UpdatedKeys": 1}
        else:
            toUpdate = {"NewKeys": 1, "UpdatedKeys": 0}

        currentDate = strftime("%Y-%m-%d", gmtime())
        currentHour = strftime("%H", gmtime())
        h = hashlib.new('md5')
        h.update("Stats%s%s" % (currentDate, currentHour))
        id = h.hexdigest()

        data = {
            "$set": {
                "date": currentDate,
                "hour": currentHour
            },
            "$inc": toUpdate

        }

        self._collection("%sStatistics" % self.collection).update({"_id": id}, data, upsert=True)

    def uploadKey(self, asciiArmoredKey):
        """

        :param asciiArmoredKey:
        :return:
        """
        j = JsonParser(asciiData=asciiArmoredKey)
        jsonAsciiArmoredKey = j.dump(raw=True)
        keyId = str(jsonAsciiArmoredKey["fingerprint"]).upper()

        hash_algo = "md5"
        h = hashlib.new(hash_algo)
        h.update(asciiArmoredKey)
        hexValue = h.hexdigest()
        data = {
            "keytext": asciiArmoredKey,
            "hash": hexValue,
            "hash_algo": hash_algo,
        }
        jsonAsciiArmoredKey['hash'] = hexValue
        jsonAsciiArmoredKey['hash_algo'] = hash_algo


        # Upload the asciiArmored Key, but first check if key has been changed
        existing = self.exists(id=keyId, collection=self.collection, fields=["hash", "hash_algo"])
        if existing and hexValue == existing["hash"]:
            self.logger.info("Key %s is unchanged, no db operations are performed" % keyId)
            return True

        if existing:
            self.update(data=data, collection=self.collection, id=keyId)
            self.updateStatistics(update=True)
        else:
            self.create(data=data, collection=self.collection, id=keyId)
            self.updateStatistics(update=False)

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