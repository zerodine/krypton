__author__ = 'thospy'

import unittest
import json

from abstracttestcase import AbstractTestCase
from krypton.hkpserver.libs.gpgjsonparser import MrParser, JsonParser

class MrParserTest(AbstractTestCase):

    key = []

    def setUp(self):
        cert = self._readKey("demodata/key01.gpg")
        j = JsonParser(asciiData=cert)
        self.key.append(json.loads(j.dump()))

    def tearDown(self):
        self.key = []

    def test_parsing(self):
        mr = MrParser(jsonData=self.key)
        print mr.parse()


    @staticmethod
    def getSuite():
        test_suite = unittest.TestSuite()
        test_suite.addTest(unittest.makeSuite(MrParserTest))
        return test_suite

if __name__ == '__main__':
    unittest.main()
