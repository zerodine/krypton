__author__ = 'thospy'

import tornado.web

from src.hkpserver.gpgmongo import GpgModel


class AddController(tornado.web.RequestHandler):

    _rawKey = None

    gpgModel = GpgModel()

    @staticmethod
    def routes(prefix = ""):
        return r"%s/add(.*)" % prefix, eval("AddController")

    def post(self, *args, **kwargs):
        self._rawKey = self.get_argument("keytext", default=None, strip=False)

        self.gpgModel.connect(db="playground")
        self.gpgModel.uploadKey(self._rawKey)

