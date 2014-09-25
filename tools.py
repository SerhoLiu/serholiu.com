#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 用于创建数据库，请按照下面的要求填写相关的信息，再运行`python create_db.py`，
# 并将生成的数据库拷贝到 blog 目录下
import os
import sys
import getopt
import sqlite3
from miniakio.libs import crypto

# 编辑下面的信息

USERNAME = "cheyo"                  # 用户名
EMAIL = "icheyo@gmail.com"        # 邮箱，登陆的时候使用
PASSWORD = "123456"                 # 登陆密码
DBFILE = "example/newblog.db"               # 数据库名称，请保持和 blog/config.py 中设置的名称相同

# 请不要改动下面的内容


def create_db(conn):
    c = conn.cursor()
    c.execute("""
        CREATE TABLE users (id INTEGER NOT NULL PRIMARY KEY,
        salt VARCHAR(12) NOT NULL, username VARCHAR(50) NOT NULL,
        password VARCHAR(255) NOT NULL, email VARCHAR(255) NOT NULL);
        """)
    c.execute("""
        CREATE TABLE posts (id INTEGER NOT NULL PRIMARY KEY,
        title VARCHAR(100) NOT NULL, slug VARCHAR(100) NOT NULL,
        content TEXT NOT NULL, tags VARCHAR(255) NOT NULL,
        category VARCHAR(30) NOT NULL, published VARCHAR(30) NOT NULL,
        comment INTEGER NOT NULL);
        """)
    c.execute("""
        CREATE TABLE tags (id INTEGER NOT NULL PRIMARY KEY,
        name VARCHAR(50) NOT NULL, post_id INTEGER NOT NULL);
        """)

    c.execute("CREATE UNIQUE INDEX users_id ON users(id);")
    c.execute("CREATE UNIQUE INDEX posts_id ON posts(id);")
    c.execute("CREATE INDEX posts_slug ON posts(slug);")
    c.execute("CREATE INDEX tags_name ON tags(name);")
    c.execute("CREATE UNIQUE INDEX tags_id ON tags(id);")
    conn.commit()


def create_user(conn):
    c = conn.cursor()
    salt = crypto.get_random_string()
    enpass = crypto.PasswordCrypto.get_encrypted(PASSWORD)
    c.execute("""
        INSERT INTO users ( salt, username, password, email) VALUES (?,?,?,?)
        """, (salt, USERNAME, enpass, EMAIL))
    conn.commit()


def get_secret():
    return os.urandom(32).encode("base64")


def main(argv):
    help = """
Usage: python tools -o <opt>
    
    opt list:
    createdb      创建数据库并添加用户信息(请先填写相关信息)
    getsecret     随机生成一个 Cookie Secret
    """ 
    opt = ""
    try:
        opts, args = getopt.getopt(argv,"ho:",["opt="])
    except getopt.GetoptError:
        print help
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print help
            sys.exit()
        elif opt in ("-o", "--opt"):
            opt = arg
    
    if opt == "createdb":
        conn = sqlite3.connect(DBFILE)
        print "开始创建数据库..."
        create_db(conn)
        print "数据库创建完毕，开始创建用户账户..."
        create_user(conn)
        conn.close()
        print "用户创建成功，请务必将生成的数据库文件拷贝到 blogconfig 中设置的目录里！！！"
    elif opt == "getsecret":
        print get_secret() 


if __name__ == '__main__':
    main(sys.argv[1:])
