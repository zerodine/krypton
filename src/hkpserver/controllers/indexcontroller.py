__author__ = 'thospy'

from basecontroller import BaseController
import tornado.template


class IndexController(BaseController):
    """

    """

    @staticmethod
    def routes(prefix="", config=None):
        """


        :type prefix: Config
        :param prefix:
        :param config:
        :return:
        """
        return r'/(.*).html', IndexController, dict(config=config)

    def get(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        """
        loader = tornado.template.Loader("src/hkpserver/views")
        self.write(loader.load("index.template.html").generate(
            current="Home"
        ))