#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import datetime
import functools

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
    d=datetime.datetime(*t)
    return d

def archives_list(posts):
    years = list(set([get_time_year(post.published) for post in posts]))
    years.sort(reverse=True)
    for year in years:
        year_posts = [post for post in posts if get_time_year(post.published)==year]
        yield (year,year_posts)
