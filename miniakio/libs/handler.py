#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    扩展 `tornado.web.BaseHandler` 以方便添加模板 filter 和 全局变量，
    并对默认的错误页进行修改。
"""

import traceback
import tornado.web

from .utils import ObjectDict
from .utils import get_home_time, format_time, get_show_time
from .utils import is_mobile, strip_tags
from .models import UserMixin
from blogconfig import SITE_NAME


class BaseHandler(tornado.web.RequestHandler, UserMixin):

    @property
    def db(self):
        return self.application.db

    def prepare(self):
        self._prepare_context()
        self._prepare_filters()

    def render_string(self, template_name, **kwargs):
        """
        重写 `render_string` 方法，以便加入自定义 filter 和自定义模板全局变量
        """
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
        if user.salt != salt.strip():
            return None
        return user

    def get_error_html(self, status_code, **kwargs):
        """
        请求错误处理：
            1. 404 错误：将使用 `templates/e404.html` 作为 404 页面
            2. 其它错误，如果在 `app.py` 中设置 `debug = True` 将会显示错误信息，否则
               输出简单的提示。
        """
        if status_code == 404:
            return self.render_string("e404.html")
        else:
            try:
                exception = "%s\n\n%s" % (kwargs["exception"],
                    traceback.format_exc())
                if self.settings.get("debug"):
                    self.set_header('Content-Type', 'text/plain')
                    for line in exception:
                        self.write(line)
                else:
                    self.write("oOps...! I made ​​a mistake... ")
            except Exception:
                return super(BaseHandler, self).get_error_html(status_code,
                    **kwargs)

    def _prepare_context(self):
        """
        将自定义变量传入模板，作为全局变量，引用时使用 `context.var` 的形式
        """
        self._context = ObjectDict()
        self._context.sitename = SITE_NAME
        self._context.is_mobile = is_mobile(self.request.headers['User-Agent'])

    def _prepare_filters(self):
        """
        将自定义 filter 传入模板
        """
        self._filters = ObjectDict()
        self._filters.get_home_time = get_home_time
        self._filters.get_show_time = get_show_time
        self._filters.time = format_time
        self._filters.strip_tags = strip_tags

    def abort(self, code):
        raise tornado.web.HTTPError(code)
