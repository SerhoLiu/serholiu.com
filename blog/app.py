#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import sys

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from libs import sqlite3lib
from config import COOKIE_SECRET, DATABASE
from blog import handlers as handler


class Application(tornado.web.Application):
    def __init__(self):
        handlers = handler
        settings = dict(
                template_path=os.path.join(os.path.dirname(__file__), "templates"),
                static_path=os.path.join(os.path.dirname(__file__), "static"),
                xsrf_cookies=True,
                cookie_secret=COOKIE_SECRET,
                login_url="/auth/signin",
                autoescape=None,
                debug=True,
               )
        tornado.web.Application.__init__(self, handlers, **settings)
        self.db = sqlite3lib.Connection(DATABASE)

def main():
    port = int(sys.argv[1].split('=')[1])
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
