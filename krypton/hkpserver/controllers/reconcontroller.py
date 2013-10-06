__author__ = "Thomas Spycher, Philipp Spinnler"
__copyright__ = "Copyright 2013, Zerodine GmbH (zerodine.com) "
__credits__ = ["Thomas Spycher", "Philipp Spinnler"]
__license__ = "Apache-2.0"
__version__ = "0.0.1"
__maintainer__ = "Thomas Spycher"
__email__ = "me@tspycher.com"
__status__ = "Development"

from basecontroller import BaseController
from krypton.hkpserver.libs.recon import Recon

class ReconController(BaseController):
    recon = Recon()

    def get(self, *args, **kwargs):
        self.write("Blubb")

    @staticmethod
    def routes(prefix="", applicationContext=None):
        """

        :param prefix:
        :param applicationContext:
        :return:
        """
        return r"%s/recon(.*)" % prefix, ReconController, dict(applicationContext=applicationContext)