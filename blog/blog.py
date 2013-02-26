#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
#import tornado.gen
from tornado.web import removeslash, asynchronous
from tornado.httpclient import AsyncHTTPClient
from libs.log import access_log
from libs.handler import BaseHandler
from libs.crypto import is_password, get_random_string
from libs.models import PostMixin, TagMixin
from libs.markdown import render_post
from libs.utils import authenticated, loads_repos
from config import PICKY_DIR

class EntryHandler(BaseHandler, PostMixin):

    @removeslash
    def get(self, slug):
        post = self.get_post_by_slug(slug)
        if not post:
            self.abort(404)
        tags = [tag.strip() for tag in post.tags.split(",")]
        next_prev = self.get_next_prev_post(post.id)
        self.render("post.html", post=post, tags=tags, next_prev=next_prev)


class TagsHandler(BaseHandler, PostMixin):

    @removeslash
    def get(self, name):
        posts = self.get_posts_by_tag(name)
        if not posts:
            self.abort(404)
        count = len(posts)
        self.render("archive.html", posts=posts, type="tag",
                                    name=name, count=count)


class CategoryHandler(BaseHandler, PostMixin):

    @removeslash
    def get(self, category):
        posts = self.get_posts_by_category(category)
        if not posts:
            self.abort(404)
        count = len(posts)
        self.render("archive.html", posts=posts, type="category",
                                    name=category, count=count)

class FeedHandler(BaseHandler, PostMixin):

    def get(self):
        posts = self.get_count_posts(10)
        self.set_header("Content-Type", "application/atom+xml")
        self.render("feed.xml", posts=posts)


class SearchHandler(BaseHandler):

    def get(self):
        self.render("search.html")


class HomeHandler(BaseHandler, PostMixin):

    def get(self):
        posts = self.get_count_posts(5)
        self.render("index.html", posts=posts)
            

class ArchiveHandler(BaseHandler, PostMixin, TagMixin):

    def get(self):
        posts = self.get_count_posts()
        from libs.utils import archives_list
        count = len(posts)
        tags = self.get_all_tag_count(30)
        self.render('archives.html', posts=posts, count=count,
            archives_list=archives_list, tags=tags)


class TagListHandler(BaseHandler, TagMixin):

    def get(self):
        tags = self.get_all_tag_count()
        count = len(tags)
        self.render('taglist.html', tags=tags, count=count)
      

class NewPostHandler(BaseHandler, PostMixin):

    @authenticated
    def get(self):
        self.render("admin/post.html")

    @authenticated
    def post(self):
        markdown = self.get_argument("markdown", None)
        comment = self.get_argument("comment", 1)
        if not markdown:
            self.redirect("/post/new")
        p = render_post(markdown)
        if comment=='0':
            comment = 0
        post = {"title": p["meta"]["title"], "slug": p["meta"]["slug"],
                "tags": p["meta"]["tags"], "category": p["meta"]["category"],
                "published": p["meta"]["published"],
                "content": p["content"],"comment": comment}

        post_id = self.create_new_post(**post)
        self.redirect("/%s" % p["meta"]["slug"])
        return


class UpdatePostHandler(BaseHandler, PostMixin):

    @authenticated
    def get(self, id):
        post = self.get_post_by_id(int(id))
        if not post:
            self.redirect('/')
        self.render("admin/update.html", id=id)

    @authenticated
    def post(self, id):
        markdown = self.get_argument("markdown", None)
        comment = self.get_argument("comment", 1)
        print comment
        if not markdown:
            self.redirect("/post/update/%s" % str(id))
        if comment=='0':
            comment = 0
        p = render_post(markdown)
        post = {"title": p["meta"]["title"], "slug": p["meta"]["slug"],
                "tags": p["meta"]["tags"], "category": p["meta"]["category"],
                "published": p["meta"]["published"],
                "content": p["content"], "comment": comment}
        result = self.update_post_by_id(int(id), **post)
        self.redirect("/%s" % p["meta"]["slug"])
        return


class DeletePostHandler(BaseHandler, PostMixin):

    @authenticated
    def get(self, id):
        self.delete_post_by_id(int(id))
        self.redirect("/")
        return


