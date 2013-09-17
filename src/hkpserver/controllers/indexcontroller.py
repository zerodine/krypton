__author__ = 'thospy'

from basecontroller import BaseController
import tornado.template

class IndexController(BaseController):

    @staticmethod
    def routes(prefix = "", config = None):
        #return (r"%s/lookup(.*)" % prefix, "LookupController", dict(config=config))
        return (r"/(.*).html", IndexController, dict(config=config) )

    def get(self, *args, **kwargs):
        loader = tornado.template.Loader("src/hkpserver/views")
        self.write(loader.load("index.template.html").generate(
            current="Home"
        ))