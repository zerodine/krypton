__author__ = 'thospy'

import sys, threading

try:
    import tornado.ioloop
    import tornado.web
except ImportError:
    sys.stderr.write("Looks like you have tornado not installed. (apt-get install python-tornado)")
    sys.exit(1)

from controllers import *


class Server(object):
    controllers = ['Lookup', 'Add']
    routes = []
    routePrefix = None
    config = None

    def __init__(self, routePrefix = "/pks", config = None):
        self.routePrefix = routePrefix
        self.config = config

    def _buildRoutes(self):
        for c in self.controllers:
            #self.routes.append((r"/%s/(.*)" % c.lower(), eval("%sController" % c)))
            #self.routes.append((r"/%s(.*)" % c.lower(), eval("%sController" % c)))
            self.routes.append(eval("%sController" % c).routes(self.routePrefix, config=self.config))

    def start(self, port = 11371, as_thread = False):
        self._buildRoutes()
        application = tornado.web.Application(self.routes)
        application.listen(port)

        if as_thread:
            threading.Thread(target=self._start).start()
            return True
        else:
            self._start()

    def _start(self):
        tornado.ioloop.IOLoop.instance().start()

    def stop(self):
        tornado.ioloop.IOLoop.instance().stop()