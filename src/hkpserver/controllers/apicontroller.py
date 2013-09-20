from StringIO import StringIO
import base64
from Image import Image

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

        if not key:
            self.write_error(status_code=404)
            return

        if self.renderer == "json":
            self.write(self.jsonRender({"keytext": key}))
        else:
            self.set_header("Content-Type", "application/pgp-keys")
            self.write(key)

    def get_hget(self, data):
        self.write_error(status_code=405)

    def get_picture(self, data):
        picture = self.gpgModel.getKeyPrimaryPicture(data[0])
        if picture:
            self.set_header("Content-Type", "image/%s" % picture["image_format"])
            #img = Image.open(StringIO(base64.b64decode(picture['image_data'])))
            #self.write(img.show())
            self.write(base64.b64decode(picture['image_data']))
            return
        self.write_error(404)

    def get_index(self, data):
        search = self._parseSearch(data[0])
        if search["searchHex"]:
            key = self.gpgModel.searchKeyId(keyId=search["searchString"], exact=False)
        else:
            key = self.gpgModel.searchKey(searchString=search["searchString"], exact=False)

        if key:
            self.write(self.jsonRender(key))
            return

        self.write_error(404)
        return

    def get_vindex(self, data):
        self.get_index(data)

    def get_stats(self, data):
        self.write_error(status_code=405)

    def post_add(self, data):
        self.write_error(status_code=405)
