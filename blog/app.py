#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path

import tornado.web
import tornado.ioloop
import tornado.options
import tornado.httpserver
from tornado.options import define, options

from libs import sqlite3lib
from config import COOKIE_SECRET, DATABASE, DEBUG
from blog import handlers as handler

define("port", default=8888, help="run on the given port", type=int)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = handler
        settings = dict(
            template_path = os.path.join(os.path.dirname(__file__), "templates"),
            static_path = os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies = True,
            cookie_secret = COOKIE_SECRET,
            login_url = "/auth/signin",
            autoescape = None,
            debug = DEBUG,
        )
        tornado.web.Application.__init__(self, handlers, **settings)
        self.db = sqlite3lib.Connection(DATABASE)


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
