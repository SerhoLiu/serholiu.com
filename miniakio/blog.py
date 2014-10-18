#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from tornado.web import removeslash
from tornado.log import access_log
from .libs.handler import BaseHandler
from .libs.crypto import PasswordCrypto, get_random_string
from .libs.models import PostMixin, TagMixin
from .libs.markdown import RenderMarkdownPost
from .libs.utils import authenticated, signer_code
from .libs.utils import unsigner_code, archive_list
from blogconfig import PICKY_DIR


class EntryHandler(BaseHandler, PostMixin):

    @removeslash
    def get(self, post_id):
        post = self.get_post_by_id(post_id)
        if not post:
            self.abort(404)
        tags = [tag.strip() for tag in post.tags.split(",")]
        next_prev = self.get_next_prev_post(post.published)
        signer = signer_code(str(post.id))
        self.render("post.html", post=post, tags=tags, next_prev=next_prev,
                                    signer=signer)


class TagsHandler(BaseHandler, PostMixin):

    @removeslash
    def get(self, name):
        posts = self.get_posts_by_tag(name)
        if not posts:
            self.abort(404)
        count = len(posts)
        self.render("category.html", posts=posts, type="tag", name=name,
            count=count)

class CategoryHandler(BaseHandler, PostMixin):


    @removeslash
    def get(self, category):
        posts = self.get_posts_by_category(category)
        if not posts:
            self.abort(404)
        count = len(posts)
        self.render("category.html", posts=posts, type="category",
                                    name=category, count=count)

class CategoriesHandler(BaseHandler, PostMixin):

    @removeslash
    def get(self):
        dictCatePosts = {}
        postsCount = 0
        categoryList = self.get_category_list()

        # if not categoryList:
        #    self.abort(404)

        for categoryRow in categoryList:
            postsCurrCategory = self.get_posts_by_category(categoryRow.category)
            dictCatePosts[categoryRow.category] = postsCurrCategory
            postsCount += len(postsCurrCategory)

        self.render("categories.html", dictCatePosts=dictCatePosts, count=postsCount)

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
        if self._context.is_mobile:
            posts = self.get_count_posts(5)
            self.render("index.html", posts=posts)
        else:
            posts = self.get_count_posts(8)
            self.render("home.html", posts=posts)
            

class ArchiveHandler(BaseHandler, PostMixin, TagMixin):

    def get(self):
        posts = self.get_count_posts()
        count = len(posts)
        self.render('archive.html', posts=posts, count=count,
            archive_list=archive_list)


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

        render = RenderMarkdownPost(markdown)
        post = render.get_render_post()
        if comment == '0':
            comment = 0
        post.update({"comment": comment})
        post.update({"markdown": markdown})
        new_post_id = self.create_new_post(**post)
        self.redirect("/%s.html" % new_post_id)
        return


class UpdatePostHandler(BaseHandler, PostMixin):

    @authenticated
    def get(self, id):
        post = self.get_post_by_id(int(id))
        if not post:
            self.redirect('/')
        self.render("admin/update.html", id=id, markdown=post['markdown'])

    @authenticated
    def post(self, id):
        markdown = self.get_argument("markdown", None)
        comment = self.get_argument("comment", 1)
        print comment
        if not markdown:
            self.redirect("/post/update/%s" % str(id))

        self.send_post_change_nofity(id)

        render = RenderMarkdownPost(markdown)
        post = render.get_render_post()

        if comment == '0':
            comment = 0

        post.update({"comment": comment})
        post.update({"markdown": markdown})
        self.update_post_by_id(int(id), **post)
        self.redirect("/%s.html" % id)
        return


class DeletePostHandler(BaseHandler, PostMixin):

    @authenticated
    def get(self, id):
        signer = self.get_argument("check", None)
        print signer
        if unsigner_code(signer) == id:
            self.delete_post_by_id(int(id))
        self.redirect("/")
        return


class PickyHandler(BaseHandler):

    def get(self, slug):
        mdfile = PICKY_DIR + "/" + str(slug) + ".md"
        try:
            md = open(mdfile)
        except IOError:
            self.abort(404)
        markdown = md.read()
        md.close()
        render = RenderMarkdownPost(markdown)
        post = render.get_render_post()
        self.render("picky.html", post=post, slug=slug)


class PickyDownHandler(BaseHandler):

    def get(self, slug):
        mdfile = PICKY_DIR + "/" + str(slug)
        try:
            md = open(mdfile)
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
            files = self.request.files['picky'][0]
        except KeyError:
            self.redirect('/post/picky')
            return
        
        if files['body'] and (files['filename'].split(".").pop().lower()=='md'):
            f = open(PICKY_DIR + '/' + files['filename'], 'w')
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
            access_log.error("Login Error for email: %s" % email)
            self.redirect("/")
            return
        encryped_pass = user.password
        if PasswordCrypto.authenticate(password, encryped_pass):
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
        self.update_user_salt(user.id, salt)
        self.clear_cookie("token")
        self.redirect("/")


class PageNotFound(BaseHandler):
    def get(self):
        self.abort(404)


handlers = [('/', HomeHandler),
            ('/([0-9]+).html/*', EntryHandler),
            ('/picky/([a-zA-Z0-9-]+)/*', PickyHandler),
            ('/picky/([a-zA-Z0-9-]+.md)', PickyDownHandler),
            ('/tag/([^/]+).html*', TagsHandler),
            ('/blog/category/([^/]+).html*', CategoryHandler),
            ('/post/new', NewPostHandler),
            ('/post/delete/([0-9]+)', DeletePostHandler),
            ('/post/update/([0-9]+)', UpdatePostHandler),
            ('/post/picky', NewPickyHandler),
            ('/auth/signin', SigninHandler),
            ('/auth/signout', SignoutHandler),
            ('/blog/feed', FeedHandler),
            ('/search/all', SearchHandler),
            ('/blog/archive.html', ArchiveHandler),
            ('/blog/tags.html', TagListHandler),
            ('/blog/categories.html', CategoriesHandler),
            (r'.*', PageNotFound),
]
