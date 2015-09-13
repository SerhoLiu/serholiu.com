#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
扩展 `tornado.web.BaseHandler` 以方便添加模板 filter 和 全局变量，
并对默认的错误页进行修改
"""

import traceback
import tornado.web

from .utils import ObjectDict, is_mobile, strip_tags
from .utils import get_time_date, get_home_time, format_time
from .models import UserMixin


class BaseHandler(tornado.web.RequestHandler, UserMixin):

    @property
    def db(self):
        return self.application.db

    @property
    def config(self):
        return self.application.config

    def prepare(self):
        self.context = ObjectDict()
        self.context.is_mobile = is_mobile(
            self.request.headers.get("User-Agent", "")
        )

    def get_template_namespace(self):
        namespace = super(BaseHandler, self).get_template_namespace()
        namespace.update(**dict(
            config=self.application.config,
            context=self.context,
            home_time=get_home_time,
            time_date=get_time_date,
            format_time=format_time,
            strip_tags=strip_tags,
        ))

        return namespace

    def get_current_user(self):
        token = self.get_secure_cookie("token")
        if not token:
            return None
        salt, user_id = token.split(b"/")
        if not user_id:
            return None
        user = self.get_user_by_id(int(user_id))
        if (not user) or user.salt.encode("utf-8") != salt.strip():
            return None
        return user

    def write_error(self, status_code, **kwargs):
        """
        请求错误处理：
            1. 404 错误：将使用 `templates/e404.html` 作为 404 页面
            2. 其它错误，如果在 `app.py` 中设置 `debug = True` 将会显示错误信息，否则
               输出简单的提示。
        """

        if status_code == 404:
            return self.render("e404.html")

        try:
            if self.settings.get("serve_traceback") and "exc_info" in kwargs:
                # in debug mode, try to send a traceback
                self.set_header('Content-Type', 'text/plain')
                for line in traceback.format_exception(*kwargs["exc_info"]):
                    self.write(line)
                self.finish()
            else:
                self.finish("oOps...! I made ​​a mistake... ")
        except Exception:
            return super(BaseHandler, self).write_error(
                status_code, **kwargs
            )

    def abort(self, code):
        raise tornado.web.HTTPError(code)
