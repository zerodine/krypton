import hashlib
from time import gmtime, strftime

from krypton.hkpserver.libs.gpgmongo.mongobackend import MongoBackend
from krypton.hkpserver.libs.gpgjsonparser import JsonParser
from krypton.hkpserver.libs.gossip import GossipTask

class GpgModel(MongoBackend):
    """

    """

    collection = "publicKeys"
    queue = None
    gossipServers = None

    def getKeyPrimaryPicture(self, keyId):
        """

        :param keyId:
        :return:
        """
        x = self.runQuery(
            collection="%sDetails" % self.collection,
            query={'fingerprint': {'$regex': keyId.upper()}},
            fields=["UserAttributePacket.image_data", "UserAttributePacket.image_format"]
        )

        if x and "UserAttributePacket" in x[0]:
            return x[0]['UserAttributePacket'][0]
        return None

    def getKeyPrimaryUid(self, keyId):
        """

        :param keyId:
        :return:
        """
        x = self.runQuery(collection="%sDetails" % self.collection, query={'fingerprint': {'$regex': keyId}}, fields=["primary_UserIDPacket"])

        if x and "primary_UserIDPacket" in x[0]:
            return x[0]["primary_UserIDPacket"]
        return None

    def getStatistics(self, onlyDay=True):
        """

        :param onlyDay:
        :return:
        """
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
        if not externalUpload and self.queue:
            for fk in jsonAsciiArmoredKey["foreignKeys"]:
                self.queue.put(GossipTask(
                    task=GossipTask.TASK_SEARCHKEY,
                    keyId=fk,
                    gossipServers=None,
                    asciiArmoredKey=None,
                    gpgModel=self
                    )
                )

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
        server = None
        if self.queue and self.gossipServers:
            server = self.gossipServers.getRandom()
        if server:
            self.logger.info("Created Synchronisation Task for Key %s to Server %s:%s" % (keyId, server["host"], server["port"]))
            self.queue.put(GossipTask(
                task=GossipTask.TASK_DISTRIBUTEKEY,
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
            keyId = keyId.upper()
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

    def searchKeyId(self, keyId, exact=False, fields=None):
        """

        :param keyId:
        :param exact:
        :return:
        """
        keyId = keyId.upper()

        if exact:
            search = keyId
        else:
            search = {'$regex': keyId}
        query = {
            "$or": [
                {'fingerprint': search},
                {'fingerprint_v3': search},
                {'key_id_64': search},
                {'key_id_32': search},
                {'key_id': search},
                {'PublicSubkeyPacket.fingerprint': search},
                {'PublicSubkeyPacket.key_id': search},
                {'PublicSubkeyPacket.fingerprint_v3': search},
                {'PublicSubkeyPacket.key_id_64': search},
                {'PublicSubkeyPacket.key_id_32': search},
            ]
        }
        data = self.runQuery(collection="%sDetails" % self.collection, query=query, fields=fields)
        if not data:
            self.tryImportRemoteKey()
            data = self.runQuery(collection="%sDetails" % self.collection, query=query, fields=fields)
        return data

    def searchKey(self, searchString, exact=False, fields=None):
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
        return self.runQuery(collection="%sDetails" % self.collection, query=query, fields=fields)

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