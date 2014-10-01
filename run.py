#!/usr/bin/env python
# -*- coding: utf-8 -*-
import tornado.ioloop
import tornado.options
import tornado.httpserver
from tornado.options import define, options
from miniakio import Application

#开发调试时使用
define("port", default=8000, help="run on the given port for develop", type=int)

def start():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    start()
