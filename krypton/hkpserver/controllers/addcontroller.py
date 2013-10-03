__author__ = "Thomas Spycher, Philipp Spinnler"
__copyright__ = "Copyright 2013, Zerodine GmbH (zerodine.com) "
__credits__ = ["Thomas Spycher", "Philipp Spinnler"]
__license__ = "Apache-2.0"
__maintainer__ = "Thomas Spycher"
__email__ = "me@tspycher.com"
__status__ = "Development"

from basecontroller import BaseController


class AddController(BaseController):
    """

    """

    _rawKey = None

    @staticmethod
    def routes(prefix="", applicationContext=None):
        """

        :param prefix:
        :param applicationContext:
        :return:
        """
        return r"%s/add(.*)" % prefix, AddController, dict(applicationContext=applicationContext)

    def post(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        """
        self._rawKey = self.get_argument("keytext", default=None, strip=False)
        self.gpgModel.connect(db=self.config.mongoDatabase)
        self.gpgModel.uploadKey(self._rawKey)
