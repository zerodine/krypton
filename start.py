__author__ = 'thospy'

#!/usr/bin/env python

import sys, os
from src.hkpserver import Server

if __name__ == "__main__":
    server = Server()
    try:
        server.start(8888)
    except KeyboardInterrupt:
        pass
    finally:
        pass