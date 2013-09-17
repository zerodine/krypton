__author__ = 'thospy'

import logging
import tornado.web
from src.hkpserver.libs.gpgmongo import GpgModel


class BaseController(tornado.web.RequestHandler):
    """

    """

    applicationContext = None
    config = None
    gpgModel = None
    logger = logging.getLogger("krypton")

    def initialize(self, applicationContext=None):
        """


        :param config:
        """
        self.applicationContext = applicationContext
        self.config = self.applicationContext.config
        self.gpgModel = GpgModel(connectionUrl=self.config.mongoConnectionUrl)
        self.gpgModel.queue = self.applicationContext.queue
        self.gpgModel.gossipServers = self.applicationContext.gossipServers
        self.gpgModel.collection = self.config.mongoCollection