#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 用于创建数据库，请按照下面的要求填写相关的信息，再运行`python create_db.py`，
# 并将生成的数据库拷贝到 blog 目录下

import sqlite3
import crypto

# 编辑下面的信息

USERNAME = "SErHo"                  # 用户名
EMAIL = "serholiu@gmail.com"        # 邮箱，登陆的时候使用
PASSWORD = "123456"                 # 登陆密码
DBFILE = "newblog.db"               # 数据库名称，请保持和 blog/config.py 中设置的名称相同

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
        category VARCHAR(30) NOT NULL, published VARCHAR(30) NOT NULL);
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
    enpass = crypto.hex_password(PASSWORD)
    c.execute("""
        INSERT INTO users ( salt, username, password, email) VALUES (?,?,?,?)
        """, (salt, USERNAME, enpass, EMAIL))
    conn.commit()


if __name__ == '__main__':
    conn = sqlite3.connect(DBFILE)

    print "开始创建数据库..."
    create_db(conn)

    print "数据库创建完毕，开始创建用户账户..."
    create_user(conn)
    conn.close()

    print "用户创建成功，请务必将生成的数据库文件拷贝到 blog 目录下！！！"
