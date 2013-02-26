#!/usr/bin/env python
# -*- coding: utf-8 -*-

import traceback
import tornado.web

from libs.utils import ObjectDict, get_home_time, format_time
from libs.models import UserMixin
from config import SITE_NAME

class BaseHandler(tornado.web.RequestHandler, UserMixin):

    @property
    def db(self):
        return self.application.db
    
    def prepare(self):
        self._prepare_context()
        self._prepare_filters()

    def render_string(self, template_name, **kwargs):
        kwargs.update(self._filters)
        assert "context" not in kwargs, "context is a reserved keyword."
        kwargs["context"] = self._context
        return super(BaseHandler, self).render_string(template_name, **kwargs)

    def get_current_user(self):
        token = self.get_secure_cookie("token")
        if not token:
            return None
        salt = token.split("/")[0]
        user_id = token.split("/")[1]
        if not user_id:
            return None
        user = self.get_user_by_id(int(user_id))
        if user.salt!=salt.strip():
            return None
        return user

    def get_error_html(self, status_code, **kwargs):
        if status_code==404:
            return self.render_string("e404.html")
        else:
            try:
                exception = "%s\n\n%s" % (kwargs["exception"], traceback.format_exc())
                if self.settings.get("debug"):
                    self.set_header('Content-Type', 'text/plain')
                    for line in exception:
                        self.write(line)
                else:
                    self.write("oOps...! I made ​​a mistake... ")
            except Exception:
                return super(BaseHandler, self).get_error_html(status_code, **kwargs)
        

    def _prepare_context(self):
        self._context = ObjectDict()
        self._context.sitename = SITE_NAME

    def _prepare_filters(self):
        self._filters = ObjectDict()
        self._filters.get_home_time = get_home_time
        self._filters.time = format_time


    def abort(self, code):
        if code==404:
            raise tornado.web.HTTPError(404)
        if code==403:
            raise tornado.web.HTTPError(403)
