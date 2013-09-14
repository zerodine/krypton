__author__ = 'thospy'
import unittest
from src.hkpserver.gpgmongo import GpgModel
from abstracttestcase import AbstractTestCase


class GpgModelTest(AbstractTestCase):
    gpgModel = None

    def setUp(self):
        self.gpgModel = GpgModel(connectionUrl=self.config.mongoConnectionUrl)
        self.gpgModel.connect(db=self.config.mongoDatabase)
        self.gpgModel.collection = self.config.mongoCollection


    def tearDown(self):
        self.gpgModel.cleanTestCollections()
        self.gpgModel = None

    def test_uploadNewKey(self):
        key = self._readKey("demodata/key01.gpg")
        x = self.gpgModel.uploadKey(key)
        self.assertEqual(x, "27C5017E0755AD31BF40832BCF96B54D3E08F9F5", "upload of key was not sucessfull")

    def test_updateKey(self):
        key = self._readKey("demodata/key01.gpg")
        x = self.gpgModel.uploadKey(key)
        self.assertEqual(x, "27C5017E0755AD31BF40832BCF96B54D3E08F9F5", "upload of key was not sucessfull")

        # Now update the key
        key = self._readKey("demodata/key01.gpg")
        x = self.gpgModel.uploadKey(key)
        self.assertDictContainsSubset({"ok":1.0, "err":None, "updatedExisting":True}, x)

    def test_retrieveKey(self):
        keyLocal = self._readKey("demodata/key01.gpg")
        self.gpgModel.uploadKey(keyLocal)
        keyServer = self.gpgModel.retrieveKey("27C5017E0755AD31BF40832BCF96B54D3E08F9F5")
        self.assertEqual(keyLocal, keyServer)

    @staticmethod
    def suite():
        test_suite = unittest.TestSuite()
        test_suite.addTest(unittest.makeSuite(GpgModelTest))
        return test_suite

if __name__ == '__main__':
    unittest.main()
