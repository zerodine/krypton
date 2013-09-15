__author__ = 'thospy'

import unittest, ConfigParser
from src.hkpserver import Config


class AbstractTestCase(unittest.TestCase):
    config = None

    @classmethod
    def setUpClass(cls):
        c = ConfigParser.RawConfigParser(allow_no_value=True)
        c.read("../server.test.conf")
        cls.config = Config()
        cls.config.mongoDatabase = c.get("mongodb", "mongoDatabase")
        cls.config.mongoConnectionUrl = c.get("mongodb", "mongoConnectionUrl")
        cls.config.mongoCollection = c.get("mongodb", "mongoCollection")

    def _readKey(self, file):
        with open(file, 'r') as content_file:
            content = content_file.read()
        return content