#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import io
import sys
import errno
import datetime
from functools import total_ordering

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


@total_ordering
class StringTime:

    def __init__(self, time):
        """
        :param time: 2016-04-20 21:49:34
        """
        self.time = time

        t = [int(tt) for tt in re.findall(r"[0-9]+", time)]
        t.append(0)
        self._datetime = datetime.datetime(*t)

    def __str__(self):
        return self.time

    def __eq__(self, other):
        return self.time == other.time

    def __lt__(self, other):
        return self.time < other.time

    @property
    def date(self):
        """
        :return: 2016-04-20
        """
        return self.time.split(" ")[0].strip()

    @property
    def year(self):
        """
        :return: 2016
        """
        return self.time.split("-")[0].strip()

    @property
    def home(self):
        """
        :return: 20 Apr
        """
        return self._datetime.strftime("%d %b")

    @property
    def ios8601(self):
        """
        :return: 2016-04-20T21:49:34Z
        """
        iso8601 = self._datetime.isoformat()
        if self._datetime.tzinfo:
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
