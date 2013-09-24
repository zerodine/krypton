import gnupg
import os
from src.hkpserver.libs.gpgmongo import GpgModel
from tests.abstracttestcase import AbstractTestCase

__author__ = 'thospy'

import unittest


class MassTest(AbstractTestCase):
    gpg = None
    basefolder = "demodata/mass"
    numKeys = 1000
    gpgModel = None

    def setUp(self):
        self.gpgModel = GpgModel(connectionUrl=self.config.mongoConnectionUrl)
        self.gpgModel.connect(db=self.config.mongoDatabase)
        self.gpgModel.collection = self.config.mongoCollection

        self.gpg = gnupg.GPG(gnupghome='/tmp', gpgbinary="/usr/local/bin/gpg")

    @unittest.skip("Do need to import the keys again")
    def test_loadTestdata(self):
        for d in os.listdir(self.basefolder):
            for f in os.listdir("%s/%s" % (self.basefolder, d)):
                keyFile = "%s/%s/%s" % (self.basefolder, d, f)
                key = self._readKey(keyFile)
                self.gpgModel.uploadKey(key)
                print "Imported key %s" % keyFile

    @unittest.skip("Do need to create more keys")
    def test_createbulkkeys(self):
        for i in range(self.numKeys):
            input_data = self.gpg.gen_key_input(key_type="RSA", key_length=1024*4)
            keyId = self.gpg.gen_key(input_data)
            print "No %s Created key with Id %s" % (i, keyId)
            folder = "%s/%s" % (self.basefolder, str(keyId)[0])
            file = "%s/%s.gpg" % (folder, keyId)
            self._mkdir(folder)
            ascii_armored_public_keys = self.gpg.export_keys(keyId)

            try:
                f = open(file, "w")
                f.write(ascii_armored_public_keys)
                f.close()
            except:
                raise

    def _mkdir(self, dir):
        if not os.path.isfile(dir) and not os.path.isdir(dir):
            os.mkdir(dir)

if __name__ == '__main__':
    unittest.main()
