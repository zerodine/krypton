__author__ = 'thospy'

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
