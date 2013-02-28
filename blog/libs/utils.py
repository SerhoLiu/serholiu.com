#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import datetime
import functools
import base64
from hashlib import sha1
import hmac
from config import COOKIE_SECRET


class ObjectDict(dict):
    
    def __getattr__(self, key):
        if key in self:
            return self[key]
        return None

    def __setattr__(self, key, value):
        self[key] = value


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


def archives_list(posts):
    years = list(set([get_time_year(post.published) for post in posts]))
    years.sort(reverse=True)
    for year in years:
        year_posts = [post for post in posts if get_time_year(post.published) == year]
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


def base64_encode(string):
    """base64 encodes a single string. The resulting string is safe for
    putting into URLs.
    """
    return base64.urlsafe_b64encode(string).strip('=')


def signer_code(id):
    mac = hmac.new(COOKIE_SECRET, digestmod=sha1)
    mac.update(id)
    s = mac.digest()
    signer = id + '.' + base64_encode(s)
    return signer


def unsigner_code(signer):
    id, base64_s = signer.split('.')
    mac = hmac.new(COOKIE_SECRET, digestmod=sha1)
    mac.update(id)
    s = mac.digest()
    if base64_s == base64_encode(s):
        return id
    else:
        return None
