#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import io
import sys
import errno
import datetime

try:
    import curses
except ImportError:
    curses = None


def read_file(filepath):
    with io.open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def write_file(filepath, content):
    with io.open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


def ensure_dir_exists(dirname):
    try:
        os.makedirs(dirname)
    except OSError as err:
        if err.errno == errno.EEXIST and os.path.isdir(dirname):
            pass
        else:
            raise


def parse_time(time):
    """
    :param time: 2016-04-20 21:49:34
    :return: datetime.datetime
    """
    t = [int(tt) for tt in re.findall(r"[0-9]+", time)]
    t.append(0)
    return datetime.datetime(*t)


def get_time_date(time):
    """
    :param time: 2016-04-20 21:49:34
    :return: 2016-04-20
    """
    time = time.split(" ")[0].strip()
    return time


def get_time_year(time):
    """
    :param time: 2016-04-20 21:49:34
    :return: 2016
    """
    year = time.split("-")[0].strip()
    return year


def get_home_time(time):
    """
    :param time: 2016-04-20 21:49:34
    :return: 20 Apr
    """
    return parse_time(time).strftime("%d %b")


def get_ios8601_time(time):
    """
    :param time: 2016-04-20 21:49:34
    :return: 2016-04-20T21:49:34Z
    """
    t = parse_time(time)
    iso8601 = t.isoformat()
    if t.tzinfo:
        return iso8601
    return iso8601 + "Z"


def _stdout_supports_color():
    color = False
    if curses and hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
        try:
            curses.setupterm()
            if curses.tigetnum("colors") > 0:
                color = True
        except Exception:
            pass

    return color


class _Echo:

    Blue = 4
    Green = 2
    Yellow = 3
    Red = 1

    FORMAT = u"%(color)s%(text)s%(end_color)s\n"

    def __init__(self, fmt=FORMAT):
        self._colors = {}
        self._fmt = fmt
        if _stdout_supports_color():
            fg_color = (
                curses.tigetstr("setaf") or
                curses.tigetstr("setf") or ""
            )
            for code in [self.Blue, self.Green, self.Yellow, self.Red]:
                self._colors[code] = str(
                    curses.tparm(fg_color, code), "ascii"
                )
            self._normal = str(curses.tigetstr("sgr0"), "ascii")
        else:
            self._normal = ""

    def _echo_colored_text(self, text, color):
        args = {
            "text": text,
        }

        if color in self._colors:
            args["color"] = self._colors[color]
            args["end_color"] = self._normal
        else:
            args["color"] = args["end_color"] = ""

        msg = self._fmt % args

        sys.stderr.write(msg)
        sys.stderr.flush()

    def info(self, text, *args):
        if args:
            text = text % args
        self._echo_colored_text(text, self.Green)

    def warn(self, text, *args):
        if args:
            text = text % args
        self._echo_colored_text(text, self.Yellow)

    def error(self, text, *args):
        if args:
            text = text % args
        self._echo_colored_text(text, self.Red)


echo = _Echo()
