#!/usr/bin/env python
# -*- coding: utf-8 -*-
##################################################
# 用于创建数据库，填好信息后，执行 `python create_db.py`
# 即可.
##################################################

import sqlite3
import crypto

################################################
###         你的信息以及数据库地址               ###
################################################

username = "SErHo"
email = "serholiu@gmail.com"
password = "123456"
db = r"/home/serho/blog.db"

#################################################

print "Start Create New SQLite3 DB ........"

conn = sqlite3.connect(db)
c = conn.cursor()

c.execute("""CREATE TABLE users (id INTEGER NOT NULL PRIMARY KEY,
             salt VARCHAR(12) NOT NULL, username VARCHAR(50) NOT NULL,
             password VARCHAR(255) NOT NULL, email VARCHAR(255) NOT NULL);
          """)
c.execute("""CREATE TABLE posts (id INTEGER NOT NULL PRIMARY KEY,
             title VARCHAR(100) NOT NULL, slug VARCHAR(100) NOT NULL,
             content TEXT NOT NULL, tags VARCHAR(255) NOT NULL,
             category VARCHAR(30) NOT NULL, published VARCHAR(30) NOT NULL);
          """)
c.execute("""CREATE TABLE tags (id INTEGER NOT NULL PRIMARY KEY,
             name VARCHAR(50) NOT NULL, post_id INTEGER NOT NULL);
          """)

c.execute("CREATE UNIQUE INDEX users_id ON users(id);")
c.execute("CREATE UNIQUE INDEX posts_id ON posts(id);")
c.execute("CREATE INDEX posts_slug ON posts(slug);")
c.execute("CREATE INDEX tags_name ON tags(name);")
c.execute("CREATE UNIQUE INDEX tags_id ON tags(id);")

print "Start Create User........."

salt = crypto.get_random_string()
enpass= crypto.hex_password(password)

c.execute("INSERT INTO users ( salt, username, password, email) VALUES (?,?,?,?)",
          (salt, username, enpass, email))

conn.commit()
conn.close()

print "DB Create.......!!"
