# -*- coding: utf-8 -*-

import os
import re
import io
import sys
import errno
import shutil
import hashlib
import datetime
import posixpath
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


def calc_file_md5(filepath):
    """
    Calc file md5 checksum
    """
    md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        while True:
            data = f.read(64 * 1024)
            if not data:
                break
            md5.update(data)

    return md5.hexdigest()


class StaticAssetUrl:

    def __init__(self, base_dir):
        self._base_dir = base_dir
        self._cache = {}

    def __call__(self, *args, **kwargs):
        if len(args) > 0:
            url = args[0]
        else:
            url = kwargs.get("url")

        if url is None:
            raise Exception("need 'url' args")

        value = self._cache.get(url)
        if value:
            return value

        value = self._add_md5(url)
        self._cache[url] = value

        return value

    def _add_md5(self, url):
        """
        给静态资源加上 md5 string
        """
        _url = url.lstrip("/") if url.startswith("/") else url
        static_path = os.path.join(self._base_dir, _url)
        if not os.path.exists(static_path):
            raise Exception(
                "static '{}' file not exists in dir '{}'".format(
                    url, self._base_dir
                )
            )

        md5 = calc_file_md5(static_path)
        dirname = os.path.dirname(static_path)
        filename = os.path.basename(static_path)
        parts = filename.split(".", 1)
        parts.insert(1, md5)
        new_path = os.path.join(dirname, ".".join(parts))
        if not os.path.exists(new_path):
            shutil.move(static_path, new_path)

        base_url = posixpath.dirname(url)

        return posixpath.join(base_url, ".".join(parts))


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
    def year(self):
        """
        :return: 2016
        """
        return self.time.split("-")[0].strip()

    @property
    def date(self):
        """
        :return: 20 Apr, 2018
        """
        return self._datetime.strftime("%d %b, %Y")

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
