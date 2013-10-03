__author__ = "Thomas Spycher, Philipp Spinnler"
__copyright__ = "Copyright 2013, Zerodine GmbH (zerodine.com) "
__credits__ = ["Thomas Spycher", "Philipp Spinnler"]
__license__ = "Apache-2.0"
__maintainer__ = "Thomas Spycher"
__email__ = "me@tspycher.com"
__status__ = "Development"

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