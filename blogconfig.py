#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

# 用于 cookie 加密，请换一个随机的，足够长，足够复杂的字符串
# !!! 不要使用现在这个
COOKIE_SECRET = "2417540af18f6aab0afe5d606e1b10f4"

# 数据库文件路径，默认是和配置文件同目录
# eg. DATABASE = "/home/myblog/mydb.db"
DATABASE = os.path.join(os.path.dirname(__file__), "db/blog.db")

# 你的博客名
SITE_NAME = u"我爱这世界!"

# Picky 目录路径，默认和配置文件同目录
PICKY_DIR = os.path.join(os.path.dirname(__file__), "picky")


# 如果在生成环境下，可以关闭 Debug 选项，这样将缓存编译好的模板，加快模板渲染速度
# 不过修改模板或代码后，需要重新启动博客，这样才有效果
#DEBUG = True
DEBUG = False

del os
