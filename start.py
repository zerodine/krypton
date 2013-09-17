#!/usr/bin/env python
from Queue import Queue

__author__ = 'thospy'


import ConfigParser
import argparse
import logging

from src.hkpserver import Server, Config, ApplicationContext

if __name__ == "__main__":
    # parsing cli arguments
    parser = argparse.ArgumentParser(description='Runs the Krypton GPG Keyserver')
    parser.add_argument('--configFile', '-c',
                        dest='configFile',
                        action='store',
                        default="server.conf",
                        help='Configuration File for the Server')
    parser.add_argument('--port', '-p',
                        dest='port',
                        action='store',
                        type=int,
                        default=8888, # default should be 11371
                        help='Port to run the server')

    args = parser.parse_args()

    # getting a configfile parser
    c = ConfigParser.RawConfigParser(allow_no_value=True)
    c.read(args.configFile)

    config = Config()
    config.mongoDatabase = c.get("mongodb", "mongoDatabase")
    config.mongoConnectionUrl = c.get("mongodb", "mongoConnectionUrl")
    config.mongoCollection = c.get("mongodb", "mongoCollection")

    app = ApplicationContext()
    app.config = config
    app.queue = Queue()

    server = Server(applicationContext=app)

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
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)

    try:
        server.start(args.port)
    except KeyboardInterrupt:
        logging.info('Server stopped')
    finally:
        pass