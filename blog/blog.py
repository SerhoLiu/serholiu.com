#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.web import removeslash, authenticated
from libs.handler import BaseHandler
from libs.crypto import hex_password, is_password, get_random_string
from libs.models import PostMixin
from libs.markdown import render_post
from libs.utils import ObjectDict
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
        posts = self.get_count_posts(10,True)
        self.set_header("Content-Type", "application/atom+xml")
        self.render("feed.xml", posts=posts)


class SearchHandler(BaseHandler):

    def get(self):
        self.render("search.html")


class HomeHandler(BaseHandler, PostMixin):

    def get(self):
        posts = self.get_count_posts(10)
        self.render("index.html", posts=posts)


class ArchiveHandler(BaseHandler, PostMixin):

    def get(self):
        posts = self.get_count_posts()
        from libs.utils import archives_list
        count = len(posts)
        self.render('archives.html', posts=posts, count=count, archives_list=archives_list)
      

class NewPostHandler(BaseHandler, PostMixin):

    @authenticated
    def get(self):
        self.render("admin/new.html")

    @authenticated
    def post(self):
        markdown = self.get_argument("markdown", None)
        if not markdown:
            self.redirect("/post/new")
        p = render_post(markdown)
        post = {"title": p["meta"]["title"], "slug": p["meta"]["slug"],
                "tags": p["meta"]["tags"], "category": p["meta"]["category"],
                "published": p["meta"]["published"], "content": p["content"]}

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
        if not markdown:
            self.redirect("/post/update/%s" % str(id))
        p = render_post(markdown)
        post = {"title": p["meta"]["title"], "slug": p["meta"]["slug"],
                "tags": p["meta"]["tags"], "category": p["meta"]["category"],
                "published": p["meta"]["published"], "content": p["content"]}
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
        tpl = PICKY_DIR + "/" + str(slug) + ".html"
        self.render(tpl)


class NewPickyHandler(BaseHandler):

    @authenticated
    def get(self):
        self.render("admin/new.html")

    @authenticated
    def post(self):
        markdown = self.get_argument("markdown", None)
        if not markdown:
            self.redirect("/picky/new")
        p = render_post(markdown)
        title = p["meta"]["title"]
        slug = p["meta"]["slug"]
        published = p["meta"]["published"]
        content = p["content"]
        html = self.render_string("picky.html", title=title, slug=slug,
                               published=published, content=content)
        self._create_html(html, slug)
        self.redirect("/picky/%s" % slug)
        return
    
    def _create_html(self, html, slug):
        fpath = PICKY_DIR + "/" + str(slug) + ".html"
        f = open(fpath, "w")
        f.write(html)
        f.close()


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
        import re
        pattern = r'^.+@[^.].*\.[a-z]{2,10}$'
        if isinstance(pattern, basestring):
            pattern = re.compile(pattern, flags=0)

        if not pattern.match(email):
            self.redirect("/auth/signin")
            return

        user = self.get_user_by_email(email)
        if not user:
            self.redirect("/")
            return
        enpass = user.password
        if is_password(password, enpass):
            token = user.salt + "/" + str(user.id)
            self.set_secure_cookie("token", str(token))
            self.redirect(self.get_argument("next", "/post/new"))
            return
        else:
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

class PageNotFound(BaseHandler):
    def get(self):
        self.abort(404)


handlers = [('/', HomeHandler),
            ('/([a-zA-Z0-9-]+)/*', EntryHandler),
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
            (r'.*', PageNotFound), 
]
