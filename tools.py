#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 用于创建数据库，请按照下面的要求填写相关的信息，再运行`python create_db.py`，
# 并将生成的数据库拷贝到 blog 目录下

import os
import sys
import os.path
import base64
import getopt
import sqlite3

from miniakio.libs import crypto

# 编辑下面的信息

USERNAME = "SErHo"             # 用户名
EMAIL = "serholiu@gmail.com"   # 邮箱，登陆的时候使用
PASSWORD = "123456"            # 登陆密码
DBFILE = "example/newblog.db"  # 数据库名称，请保持和 blog/config.py 中设置的名称相同


# 请不要改动下面的内容
def create_tables(db):
    pwd = os.path.dirname(os.path.realpath(__file__))
    schema = os.path.join(pwd, "example", "sqlite3.sql")
    c = db.cursor()
    with open(schema, encoding="utf-8") as f:
        c.executescript(f.read())

    db.commit()


def create_user(db):
    c = db.cursor()
    salt = crypto.get_random_string()
    enpass = crypto.PasswordCrypto.get_encrypted(PASSWORD)
    c.execute(
        "INSERT INTO users (salt, username, password, email) VALUES (?,?,?,?)",
        (salt, USERNAME, enpass, EMAIL)
    )
    db.commit()


def get_secret():
    return base64.b64encode(os.urandom(32)).decode("utf-8")


def main(argv):
    helps = """
Usage: python tools -o <opt>

    opt list:
    createdb      创建数据库并添加用户信息(请先填写相关信息)
    getsecret     随机生成一个 Cookie Secret
    """
    opt = ""
    try:
        opts, args = getopt.getopt(argv, "ho:", ["opt="])
    except getopt.GetoptError:
        print(helps)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(helps)
            sys.exit()
        elif opt in ("-o", "--opt"):
            opt = arg
        else:
            print(helps)
            sys.exit()

    if opt == "createdb":
        db = sqlite3.connect(DBFILE)
        print("开始创建数据库...")
        create_tables(db)
        print("数据库创建完毕，开始创建用户账户...")
        create_user(db)
        db.close()
        print("用户创建成功，请务必将生成的数据库文件拷贝到 blogconfig 中设置的目录里！！！")
    elif opt == "getsecret":
        print(get_secret())


if __name__ == '__main__':
    main(sys.argv[1:])
