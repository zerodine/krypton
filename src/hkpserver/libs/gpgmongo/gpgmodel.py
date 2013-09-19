import hashlib
from time import gmtime, strftime
from tornado import httpclient
from tornado.httputil import HTTPHeaders
import re

from src.hkpserver.libs.gpgmongo.mongobackend import MongoBackend
from src.hkpserver.libs.gpgjsonparser import JsonParser
from src.hkpserver.libs.gossip import GossipTask

class GpgModel(MongoBackend):
    """

    """

    collection = "publicKeys"
    queue = None
    gossipServers = None

    def getStatistics(self, onlyDay=True):
        keys = ["date"]
        if not onlyDay:
            keys.append("hour")

        rows = keys + ["NewKeys", "UpdatedKeys"]
        return self._collection("%sStatistics" % self.collection).group(
            key=keys,
            condition=rows,
            initial={"totalNewKeys": 0, "totalUpdatedKeys": 0},
            reduce="""
            function ( curr, result ) {
                result.totalNewKeys += curr.NewKeys;
                result.totalUpdatedKeys += curr.UpdatedKeys;
            }"""
        )


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

    def updateStatistics(self, update=False, overwriteDate=None):
        """


        :param overwriteDate: this is mainly for unittests
        :param update:
        """
        if overwriteDate:
            now = gmtime(overwriteDate)
        else:
            now = gmtime()

        if update:
            toUpdate = {"NewKeys": 0, "UpdatedKeys": 1}
        else:
            toUpdate = {"NewKeys": 1, "UpdatedKeys": 0}

        currentDate = strftime("%Y-%m-%d", now)
        currentHour = strftime("%H", now)
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

    def uploadKey(self, asciiArmoredKey, force=True, externalUpload=False):
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

        # getting missing keys
        if not externalUpload:
            for fk in jsonAsciiArmoredKey["foreignKeys"]:
                self.tryImportRemoteKey(fk)

        # Upload the asciiArmored Key, but first check if key has been changed
        existing = self.exists(id=keyId, collection=self.collection, fields=["hash", "hash_algo"])
        if existing and hexValue == existing["hash"] and not force:
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
        data = self.runQuery(collection="%sDetails" % self.collection, query=query)
        if not data:
            self.tryImportRemoteKey()
            data = self.runQuery(collection="%sDetails" % self.collection, query=query)
        return data

    def tryImportRemoteKey(self, keyId):
        self.logger.info("Trying to get key %s" % keyId)
        url = "http://pool.sks-keyservers.net:11371/pks/lookup?op=get&search=0x%s&options=mr" % keyId
        http_client = httpclient.HTTPClient()
        http_request = httpclient.HTTPRequest(url=url)
        http_request.headers = (HTTPHeaders({"content-type": "application/pgp-keys"}))
        response = None
        try:
            response = http_client.fetch(http_request)
        except httpclient.HTTPError, e:
            print e
            return False

        key = re.search("-----BEGIN PGP PUBLIC KEY BLOCK.*END PGP PUBLIC KEY BLOCK-----", response.body, re.I | re.S | re.M).group(0)
        if key:
            return self.uploadKey(asciiArmoredKey=key, force=True, externalUpload=True)
        return False

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
            self.removeCollection("%sStatistics" % self.collection)
            return True
        return False