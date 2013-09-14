__author__ = 'thospy'

import tornado.web
from src.hkpserver.gpgmongo import GpgModel


class BaseController(tornado.web.RequestHandler):
    config = None
    gpgModel = None


    def initialize(self, config = None):
        self.config = config
        self.gpgModel = GpgModel(connectionUrl=self.config.mongoConnectionUrl)
        self.gpgModel.collection = self.config.mongoCollection