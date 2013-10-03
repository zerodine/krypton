__author__ = "Thomas Spycher, Philipp Spinnler"
__copyright__ = "Copyright 2013, Zerodine GmbH (zerodine.com) "
__credits__ = ["Thomas Spycher", "Philipp Spinnler"]
__license__ = "Apache-2.0"
__maintainer__ = "Thomas Spycher"
__email__ = "me@tspycher.com"
__status__ = "Development"

import random


class GossipServers(object):

    _servers = []

    def __init__(self, serverList = []):
        for s in serverList:
            if not s:
                continue
            ss = str(s).split(":")
            port = "11371"
            if len(ss) >= 2:
                port = ss[1]
            self._servers.append({"host": ss[0], "port": port})

    def getRandom(self):
        if len(self._servers):
            return self._servers[random.randint(0, len(self._servers)-1)]
        return None

    def getAll(self):
        return self._servers

    def __repr__(self):
        y = []
        for x in self._servers:
            y.append("hkp://%s:%s" % (x["host"], x["port"]))
        return "\n".join(y)