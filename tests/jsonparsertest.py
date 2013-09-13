__author__ = 'thospy'

import unittest
import json

from src.hkpserver.gpgjsonparser import JsonParser

class JsonParserTest(unittest.TestCase):


    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_parsing(self):
        cert = self._readKey("demodata/key01.gpg")
        j = JsonParser(asciiData=cert)
        data = json.loads(j.dump())

        self.assertEquals(data["fingerprint"], "27C5017E0755AD31BF40832BCF96B54D3E08F9F5", "Finger print missmatch")

    def _readKey(self, file):
        with open(file, 'r') as content_file:
            content = content_file.read()
        return content

if __name__ == '__main__':
    unittest.main()
