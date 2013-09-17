__author__ = 'thospy'

import sys, threading
import logging

try:
    import tornado.ioloop
    import tornado.web
except ImportError:
    sys.stderr.write("Looks like you have tornado not installed. (apt-get install python-tornado)")
    sys.exit(1)

from controllers import *


class Server(object):
    controllers = ['Lookup', 'Add', 'Index']
    routes = []
    routePrefix = None
    config = None
    logger = logging.getLogger("krypton")

    def __init__(self, routePrefix="/pks", config=None):
        self.routePrefix = routePrefix
        self.config = config

    def _buildRoutes(self):
        static = [
            (r'/(.*)', tornado.web.StaticFileHandler, {'path': "src/hkpserver/wwwroot"})
        ]
        for c in self.controllers:
            self.routes.append(eval("%sController" % c).routes(self.routePrefix, config=self.config))
        for s in static:
            self.routes.append(s)

    def start(self, port=11371, as_thread=False):
        self._buildRoutes()
        application = tornado.web.Application(self.routes)
        application.listen(port)
        self.logger.info("Server will liston on Port: %i" % port)
        if as_thread:
            threading.Thread(target=self._start).start()
            return True
        else:
            self._start()

    def _start(self):
        tornado.ioloop.IOLoop.instance().start()

    def stop(self):
        tornado.ioloop.IOLoop.instance().stop()