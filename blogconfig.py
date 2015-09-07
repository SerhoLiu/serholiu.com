#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os


# 博客名和简介
blogname = "I'm Force"
blogdesc = "May the Force Be with you"


# 数据库和 Picky 目录
picky = os.path.join(os.path.dirname(__file__), "picky")
database = os.path.join(os.path.dirname(__file__), "newblog.db")


# 调试模式
debug = True


del os
