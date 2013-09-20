import base64
#from Image import Image

__author__ = 'thospy'

from basecontroller import BaseController


# noinspection PyUnusedLocal
class ApiController(BaseController):
    """

    """
    defaultRenderer = "json"
    renderer = None

    # noinspection PyUnusedLocal
    @staticmethod
    def routes(prefix="", applicationContext=None):
        """


        :type prefix: Config
        :param prefix:
        :return:
        """
        return r'(/api(.*)$)', ApiController, dict(applicationContext=applicationContext)

    def post(self, *args, **kwargs):
        """
        Handles POST requests

        :param args:
        :param kwargs:
        """
        self._performAction(args, kwargs)

    def get(self, *args, **kwargs):
        """
        Handles GET requests

        :param args:
        :param kwargs:
        """
        self._performAction(args, kwargs)

    # noinspection PyUnusedLocal
    def _performAction(self, *args, **kwargs):
        """
        Determine the action to perform

        :param args:
        :param kwargs:
        """
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
        """
        Serves: json and pgp-keys data

        http://localhost:8888/api/get/CF96B54D3E08F9F5 | .json
            Delivers the AsciiArmored Key as json document
        http://localhost:8888/api/get/CF96B54D3E08F9F5.gpg
            Downloads the key directly "(Content-Type: application/pgp-keys)

        http://localhost:8888/api/get/6f44e8f94bb2345a5ee764e09d2b6b3a.gpg/hash
        http://localhost:8888/api/get/6f44e8f94bb2345a5ee764e09d2b6b3a/hash
            The same as above, but searching for hash

        :param data:
        :return:
        """
        if not len(data) >= 1:
            self.write_error(status_code=405)
            return

        if "hash" in data:
            key = self.gpgModel.retrieveKey(hash=data[0])
        else:
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
        """
        Alias for get, but searching for hash instead of keyId

        :param data:
        """
        data.append("hash")
        self.get_get(data)

    def get_picture(self, data):
        """
        Serves: json and picture data

        http://localhost:8888/api/picture/CF96B54D3E08F9F5.png | .<WHATEVER>
            Shows the picture directly
        http://localhost:8888/api/picture/CF96B54D3E08F9F5 | .json
            Gets the picture base64 encoding in a json document

        :param data:
        :return:
        """
        picture = self.gpgModel.getKeyPrimaryPicture(data[0])
        if picture:
            if self.renderer == "json":
                self.write(self.jsonRender(picture))
                return
            self.set_header("Content-Type", "image/%s" % picture["image_format"])
            #img = Image.open(StringIO(base64.b64decode(picture['image_data'])))
            #self.write(img.show())
            self.write(base64.b64decode(picture['image_data']))
            return
        self.write_error(404)

    def get_index(self, data):
        """
        Serves: only json documents

        To Search for a keyid prefix it wit 0x to indicate a hex based search

        http://localhost:8888/api/index/0xCF96B54D3E08F9F5
            To search for a key id (fingerprint, subkey fingerprints etc)
        http://localhost:8888/api/index/spycher
            To search textual
        http://localhost:8888/api/index/0x3E08F9F5/exact
            Searches for an exact match of the key

        :param data:
        :return:
        """
        exact = False
        if "exact" in data:
            exact = True

        search = self._parseSearch(data[0])
        if search["searchHex"]:
            key = self.gpgModel.searchKeyId(keyId=search["searchString"], exact=exact)
        else:
            key = self.gpgModel.searchKey(searchString=search["searchString"], exact=exact)

        if key:
            self.write(self.jsonRender(key))
            return

        self.write_error(404)
        return

    def get_vindex(self, data):
        """
        Alias for index

        :param data:
        """
        self.get_index(data)

    def get_search(self, data):
        """
        Alias for index

        :param data:
        """
        self.get_index(data)

    def get_stats(self, data):
        """
        Not Supported

        :param data:
        """
        self.write_error(status_code=405)

    def post_add(self, data):
        """
        Not Supported

        :param data:
        """
        self.write_error(status_code=405)