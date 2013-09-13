__author__ = 'thospy'

from basecontroller import BaseController

class AddController(BaseController):

    _rawKey = None

    @staticmethod
    def routes(prefix = "", config = None):
        #return r"%s/add(.*)" % prefix, eval("AddController")
        return (r"%s/add(.*)" % prefix, AddController, dict(config=config))


    def post(self, *args, **kwargs):
        self._rawKey = self.get_argument("keytext", default=None, strip=False)

        self.gpgModel.connect(db=self.config.mongoDatabase)
        self.gpgModel.uploadKey(self._rawKey)

