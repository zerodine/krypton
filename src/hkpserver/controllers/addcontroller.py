__author__ = 'thospy'

import tornado.web


class AddController(tornado.web.RequestHandler):

    _rawKey = None

    @staticmethod
    def routes(prefix = ""):
        return r"%s/add(.*)" % prefix, eval("AddController")

    def post(self, *args, **kwargs):
        self._rawKey = self.get_argument("keytext", default=None, strip=False)
        print self._rawKey
