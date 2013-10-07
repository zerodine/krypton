__author__ = "Thomas Spycher, Philipp Spinnler"
__copyright__ = "Copyright 2013, Zerodine GmbH "
__credits__ = ["Thomas Spycher", "Philipp Spinnler"]
__license__ = "Apache-2.0"
__version__ = "0.0.1"
__maintainer__ = "Thomas Spycher"
__email__ = "me@tspycher.com"
__status__ = "Test"

import os
import random
from krypton.hkpserver.libs.gpgmongo import GpgModel
from krypton.hkpserver.libs.recon import Recon, ReconPartner
from tests.abstracttestcase import AbstractTestCase

import unittest

class ReconTest(AbstractTestCase):
    gpgModel1 = None
    gpgModel2 = None

    basefolder = "demodata/mass"

    def setUp(self):
        self.gpgModel1 = GpgModel(connectionUrl=self.config.mongoConnectionUrl)
        self.gpgModel1.connect(db=self.config.mongoDatabase)
        self.gpgModel1.collection = "testReconPartner1"

        self.gpgModel2 = GpgModel(connectionUrl=self.config.mongoConnectionUrl)
        self.gpgModel2.connect(db=self.config.mongoDatabase)
        self.gpgModel2.collection = "testReconPartner2"

        self._loadTestdata()

    def tearDown(self):
        self.gpgModel1.cleanTestCollections()
        self.gpgModel1 = None

        self.gpgModel2.cleanTestCollections()
        self.gpgModel2 = None

    def test_recon(self):
        # Adding updated keys
        self.gpgModel1.uploadKey(self._readKey("demodata/recon/ABDFF806_1.asc"))
        self.gpgModel2.uploadKey(self._readKey("demodata/recon/ABDFF806_2.asc"))
        self.gpgModel2.uploadKey(self._readKey("demodata/recon/D1FB51A3_1.asc"))
        self.gpgModel1.uploadKey(self._readKey("demodata/recon/D1FB51A3_2.asc"))

        hashes1 = self.gpgModel1.getHashes()
        hashes2 = self.gpgModel2.getHashes()

        r = Recon()
        stats = r.syncPartners(
            reconPartner1=ReconPartner(url=None, hashes=hashes1, model=self.gpgModel1),
            reconPartner2=ReconPartner(url=None, hashes=hashes2, model=self.gpgModel2),
        )
        print stats
        self.assertEqual(len(set(self.gpgModel1.getHashes()).symmetric_difference(set(self.gpgModel2.getHashes()))), 0)


    def _loadTestdata(self):
        partner1 = 0
        partner2 = 0
        for d in os.listdir(self.basefolder):
            for f in os.listdir("%s/%s" % (self.basefolder, d)):
                keyFile = "%s/%s/%s" % (self.basefolder, d, f)
                key = self._readKey(keyFile)
                #print "importing %s" % keyFile
                randVal = random.randint(100, 102) - 100
                if randVal == 2:
                    partner1 += 1
                    self.gpgModel1.uploadKey(key)
                    continue
                elif randVal == 1:
                    partner2 += 1
                    self.gpgModel2.uploadKey(key)
                    continue
                elif randVal == 0:
                    partner1 += 1
                    self.gpgModel1.uploadKey(key)
                    partner2 += 1
                    self.gpgModel2.uploadKey(key)
                    continue

        #print partner1
        #print partner2

if __name__ == '__main__':
    unittest.main()
