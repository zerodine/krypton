__author__ = 'thospy'

#!/usr/bin/env python

#import sys, os
import ConfigParser

from src.hkpserver import Server, Config

if __name__ == "__main__":
    c = ConfigParser.RawConfigParser(allow_no_value=True)
    c.read("server.conf")

    config = Config()
    config.mongoDatabase = c.get("mongodb", "mongoDatabase")
    config.mongoConnectionUrl = c.get("mongodb", "mongoConnectionUrl")

    server = Server(config=config)
    try:
        server.start(8888)
    except KeyboardInterrupt:
        pass
    finally:
        pass