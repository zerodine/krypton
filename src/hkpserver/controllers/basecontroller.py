__author__ = 'thospy'

import logging
import tornado.web
from src.hkpserver.libs.gpgmongo import GpgModel


class BaseController(tornado.web.RequestHandler):
    """

    """

    config = None
    gpgModel = None
    logger = logging.getLogger("krypton")

    def initialize(self, config=None):
        """


        :param config:
        """
        self.config = config
        self.gpgModel = GpgModel(connectionUrl=self.config.mongoConnectionUrl)
        self.gpgModel.collection = self.config.mongoCollection