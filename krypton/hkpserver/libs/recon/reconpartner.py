import logging
import urllib
from tornado import httpclient
import tornado
from tornado.httputil import HTTPHeaders

__author__ = "Thomas Spycher, Philipp Spinnler"
__copyright__ = "Copyright 2013, Zerodine GmbH (zerodine.com) "
__credits__ = ["Thomas Spycher", "Philipp Spinnler"]
__license__ = "Apache-2.0"
__version__ = "0.0.1"
__maintainer__ = "Thomas Spycher"
__email__ = "me@tspycher.com"
__status__ = "Development"


class ReconPartner(object):

    _url = None
    _hashes = None
    _model = None
    logger = logging.getLogger("krypton.reconPartner")


    def __init__(self, url, hashes=None, model = None):
        self._url = url
        self._hashes = hashes
        self._model = model

    def url(self):
        return self._url

    def hashes(self):
        """


        :return:
        """
        self._hashes = None
        if self._model:
            self._hashes = self._model.getHashes()
        else:
            x = self._httpRequest(url="%s/recon" % self._url)
            if x:
                self._hashes = x["results"]

        if self._hashes is not None:
            return set(self._hashes)
        return None

    def getKey(self, hash=None, keyId=None):
        """

        :param hash:
        :param keyId:
        :return:
        """
        if self._model:
            if hash:
                return self._model.retrieveKey(hash=hash)
            else:
                return self._model.retrieveKey(keyId=keyId)

        if hash:
            url = "%s/lookup?op=hget&search=%s&options=mr&exact=on" % (self._url, hash)
        else:
            url = "%s/lookup?op=get&search=0x%s&options=mr&exact=on" % (self._url, keyId)
        return self._httpRequest(url=url, jsonResponse=False)

    def storeKey(self, asciiArmoredKey):
        """

        :param asciiArmoredKey:
        :return:
        """
        if self._model:
            return self._model.uploadKey(asciiArmoredKey=asciiArmoredKey, force=True, externalUpload=True)

        return self._httpRequest(url="%s/add" % self._url, data={'keytext': asciiArmoredKey})

    def _httpRequest(self, url, data=None, jsonResponse=True):
        """

        :param url:
        :param data:
        :param jsonResponse:
        :return:
        """
        http_client = httpclient.HTTPClient()
        http_request = httpclient.HTTPRequest(url=url)

        if not jsonResponse and not data:
            http_request.headers = (HTTPHeaders({"content-type": "application/pgp-keys"}))

        if data:
            http_request.method = "POST"
            http_request.body = urllib.urlencode(data)

        # Run the HTTP Request
        try:
            response = http_client.fetch(http_request)
        except httpclient.HTTPError, e:
            self.logger.warning("Problem while getting data from %s (%s)" % (url, str(e)))
            return False

        # Handling of POST responses
        if data:
            if int(response.code) == 200:
                return True
            self.logger.warning("Problem while posting data to %s" % (url))
            return False

        if not jsonResponse:
            return response.body

        # Handling of GET responses, expecting JSON data
        try:
            jsonData = tornado.escape.json_decode(response.body)
        except ValueError:
            self.logger.warning('No Json Data received in requests body for receiving data from %s' % url)
            return False

        if not jsonData or not "results" in jsonData:
            self.logger.warning("No valid Result received")
            return False

        return jsonData

    def __repr__(self):
        if self._url:
            return u"%s" % self._url
        return u"Model: %s" % self._model
