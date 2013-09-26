import logging
from tornado import httpclient
from tornado.httputil import HTTPHeaders
import re
import urllib

__author__ = 'thospy'


class GossipTask(object):

    name = "Gossip Syncronisation Task"
    keyId = None
    gossipServers = None
    asciiArmoredKey = None
    logger = logging.getLogger("krypton.gossip")
    numberOfTries = 0
    maxNumberOfTries = 5
    givingUp = False
    gpgModel = None

    TASK_DISTRIBUTEKEY = 1
    TASK_SEARCHKEY = 2

    task = None

    def __init__(self, task, keyId=None, gossipServers=None, asciiArmoredKey=None, gpgModel=None):
        self.task = task
        self.keyId = keyId
        self.asciiArmoredKey = asciiArmoredKey
        self.gossipServers = gossipServers
        self.gpgModel = gpgModel

    def doWork(self):
        if self.task == self.TASK_DISTRIBUTEKEY:
            x = self._doTaskDistributeKey()
        elif self.task == self.TASK_SEARCHKEY:
            x = self._doTaskSearchKey()

        if x:
            return x
        return self._handleFail()

    def _doTaskSearchKey(self):
        self.logger.info("Trying to get key %s" % self.keyId)
        url = "http://pool.sks-keyservers.net:11371/pks/lookup?op=get&search=0x%s&options=mr" % self.keyId
        http_client = httpclient.HTTPClient()
        http_request = httpclient.HTTPRequest(url=url)
        http_request.headers = (HTTPHeaders({"content-type": "application/pgp-keys"}))
        try:
            response = http_client.fetch(http_request)
        except httpclient.HTTPError, e:
            self.logger.warning("Problem while getting key %s (%s)" % (self.keyId, str(e)))
            return False

        key = re.search("-----BEGIN PGP PUBLIC KEY BLOCK.*END PGP PUBLIC KEY BLOCK-----",
                        response.body, re.I | re.S | re.M).group(0)
        if key:
            if self.gpgModel.uploadKey(asciiArmoredKey=key, force=True, externalUpload=True):
                self.logger.info("Successfully imported key %s" % self.keyId)
            else:
                self.logger.info("Error while importing key %s. Please see the logs" % self.keyId)
        return False

    def _doTaskDistributeKey(self):
        server = self.gossipServers.getRandom()
        http_client = httpclient.HTTPClient()
        http_request = httpclient.HTTPRequest(url="http://%s:%i/pks/add" % (server["host"], int(server["port"])))
        post_data = {'keytext': self.asciiArmoredKey}
        http_request.method = "POST"
        http_request.body = urllib.urlencode(post_data)
        try:
            response = http_client.fetch(http_request)
            if int(response.code) != 200:
                return False
        except httpclient.HTTPError, e:
            self.logger.warning("Problem while sending key %s to other keyserver: %s" % (self.keyId, str(e)))
            return False
        return True

    def _handleFail(self):
        self.numberOfTries += 1
        if self.numberOfTries >= self.maxNumberOfTries:
            self.givingUp = True
        return False