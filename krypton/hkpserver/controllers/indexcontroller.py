__author__ = "Thomas Spycher, Philipp Spinnler"
__copyright__ = "Copyright 2013, Zerodine GmbH (zerodine.com) "
__credits__ = ["Thomas Spycher", "Philipp Spinnler"]
__license__ = "Apache-2.0"
__maintainer__ = "Thomas Spycher"
__email__ = "me@tspycher.com"
__status__ = "Development"

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