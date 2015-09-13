#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import os.path
from tornado.web import removeslash
from tornado.log import access_log

from .libs.handler import BaseHandler
from .libs.crypto import PasswordCrypto, get_random_string
from .libs.models import PostMixin, TagMixin
from .libs.markdown import RenderMarkdownPost
from .libs.utils import ObjectDict
from .libs.utils import authenticated, get_time_year
from .libs.utils import signer_encode, signer_check


class HomeHandler(BaseHandler, PostMixin):

    def get(self):
        if self.context.is_mobile:
            posts = self.get_count_posts(1)
            self.render("index.html", posts=posts)
        else:
            posts = self.get_count_posts(8)
            self.render("home.html", posts=posts)


class PostHandler(BaseHandler, PostMixin):

    @removeslash
    def get(self, slug):
        post = self.get_post_by_slug(slug.lower())
        if not post:
            self.abort(404)
        tags = [tag.strip() for tag in post.tags.split(",")]
        pager = self.get_next_prev_post(post.published)
        signer = signer_encode(self.config.secret, str(post.id))
        self.render(
            "post.html",
            post=post,
            tags=tags,
            pager=pager,
            signer=signer
        )


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

        render = RenderMarkdownPost(markdown)
        post = render.get_render_post()
        post.update({"comment": 0 if comment == "0" else 1})
        self.create_new_post(post)

        self.redirect("/%s" % post["slug"])


class UpdatePostHandler(BaseHandler, PostMixin):

    @authenticated
    def get(self, pid):
        post = self.get_post_by_id(int(pid))
        if not post:
            self.redirect("/")
        self.render("admin/update.html", pid=pid)

    @authenticated
    def post(self, pid):
        markdown = self.get_argument("markdown", None)
        comment = self.get_argument("comment", 1)
        if not markdown:
            self.redirect("/post/update/%s" % pid)

        render = RenderMarkdownPost(markdown)
        post = render.get_render_post()
        post.update({"comment": 0 if comment == "0" else 1})
        self.update_post_by_id(pid, post)

        self.redirect("/%s" % post["slug"])


class DeletePostHandler(BaseHandler, PostMixin):

    @authenticated
    def get(self, pid):
        signer = self.get_argument("check", None)
        if signer_check(self.config.secret, signer, pid):
            self.delete_post_by_id(int(pid))
        self.redirect("/")


class PickyHandler(BaseHandler):

    @removeslash
    def get(self, slug):
        mdfile = os.path.join(self.config.picky, slug + ".md")
        try:
            md = open(mdfile, "r", encoding="utf-8")
        except IOError:
            self.abort(404)

        markdown = md.read()
        md.close()
        render = RenderMarkdownPost(markdown)

        picky = ObjectDict(render.get_render_post())
        picky.slug = slug
        signer = signer_encode(self.config.secret, slug)

        self.render("picky.html", picky=picky, signer=signer)


class PickyDownHandler(BaseHandler):

    def get(self, slug):
        mdfile = os.path.join(self.config.picky, slug)
        try:
            md = open(mdfile, "r", encoding="utf-8")
        except IOError:
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
        try:
            files = self.request.files["picky"][0]
        except KeyError:
            self.redirect("/post/picky")
            return

        ext = files["filename"].split(".").pop().lower()
        if files["body"] and (ext == "md"):
            f = open(os.path.join(self.config.picky, files['filename']), 'wb')
            f.write(files['body'])
            f.close()

            slug = files["filename"].split(".")[0]
            self.redirect("/picky/%s" % slug)
            return

        self.redirect("/post/picky")


class DeletePickyHandler(BaseHandler):

    @authenticated
    def get(self, slug):
        signer = self.get_argument("check", None)
        if not signer_check(self.config.secret, signer, slug):
            self.redirect("/picky/%s" % slug)
            return

        mdfile = os.path.join(self.config.picky, slug + ".md")
        os.remove(mdfile)
        self.redirect("/")


class TagsHandler(BaseHandler, PostMixin):

    @removeslash
    def get(self, name):
        posts = self.get_posts_by_tag(name)
        if not posts:
            self.abort(404)
        count = len(posts)
        self.render(
            "archive.html",
            posts=posts,
            type="tag",
            name=name,
            count=count
        )


class CategoryHandler(BaseHandler, PostMixin):

    @removeslash
    def get(self, category):
        posts = self.get_posts_by_category(category)
        if not posts:
            self.abort(404)
        count = len(posts)
        self.render(
            "archive.html",
            posts=posts,
            type="category",
            name=category,
            count=count
        )


class FeedHandler(BaseHandler, PostMixin):

    def get(self):
        posts = self.get_count_posts(10)
        self.set_header("Content-Type", "application/atom+xml")
        self.render("feed.xml", posts=posts)


class ArchiveHandler(BaseHandler, PostMixin, TagMixin):

    def get(self):
        posts = self.get_count_posts()
        count = len(posts)
        archives = {}

        for post in posts:
            year = get_time_year(post.published)
            if year in archives:
                archives[year].append(post)
            else:
                archives[year] = [post]

        archives = sorted(
            archives.items(),
            key=lambda item: item[0],
            reverse=True
        )

        self.render(
            "archives.html",
            count=count,
            archives=archives
        )


class TagListHandler(BaseHandler, TagMixin):

    def get(self):
        tags = self.get_all_tag_count()
        count = len(tags)
        self.render("taglist.html", tags=tags, count=count)


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

        pattern = r"^.+@[^.].*\.[a-z]{2,10}$"
        if isinstance(pattern, str):
            pattern = re.compile(pattern, flags=0)

        if not pattern.match(email):
            self.redirect("/auth/signin")
            return

        user = self.get_user_by_email(email)
        if not user:
            access_log.error("Login Error for email: %s" % email)
            self.redirect("/")
            return

        encryped_pass = user.password
        if PasswordCrypto.authenticate(password, encryped_pass):
            token = user.salt + "/" + str(user.id)
            self.set_secure_cookie("token", token)
            self.redirect(self.get_argument("next", "/post/new"))
        else:
            access_log.error("Login Error for password: %s!" % password)
            self.redirect("/")


class SignoutHandler(BaseHandler):

    def get(self):
        user = self.current_user
        if not user:
            self.redirect("/")
            return
        salt = get_random_string()
        self.update_user_salt(user.id, salt)
        self.clear_cookie("token")
        self.redirect("/")


class PageNotFound(BaseHandler):

    def get(self):
        self.abort(404)


handlers = [
    (r"/", HomeHandler),
    (r"/([a-zA-Z0-9-]+)/*", PostHandler),
    (r"/picky/([a-zA-Z0-9-]+)/*", PickyHandler),
    (r"/picky/([a-zA-Z0-9-]+.md)", PickyDownHandler),
    (r"/tag/([^/]+)/*", TagsHandler),
    (r"/category/([^/]+)/*", CategoryHandler),
    (r"/post/new", NewPostHandler),
    (r"/post/delete/([0-9]+)", DeletePostHandler),
    (r"/post/update/([0-9]+)", UpdatePostHandler),
    (r"/post/picky", NewPickyHandler),
    (r"/picky/delete/([a-zA-Z0-9-]+)", DeletePickyHandler),
    (r"/auth/signin", SigninHandler),
    (r"/auth/signout", SignoutHandler),
    (r"/blog/feed", FeedHandler),
    (r"/blog/all", ArchiveHandler),
    (r"/blog/tags", TagListHandler),
    (r".*", PageNotFound),
]
