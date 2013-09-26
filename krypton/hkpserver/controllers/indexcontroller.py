__author__ = 'thospy'

from basecontroller import BaseController
import tornado.template


class IndexController(BaseController):
    """

    """

    # noinspection PyUnusedLocal
    @staticmethod
    def routes(prefix="", applicationContext=None):
        """


        :type prefix: Config
        :param prefix:
        :return:
        """
        #return r'/(.*).html', IndexController, dict(applicationContext=applicationContext)
        return r'(/$|/(.*).html)', IndexController, dict(applicationContext=applicationContext)

    def get(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        """
        loader = tornado.template.Loader(self.buildPath("hkpserver/views"))
        self.write(loader.load("index.template.html").generate(
            current="Home"
        ))