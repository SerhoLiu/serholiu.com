#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import tornado.web
from .libs import sqlite3lib
from .blog import handlers as handler
from blogconfig import COOKIE_SECRET, DATABASE, DEBUG


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
