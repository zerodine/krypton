__author__ = 'thospy'

import tornado.web


class LookupController(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        op = self.get_argument("op", default="index", strip=False)
        getattr(self, "op_%s" % str(op).lower())(**kwargs)

    def op_index(self):
        self.write("Index")

    def op_vindex(self):
        self.write("Verbose Index")

    def op_get(self):
        self.write("Get")