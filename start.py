__author__ = 'thospy'

#!/usr/bin/env python

import ConfigParser
import argparse

from src.hkpserver import Server, Config

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Runs the Krypton GPG Keyserver')
    parser.add_argument('--configFile', '-c',
                        dest='configFile',
                        action='store',
                        default="server.conf",
                        help='Configuration File for the Server')

    args = parser.parse_args()

    c = ConfigParser.RawConfigParser(allow_no_value=True)
    c.read(args.configFile)

    config = Config()
    config.mongoDatabase = c.get("mongodb", "mongoDatabase")
    config.mongoConnectionUrl = c.get("mongodb", "mongoConnectionUrl")
    config.mongoCollection = c.get("mongodb", "mongoCollection")
    server = Server(config=config)
    try:
        server.start(8888)
    except KeyboardInterrupt:
        pass
    finally:
        pass