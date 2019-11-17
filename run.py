#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import traceback

from miniakio.blog import Blog
from miniakio.utils import echo


if __name__ == "__main__":
    usage = "Usage: %s [build, server]"
    if len(sys.argv) < 2:
        echo.error(usage, sys.argv[0])
        sys.exit(1)

    conf = os.environ.get("ENV_MINIAKIO_CONF", "config.yaml")
    if not os.path.exists(conf):
        echo.error("config file '%s' not exists", conf)

    pwd = os.path.dirname(__file__)

    blog = Blog(pwd, conf)
    if sys.argv[1] == "build":
        try:
            start = time.time()
            blog.build()
            echo.warn("build finish, cost %s", time.time() - start)
        except Exception as e:
            echo.error("build failed, %s: %s", e, traceback.format_exc())
    elif sys.argv[1] == "server":
        if len(sys.argv) == 3:
            blog.server(int(sys.argv[2]))
        else:
            blog.server()
    else:
        echo.error(usage, sys.argv[0])
        sys.exit(1)
