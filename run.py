#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.ioloop
import tornado.options
import tornado.httpserver
from tornado.log import gen_log
from tornado.options import define, options

from miniakio import Application


define("port", default=8888, help="run on the given port", type=int)


def start():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    gen_log.info("* start at: http://localhost:%d", options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    start()
