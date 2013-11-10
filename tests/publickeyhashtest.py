import StringIO

__author__ = 'tspycher'

import unittest
#from operator import itemgetter
#import hashlib, bitstring
#import binascii
import pgpdump
from pgpdump.utils import sksHash


class PublickeyHashTest(unittest.TestCase):

    pubkey = """-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: SKS 1.1.4
Comment: Hostname: sks01.keyhub.io

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
=7sxV
-----END PGP PUBLIC KEY BLOCK-----"""

    pubkeyHash = "A20E35AC1AEE03E870FCFEBAF5EE3C21"

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_hash(self):
        key = pgpdump.AsciiData(self.pubkey)
        h = sksHash(list(key.packets()))
        self.assertEqual(h.upper(), self.pubkeyHash.upper())

    @staticmethod
    def getSuite():
        test_suite = unittest.TestSuite()
        test_suite.addTest(unittest.makeSuite(PublickeyHashTest))
        return test_suite
if __name__ == '__main__':
    unittest.main()
