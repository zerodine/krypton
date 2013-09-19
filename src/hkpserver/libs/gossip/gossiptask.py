import logging
from tornado import httpclient
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

    def __init__(self, keyId, gossipServers, asciiArmoredKey, ):
        self.keyId = keyId
        self.asciiArmoredKey = asciiArmoredKey
        self.gossipServers = gossipServers

    def doWork(self):
        server = self.gossipServers.getRandom()
        http_client = httpclient.HTTPClient()
        http_request = httpclient.HTTPRequest(url="http://%s:%i/pks/add" % (server["host"], int(server["port"])))
        post_data = {'keytext': self.asciiArmoredKey}
        http_request.method = "POST"
        http_request.body = urllib.urlencode(post_data)
        try:
            response = http_client.fetch(http_request)
            if int(response.code) != 200:
                return self._handleFail()
        except httpclient.HTTPError, e:
            self.logger.warning("Error: %s" % e)
            return self._handleFail()
        return True

    def _handleFail(self):
        self.numberOfTries += 1
        if self.numberOfTries >= self.maxNumberOfTries:
            self.givingUp = True
        return False