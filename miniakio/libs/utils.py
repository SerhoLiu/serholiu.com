#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import hmac
import base64
import datetime
import functools
from hashlib import sha1
from html.parser import HTMLParser

from blogconfig import COOKIE_SECRET


class ObjectDict(dict):

    def __getattr__(self, key):
        if key in self:
            return self[key]
        return None

    def __setattr__(self, key, value):
        self[key] = value


# 所有日期采用 `YYYY-MM-DD HH:MM` 格式字符串存储，
# 下面的三个函数用于获取年月日、年和将字符串转换为时间对象

def get_home_time(time):
    time = time.split(" ")[0].strip()
    return time


def get_time_year(time):
    t = get_home_time(time)
    year = t.split("-")[0].strip()
    return year


def format_time(time):
    t = [int(tt) for tt in re.findall(r"[0-9]+", time)]
    t.append(0)
    d = datetime.datetime(*t)
    return d


def get_show_time(time):
    t = [int(tt) for tt in re.findall(r"[0-9]+", time)]
    t.append(0)
    d = datetime.datetime(*t)
    return d.strftime("%d %b")


def archives_list(posts):
    """
    生成文章存档，按年分类
    """
    years = list(set([get_time_year(post.published) for post in posts]))
    years.sort(reverse=True)
    for year in years:
        year_posts = [post for post in posts
                      if get_time_year(post.published) == year]
        yield (year, year_posts)


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


# 因为删除文章链接使用的是 GET 而非 POST，所以无法使用 Tornado 自带的 xsrf
# 预防方法，因此这里使用简单的加密方法，构造文章删除链接
def base64_encode(string):
    """
    base64 encodes a single string. The resulting string is safe for
    putting into URLs.
    """
    return base64.urlsafe_b64encode(string).strip(b'=')


def signer_code(id):
    mac = hmac.new(COOKIE_SECRET.encode(), digestmod=sha1)
    mac.update(id.encode())
    s = mac.digest()
    signer = id + '.' + base64_encode(s).decode()
    return signer


def unsigner_code(signer):
    id, base64_s = signer.split('.')
    mac = hmac.new(COOKIE_SECRET.encode(), digestmod=sha1)
    mac.update(id.encode())
    s = mac.digest()
    if base64_s == base64_encode(s).decode():
        return id
    else:
        return None


# Mobile Detect
def is_mobile(user_agent):
    detects = "iPod|iPhone|Android|Opera Mini|BlackBerry| \
               webOS|UCWEB|Blazer|PSP|IEMobile"
    return re.search(detects, user_agent)


# 去除文章description中的html标签
class MLStripper(HTMLParser):

    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()
