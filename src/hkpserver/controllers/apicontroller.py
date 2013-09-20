__author__ = 'thospy'

from basecontroller import BaseController


class ApiController(BaseController):
    """

    """
    defaultRenderer = "json"
    renderer = None

    @staticmethod
    def routes(prefix="", applicationContext=None):
        """


        :type prefix: Config
        :param prefix:
        :param config:
        :return:
        """
        return r'(/api(.*)$)', ApiController, dict(applicationContext=applicationContext)

    def post(self, *args, **kwargs):
        self._performAction(args, kwargs)


    def get(self, *args, **kwargs):
        self._performAction(args, kwargs)

    def _performAction(self, *args, **kwargs):
        x = str(args[0][1])[1:].split("/")
        xx = x[-1:][0].split(".")
        x[-1:] = [xx[0]]
        if len(xx) >= 2:
            self.renderer = xx[1]
        else:
            self.renderer = self.defaultRenderer

        action = str("%s_%s" % (self.request.method, x[0])).lower()
        try:
            self.gpgModel.connect(db=self.config.mongoDatabase)
            getattr(self, action)(x[1:])
        except AttributeError:
            self.write_error(status_code=404)

    def get_get(self, data):
        if not len(data) >= 1:
            self.write_error(status_code=405)
            return

        key = self.gpgModel.retrieveKey(keyId=data[0])

        if self.renderer == "json":
            self.write(self.jsonRender({"keytext": key}))
        else:
            self.set_header("Content-Type", "application/pgp-keys")
            self.write(key)

    def get_hget(self, data):
        self.write_error(status_code=405)

    def get_index(self, data):
        self.write_error(status_code=405)

    def get_vindex(self, data):
        self.write_error(status_code=405)

    def get_stats(self, data):
        self.write_error(status_code=405)

    def post_add(self, data):
        self.write_error(status_code=405)
