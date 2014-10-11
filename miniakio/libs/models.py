#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pika

class UserMixin(object):

    def get_user_by_id(self, id):
        user = self.db.get("SELECT * FROM users WHERE id = ?", int(id))
        return user

    def get_user_by_email(self, email):
        user = self.db.get("SELECT * FROM users WHERE email = ?", email)
        return user

    def update_user_salt(self, id, salt):
        user = self.get_user_by_id(id)
        if not user:
            return False
        self.db.execute("UPDATE users SET salt=? WHERE id=?;", salt, id)
        return True


class PostMixin(object):

    def get_post_by_id(self, id):
        post = self.db.get("SELECT * FROM posts WHERE id = ?", id)
        return post

    def get_posts_by_tag(self, tag):
        sql = """SELECT p.id, p.title, p.published FROM posts AS p 
                   INNER JOIN tags AS t 
                   ON p.id = t.post_id 
                   WHERE t.name = ? 
                   ORDER BY p.published desc;
              """
        posts = self.db.query(sql, tag)
        return posts

    def get_category_list(self):
        sql = """SELECT DISTINCT category FROM posts 
                 ORDER BY category ASC;
              """
        categoryList = self.db.query(sql)
        return categoryList

    def get_posts_by_category(self, category):
        sql = """SELECT id, published, title FROM posts
                 WHERE category = ?
                 ORDER BY published desc;
              """
        posts = self.db.query(sql, category)
        return posts

    def get_count_posts(self, count=None):
        if count:
            posts = self.db.query("SELECT * FROM posts ORDER BY published "
                                "DESC LIMIT ?;",count)
        else:
            posts = self.db.query("SELECT id,title,published FROM posts ORDER BY published DESC;")
        return posts

    def create_new_post(self, **post):
        sql = """INSERT INTO posts (title,content,tags,category,published,comment,markdown)
                 VALUES (?,?,?,?,?,?,?);
              """
        post_id = self.db.execute(sql, post["title"], post["content"],
                              post["tags"], post["category"], post["published"], post['comment'], post['markdown'])
        if post_id:
            tags = [tag.strip() for tag in post["tags"].split(",")]
            for tag in tags:
                self.db.execute("INSERT INTO tags (name,post_id) VALUES (?,?);", tag, post_id)
        return post_id

    def update_post_by_id(self, id, **post):
        sql = """UPDATE posts SET title=?,content=?,tags=?,category=?,
                 published=?,comment=?,markdown=? WHERE id=?;
              """
        p = self.get_post_by_id(id)
        if p.tags != post["tags"]:
            has_new_tag = True
        else:
            has_new_tag = False
        self.db.execute(sql, post["title"], post["content"],
                     post["tags"], post["category"], post["published"],
                     post['comment'], post['markdown'], id)
        if has_new_tag:
            new_tags = [tag.strip() for tag in post["tags"].split(",")]
            self.db.execute("DELETE FROM tags WHERE post_id=?;", id)
            for tag in new_tags:
                self.db.execute("INSERT INTO tags (name,post_id) VALUES (?,?);", tag, id)
        return True

    def delete_post_by_id(self, id):
        self.db.execute("DELETE FROM posts WHERE id=?;", id)
        self.db.execute("DELETE FROM tags WHERE post_id=?;", id)
        return True


    def get_next_prev_post(self, published):
        next_post = self.db.get(
          "SELECT id,title FROM posts WHERE published > ? ORDER BY published ASC LIMIT 1;",
          published)

        prev_post = self.db.get(
          "SELECT id,title FROM posts WHERE published < ? ORDER BY published DESC LIMIT 1;",
          published)

        return {"next": next_post, "prev": prev_post}

    def send_post_change_nofity(self, post_id):
      QUEUE_NAME = 'PostChange'
      msg_content = post_id
      connection = pika.BlockingConnection(pika.ConnectionParameters(
              host='localhost'))
      channel = connection.channel()

      channel.queue_declare(queue=QUEUE_NAME)

      channel.basic_publish(exchange='',
                            routing_key=QUEUE_NAME,
                            body=msg_content)
      print '[x] Sent nofity for post id[%s]' % post_id
      connection.close()

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
