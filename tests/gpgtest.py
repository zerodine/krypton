__author__ = 'thospy'

import unittest
from krypton.hkpplus.libs.gpg import Gpg, GpgSignatureException, Jws
from abstracttestcase import AbstractTestCase


class GpgTest(AbstractTestCase):

    def test_getKeyid(self):
        keyPub = self._readKey("demodata/key02.gpg")
        keyPriv = self._readKey("demodata/key02.priv.gpg")

        data = {"plain": "This Text is signed"}

        jws = Jws(publicKey=keyPub, privateKey=keyPriv)
        signedData = jws.sign(data)
        print signedData
        jws2 = Jws()
        keyId = jws2.getSignedKeyId(signedData)

        self.assertEqual(keyId, "8EC0AE04CBB22E3664B2FE17B0B775686ECCF537")

    def test_jws(self):
        keyPub = self._readKey("demodata/key02.gpg")
        keyPriv = self._readKey("demodata/key02.priv.gpg")

        data = {"Username": "jbauer", "email":"jack.bauer@gmail.com"}

        jws = Jws(publicKey=keyPub, privateKey=keyPriv)
        signedData = jws.sign(data)
        #print signedData
        verifiedData = jws.verify(data=signedData)

        self.assertDictEqual(data, verifiedData[1])

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
