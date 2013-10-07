import logging

__author__ = 'thospy'

import unittest, ConfigParser
from krypton.hkpserver import Config


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


        # set up logging to file - see previous section for more details
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M',
                            filename='/tmp/krypton.log',
                            filemode='w')
        # define a Handler which writes INFO messages or higher to the sys.stderr
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        # set a format which is simpler for console use
        formatter = logging.Formatter('%(name)-22s: %(levelname)-8s %(message)s')
        # tell the handler to use this format
        console.setFormatter(formatter)
        # add the handler to the root logger
        logging.getLogger('').addHandler(console)

    def _readKey(self, file):
        with open(file, 'r') as content_file:
            content = content_file.read()
        return content