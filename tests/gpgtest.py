__author__ = 'thospy'

import unittest
from krypton.hkpplus.libs.gpg import Gpg, GpgSignatureException
from abstracttestcase import AbstractTestCase


class GpgTest(AbstractTestCase):
    def test_encryption_seperateinstances(self):
        keyPub = self._readKey("demodata/key02.gpg")
        keyPriv = self._readKey("demodata/key02.priv.gpg")

        g = Gpg()
        g2 = Gpg()

        id = g.loadKey(str(keyPub))
        g2.loadKey(str(keyPriv))

        message = "This message is extremely secure!!!! "
        encrypted = g.encrypt(plaintext=message, recipientKeyId=id)
        messageDecrypted = g2.decrypt(encryptedText=encrypted, keyPassword="Feelfree")
        self.assertEqual(message, messageDecrypted)

        signature = g2.sign(id, message, keyPassword="Feelfree", detach=True)
        self.assertTrue(g.verify(original=message, signature=signature))

        #try:
        #    print g.verify(original="Blubdb", signature=signature)
        #except GpgSignatureException, e:
        #    print "Signature is not valid"

    @staticmethod
    def getSuite():
        test_suite = unittest.TestSuite()
        test_suite.addTest(unittest.makeSuite(AbstractTestCase))
        return test_suite

if __name__ == '__main__':
    unittest.main()
