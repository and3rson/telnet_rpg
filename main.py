#!/usr/bin/env python2

from gevent.monkey import patch_all

patch_all()

import gevent
import gevent.server
import engine


server = gevent.server.StreamServer(('0.0.0.0', 8081), engine.ClientHandler.create)
server.serve_forever()
