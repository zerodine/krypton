__author__ = 'thospy'

import sys
import threading
import logging

try:
    import tornado.ioloop
    import tornado.web
except ImportError:
    sys.stderr.write("Looks like you have tornado not installed. (apt-get install python-tornado)")
    sys.exit(1)

from src.hkpserver.libs.gossip import Gossiping
from controllers import *

try:
    from src.hkpplus.controllers import *
except ImportError, e:
    pass


class Server(object):
    """

    """

    controllers = ['Lookup', 'Add', 'Index']
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

        try:
            # noinspection PyUnresolvedReferences
            ApiController
            self.controllers.append('Api')
            logging.getLogger("krypton.bootstrap").info("Kryptonplus IS available, running enterprise version")
        except NameError, e:
            logging.getLogger("krypton.bootstrap").info("Kryptonplus is NOT available, running community version")

    def _buildRoutes(self):
        """


        """
        static = [
            (r'/(.*)', tornado.web.StaticFileHandler, {'path': "src/hkpserver/wwwroot"})
        ]
        for c in self.controllers:
            self.routes.append(eval("%sController" % c).routes(
                prefix=self.routePrefix,
                applicationContext=self.applicationContext))
        for s in static:
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