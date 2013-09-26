__author__ = 'thospy'

import logging
import tornado.web
import json
import os
from krypton.hkpserver.libs.gpgmongo import GpgModel

class BaseController(tornado.web.RequestHandler):
    """

    """

    applicationContext = None
    config = None
    gpgModel = None
    logger = logging.getLogger("krypton")

    def prepare(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Server", "%s/%s" % (self.applicationContext.applicationName, self.applicationContext.version))

    def initialize(self, applicationContext=None):
        """

        :param applicationContext:
        """
        self.applicationContext = applicationContext
        self.config = self.applicationContext.config
        self.gpgModel = GpgModel(connectionUrl=self.config.mongoConnectionUrl)
        self.gpgModel.queue = self.applicationContext.queue
        self.gpgModel.gossipServers = self.applicationContext.gossipServers
        self.gpgModel.collection = self.config.mongoCollection

    def buildPath(self, relativePath):
        return os.path.join(self.applicationContext.basePath, relativePath)

    def _parseSearch(self, searchString):
        """

        :param searchString:
        """
        hexIndicator = "0x"
        s = str(searchString)
        searchHex = False
        if s.lower().startswith(hexIndicator):
            searchHex = True
            s = s[len(hexIndicator):]

        searchString = s
        return {"searchHex": searchHex, "searchString": searchString}

    def strip0x(self, x):
        if str(x).lower().startswith("0x"):
            return str(x[2:]).upper()
        return x

    def jsonRender(self, data):
        base = {
            "count": len(data),
            "results": data
        }
        self.set_header(name="Content-Type", value="application/json")
        return json.dumps(base, indent=2)
