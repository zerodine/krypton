__author__ = 'thospy'

import logging
import tornado.web
from src.hkpserver.gpgmongo import GpgModel


class BaseController(tornado.web.RequestHandler):
    config = None
    gpgModel = None
    logger = logging.getLogger("krypton")

    def initialize(self, config = None):
        self.config = config
        self.gpgModel = GpgModel(connectionUrl=self.config.mongoConnectionUrl)
        self.gpgModel.collection = self.config.mongoCollection