#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .utils import ObjectDict


class UserMixin(object):

    def get_user_by_id(self, uid):
        return self.db.get("SELECT * FROM users WHERE id = ?", uid)

    def get_user_by_email(self, email):
        return self.db.get("SELECT * FROM users WHERE email = ?", email)

    def update_user_salt(self, uid, salt):
        self.db.execute("UPDATE users SET salt=? WHERE id=?;", salt, uid)


class PostMixin(object):

    def get_post_by_id(self, pid):
        return self.db.get("SELECT * FROM posts WHERE id = ?", pid)

    def get_post_by_slug(self, slug):
        return self.db.get("SELECT * FROM posts WHERE slug = ?", slug)

    def get_posts_by_tag(self, tag):
        sql = """SELECT p.slug, p.title, p.published FROM posts AS p
                 INNER JOIN tags AS t
                 ON p.id = t.post_id
                 WHERE t.name = ?
                 ORDER BY p.published DESC;
              """

        return self.db.query(sql, tag)

    def get_posts_by_category(self, category):
        sql = """SELECT slug, title, published FROM posts
                 WHERE category = ?
                 ORDER BY published DESC;
              """

        return self.db.query(sql, category)

    def get_count_posts(self, count=None):
        if count:
            sql = "SELECT * FROM posts ORDER BY published DESC LIMIT ?;"
            posts = self.db.query(sql, count)
        else:
            sql = """SELECT slug, title, published
                     FROM posts ORDER BY published DESC;
                  """
            posts = self.db.query(sql)

        return posts

    def create_new_post(self, post):
        while True:
            p = self.get_post_by_slug(post["slug"])
            if not p:
                break
            post["slug"] += "-2"

        sql = """INSERT INTO posts (title, slug, content, tags,
                 category, published, comment, cover)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?);
              """

        with self.db as db:
            pid = db.execute(
                sql,
                post["title"], post["slug"], post["content"],
                post["tags"], post["category"], post["published"],
                post["comment"], post.get("cover")
            )
            db.executemany(
                "INSERT INTO tags (name, post_id) VALUES (?, ?);",
                [(tag.strip(), pid) for tag in post["tags"].split(",")]
            )

        return pid

    def update_post_by_id(self, pid, post):
        sql = """UPDATE posts
                 SET title=?, slug=?, content=?, tags=?,
                 category=?, published=?, comment=?, cover=?
                 WHERE id=?;
              """

        p = self.get_post_by_id(pid)

        with self.db as db:
            db.execute(
                sql,
                post["title"], post["slug"], post["content"],
                post["tags"], post["category"], post["published"],
                post["comment"], post.get("cover"),
                pid
            )

            if p.tags == post["tags"]:
                return

            db.execute("DELETE FROM tags WHERE post_id=?;", pid)
            db.executemany(
                "INSERT INTO tags (name, post_id) VALUES (?, ?);",
                [(tag.strip(), pid) for tag in post["tags"].split(",")]
            )

    def delete_post_by_id(self, pid):
        with self.db as db:
            db.execute("DELETE FROM posts WHERE id=?;", pid)
            db.execute("DELETE FROM tags WHERE post_id=?;", pid)

    def get_next_prev_post(self, published):
        next_sql = """SELECT slug, title FROM posts
                      WHERE published > ? ORDER BY published ASC LIMIT 1;
                   """

        prev_sql = """SELECT slug, title FROM posts
                      WHERE published < ? ORDER BY published DESC LIMIT 1;
                   """

        return ObjectDict(dict(
            next=self.db.get(next_sql, published),
            prev=self.db.get(prev_sql, published)
        ))


class TagMixin(object):

    def get_all_tag_count(self, number=None):
        if number:
            sql = """SELECT name, COUNT(name) AS num FROM tags
                     GROUP BY name ORDER BY num DESC LIMIT ?;
                  """
            tags = self.db.query(sql, number)
        else:
            sql = """SELECT name, COUNT(name) AS num FROM tags
                     GROUP BY name ORDER BY num DESC;
                  """
            tags = self.db.query(sql)

        return tags
