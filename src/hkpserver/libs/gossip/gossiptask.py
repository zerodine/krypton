from tornado import httpclient
import urllib

__author__ = 'thospy'


class GossipTask(object):

    name = "Gossip Syncronisation Task"
    keyId = None
    toServer = None
    toServerPort = None
    asciiArmoredKey = None

    def __init__(self, keyId, toServer, asciiArmoredKey, toServerPort=11371):
        self.keyId = keyId
        self.asciiArmoredKey = asciiArmoredKey
        self.toServer = toServer
        self.toServerPort = toServerPort

    def doWork(self):
        http_client = httpclient.HTTPClient()
        http_request = httpclient.HTTPRequest(url="http://%s:%i/pks/add" % (self.toServer, self.toServerPort))
        post_data = {'keytext': self.asciiArmoredKey}
        http_request.method = "POST"
        http_request.body = urllib.urlencode(post_data)
        try:
            response = http_client.fetch(http_request)
            print response.body
        except httpclient.HTTPError, e:
            print "Error:", e
