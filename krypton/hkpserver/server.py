__author__ = "Thomas Spycher, Philipp Spinnler"
__copyright__ = "Copyright 2013, Zerodine GmbH (zerodine.com) "
__credits__ = ["Thomas Spycher", "Philipp Spinnler"]
__license__ = "Apache-2.0"
__maintainer__ = "Thomas Spycher"
__email__ = "me@tspycher.com"
__status__ = "Development"
import sys, os
import threading
import logging

try:
    import tornado.ioloop
    import tornado.web
except ImportError:
    sys.stderr.write("Looks like you have tornado not installed. (apt-get install python-tornado)")
    sys.exit(1)

from krypton.hkpserver.libs.gossip import Gossiping
from controllers import *


hkpplus = False
try:
    from krypton.hkpplus.controllers.apicontroller import ApiController
    hkpplus = True
except ImportError as e:
    if not "apicontroller" in str(e).lower():
        raise e


class Server(object):
    """

    """

    controllers = ['Lookup', 'Add', 'Index', 'Recon']
    routes = []
    routePrefix = None
    applicationContext = None
    logger = logging.getLogger("krypton")
    gossiping = None

    def __init__(self, routePrefix="/pks", applicationContext=None):
        """

        :param routePrefix:
        :param config:
        """
        self.routePrefix = routePrefix
        self.applicationContext = applicationContext
        self.gossiping = Gossiping(applicationContext=self.applicationContext)

        if hkpplus:
            self.controllers.append('Api')
            logging.getLogger("krypton.bootstrap").info("Kryptonplus IS available, running enterprise version")
        else:
            logging.getLogger("krypton.bootstrap").info("Kryptonplus is NOT available, running community version")

    def _buildRoutes(self):
        """


        """
        print os.path.join(self.applicationContext.basePath, "../doc/html")
        staticPre = [
            (r'/doc/(.*)', tornado.web.StaticFileHandler,
             {'path': os.path.join(self.applicationContext.basePath, "doc/html")})
        ]
        staticPost = [
            (r'/(.*)', tornado.web.StaticFileHandler,
             {'path':  os.path.join(self.applicationContext.basePath, "hkpserver/wwwroot")})
        ]
        for s in staticPre:
            self.routes.append(s)
        for c in self.controllers:
            self.routes.append(eval("%sController" % c).routes(
                prefix=self.routePrefix,
                applicationContext=self.applicationContext))
        for s in staticPost:
            self.routes.append(s)

    def start(self, port=11371, as_thread=False):
        """

        :param port:
        :param as_thread:
        :return:
        """
        self._buildRoutes()
        application = tornado.web.Application(self.routes)
        application.listen(port)
        self.logger.info("Server will liston on Port: %i" % port)
        self.gossiping.start()

        if as_thread:
            threading.Thread(target=self._start).start()
            return True
        else:
            self._start()

    def _start(self):
        """


        """
        tornado.ioloop.IOLoop.instance().start()

    def stop(self):
        """


        """
        tornado.ioloop.IOLoop.instance().stop()
        self.gossiping.stop()