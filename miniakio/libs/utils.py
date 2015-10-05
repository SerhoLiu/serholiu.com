#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import hmac
import base64
import hashlib
import datetime
import functools
from html.parser import HTMLParser


class ObjectDict(dict):

    def __getattr__(self, key):
        if key in self:
            return self[key]
        return None

    def __setattr__(self, key, value):
        self[key] = value


# 所有日期采用 `YYYY-MM-DD HH:MM` 格式字符串存储，
# 下面的三个函数用于获取年月日、年和将字符串转换为时间对象

def format_time(time):
    t = [int(tt) for tt in re.findall(r"[0-9]+", time)]
    t.append(0)
    return datetime.datetime(*t)


def get_time_date(time):
    time = time.split(" ")[0].strip()
    return time


def get_time_year(time):
    year = time.split("-")[0].strip()
    return year


def get_home_time(time):
    return format_time(time).strftime("%d %b")


def authenticated(method):
    """Decorate methods with this to require that the user be logged in."""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            if self.request.method in ("GET", "HEAD"):
                self.redirect("/")
                return
            self.abort(403)
        return method(self, *args, **kwargs)
    return wrapper


def random_secret():
    return os.urandom(32)


# 因为删除文章链接使用的是 GET 而非 POST，无法使用 Tornado 自带的 xsrf
# 这里通过对相关信息生成验证摘要来避免伪造请求

def signer_encode(secret, info):
    """
    对 info 使用 secret 生成验证摘要
    """
    mac = hmac.new(secret, digestmod=hashlib.sha256)
    mac.update(info.encode())
    signer = base64.urlsafe_b64encode(mac.digest()).decode()

    return "%s.%s" % (info, signer)


def signer_check(secret, signer, info):
    """
    验证 signer 是通过 secret 对 info 生成的摘要
    :param secret: 通过 signer_encode 生成的验证摘要
    """
    try:
        old, signer = signer.split('.')
    except (AttributeError, ValueError):
        return False

    if old != info:
        return False

    mac = hmac.new(secret, digestmod=hashlib.sha256)
    mac.update(info.encode())
    check = mac.digest()
    return base64.urlsafe_b64decode(signer) == check


# 去除文章description中的html标签
class MLStripper(HTMLParser):

    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return "".join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data().replace("\n", "")
