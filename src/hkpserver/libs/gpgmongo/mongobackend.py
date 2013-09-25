__author__ = 'thospy'

import pymongo
import logging


class MongoBackend(object):
    """

    """

    _c = None
    db = None

    connected = False
    connectionUrl = ""
    logger = logging.getLogger("krypton.mongo")

    def __init__(self, connectionUrl):
        """

        :param connectionUrl:
        """
        self.connectionUrl = connectionUrl

    def connect(self, db):
        """

        :param db:
        """
        if not self.connected:
            self._c = pymongo.MongoClient(self.connectionUrl)
            self.db = self._c[db]
            self.connected = True

    def _collection(self, collection):
        """

        :param collection:
        :return:
        """
        x = self.db[collection]
        x.DESCENDING = 0
        x.ASCENDING = 0
        return x

    def exists(self, collection, id, fields=[]):
        """

        :param collection:
        :param id:
        :return:
        """
        self.logger.debug("Checking for existence of id %s in collection %s" % (id, collection))
        return self._collection(collection).find_one({"_id": id}, fields=fields)

    def create(self, collection, data, id=None):
        """

        :param collection:
        :param data:
        :param id:
        :return:
        """
        self.logger.debug("Create Record in collection %s" % collection)

        if id is not None:
            data["_id"] = id
        try:
            return self._collection(collection).insert(data)
        except OverflowError:
            print data
            raise

    def update(self, collection, data, id):
        """

        :param collection:
        :param data:
        :param id:
        :return:
        """
        self.logger.debug("Updating Record with id %s in collection %s" % (id, collection))
        return self._collection(collection).update({"_id": id}, data)

    def read(self, collection, id, fields=None):
        """

        :param collection:
        :param id:
        :param fields:
        :return:
        """
        self.logger.debug("Read record with id %s in collection %s" % (id, collection))
        return self._collection(collection).find_one({"_id": {"$regex": id}}, fields=fields)

    def delete(self, collection, id):
        """

        :param collection:
        :param idValue:
        """
        pass

    def runQuery(self, collection, query=None, fields=None):
        """

        :param collection:
        :param query:
        :return:
        """
        self.logger.debug("Run Query: %s in collection %s" % (str(query), collection))
        data = []
        for x in self._collection(collection).find(spec=query, fields=fields):
            data.append(x)
        return data

    def removeCollection(self, collection):
        """

        :param collection:
        :return:
        """
        return self.db.drop_collection(collection)