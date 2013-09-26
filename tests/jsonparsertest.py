__author__ = 'thospy'

import unittest
import json

from abstracttestcase import AbstractTestCase
from krypton.hkpserver.libs.gpgjsonparser import JsonParser

class JsonParserTest(AbstractTestCase):


    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_parsing(self):
        cert = self._readKey("demodata/key01.gpg")
        j = JsonParser(asciiData=cert)
        data = json.loads(j.dump())
        print data

        self.assertEquals(data["fingerprint"], "27C5017E0755AD31BF40832BCF96B54D3E08F9F5", "Finger print missmatch")

    @staticmethod
    def getSuite():
        test_suite = unittest.TestSuite()
        test_suite.addTest(unittest.makeSuite(JsonParserTest))
        return test_suite


if __name__ == '__main__':
    unittest.main()
