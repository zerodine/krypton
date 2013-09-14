__author__ = 'thospy'

import pymongo
import datetime


class MongoBackend(object):

    _c = None
    db = None

    connected = False
    connectionUrl = ""

    def __init__(self, connectionUrl):
        self.connectionUrl = connectionUrl

    def connect(self, db):
        if not self.connected:
            self._c = pymongo.MongoClient(self.connectionUrl)
            self.db = self._c[db]
            self.connected = True

    def exists(self, collection, id):
        return self.db[collection].find_one({"_id": id}, fields=[])

    def create(self, collection, data, id = None):
        if id is not None:
            data["_id"] = id
        return self.db[collection].insert(data)

    def update(self, collection, data, id):
        return self.db[collection].update({"_id": id}, data)

    def read(self, collection, id, fields=None):
        return self.db[collection].find_one({"_id": id}, fields=fields)

    def delete(self, collection, id):
        pass

    def removeCollection(self, collection):
        return self.db.drop_collection(collection)