class PickyHandler(BaseHandler):

    def get(self, slug):
        mdfile = PICKY_DIR + "/" + str(slug) + ".md"
        try:
            md = open(mdfile)
        except IOError:
            print "Not"
            self.abort(404)
        markdown = md.read()
        md.close()
        p = render_post(markdown)
        title = p["meta"]["title"]
        published = p["meta"]["published"]
        content = p["content"]
        self.render("picky.html", title=title, slug=slug,
                     published=published, content=content)


class PickyDownHandler(BaseHandler):

    def get(self, slug):
        mdfile = PICKY_DIR + "/" + str(slug)
        try:
            md = open(mdfile)
        except IOError:
            print "Not"
            self.abort(404)
        markdown = md.read()
        md.close()
        self.set_header("Content-Type", "text/x-markdown")
        self.write(markdown)


class NewPickyHandler(BaseHandler):

    @authenticated
    def get(self):
        self.render("admin/picky.html")

    @authenticated
    def post(self):
        files = self.request.files['picky'][0]
        if files['body'] and (files['filename'].split(".").pop().lower()=='md'):
            f = open(PICKY_DIR + '/' + files['filename'],'w')
            f.write(files['body'])
            f.close()
            slug = files['filename'].split('.')[0]
            self.redirect("/picky/%s" % slug)
        self.redirect('/post/picky')


class SigninHandler(BaseHandler):

    def get(self):
        if self.current_user:
            self.redirect(self.get_argument("next", "/"))
            return
        self.render("admin/signin.html")

    def post(self):
        email = self.get_argument("email", None)
        password = self.get_argument("password", None)
        if (not email) or (not password):
            self.redirect("/auth/signin")
            return
        pattern = r'^.+@[^.].*\.[a-z]{2,10}$'
        if isinstance(pattern, basestring):
            pattern = re.compile(pattern, flags=0)

        if not pattern.match(email):
            self.redirect("/auth/signin")
            return

        user = self.get_user_by_email(email)
        if not user:
            access_log.error("Login Error for email: %s!" % email)
            self.redirect("/")
            return
        enpass = user.password
        if is_password(password, enpass):
            token = user.salt + "/" + str(user.id)
            self.set_secure_cookie("token", str(token))
            self.redirect(self.get_argument("next", "/post/new"))
            return
        else:
            access_log.error("Login Error for password: %s!" % password)
            self.redirect("/")
        return


class SignoutHandler(BaseHandler):

    def get(self):
        user = self.current_user
        if not user:
            self.redirect("/")
        salt = get_random_string()
        is_ok = self.update_user_salt(user.id, salt)
        self.clear_cookie("token")
        self.redirect("/")


# class GithubHandler(BaseHandler):

#     @asynchronous
#     @tornado.gen.engine
#     def get(self):
#         http_client = AsyncHTTPClient()
#         response = yield tornado.gen.Task(http_client.fetch,
#             "https://api.github.com/users/SerhoLiu/repos?sort=updated")
#         #print response.body
#         repos = loads_repos(response.body)
#         self.render("github.html", repos=repos)


class PageNotFound(BaseHandler):
    def get(self):
        self.abort(404)


handlers = [('/', HomeHandler),
            ('/([a-zA-Z0-9-]+)/*', EntryHandler),
            #('/picky/repos', GithubHandler),
            ('/picky/([a-zA-Z0-9-]+)/*', PickyHandler),
            ('/picky/([a-zA-Z0-9-]+.md)', PickyDownHandler),
            ('/tag/([^/]+)/*', TagsHandler),
            ('/category/([^/]+)/*', CategoryHandler),
            ('/post/new', NewPostHandler),
            ('/post/delete/([0-9]+)', DeletePostHandler),
            ('/post/update/([0-9]+)', UpdatePostHandler),
            ('/post/picky', NewPickyHandler),
            ('/auth/signin', SigninHandler),
            ('/auth/signout', SignoutHandler),
            ('/blog/feed', FeedHandler),
            ('/search/all', SearchHandler),
            ('/blog/all', ArchiveHandler),
            ('/blog/tags', TagListHandler),
            (r'.*', PageNotFound), 
]
