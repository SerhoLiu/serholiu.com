#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import tornado.web
from tornado.escape import xhtml_escape

from .libs import sqlite3lib, utils
from .blog import handlers as handler

import blogconfig


class Application(tornado.web.Application):

    def __init__(self):
        self._setup_config()

        handlers = handler
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            cookie_secret=self.config.secret,
            login_url="/auth/signin",
            autoescape=None,
            debug=self.config.debug,
        )
        tornado.web.Application.__init__(self, handlers, **settings)

        self.db = sqlite3lib.Connection(self.config.database)

    def _setup_config(self):
        config = {}
        for key in dir(blogconfig):
            # ignore module builtin
            if not key.startswith("_"):
                config[key] = getattr(blogconfig, key)

        if "secret" in config:
            config["secret"] = config["secret"].encode()
        else:
            config["secret"] = utils.random_secret()

        config["blogname"] = xhtml_escape(config["blogname"])
        config["blogdesc"] = xhtml_escape(config["blogdesc"])

        self.config = utils.ObjectDict(config)
