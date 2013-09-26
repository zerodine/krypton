__author__ = 'thospy'

import os
import krypton

class ApplicationContext(object):
    applicationName = "Krypton Keyserver"
    version = "0.1"
    url = "https://github.com/zerodine/krypton/"
    serverContact = "tspycher"

    config = None
    queue = None
    gossipServers = None

    basePath = "."

    def __init__(self):
        """
        Get the absolute path of the krypton module. This path is important for accessing
        templates etc.

        """
        self.basePath = os.path.dirname(krypton.__file__)