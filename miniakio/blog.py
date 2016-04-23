#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import tqdm
import yaml
import shutil
import os.path
from jinja2 import Environment, FileSystemLoader

from miniakio.server import Server
from miniakio.models import Post, Picky
from miniakio.utils import ensure_dir_exists
from miniakio.utils import read_file, write_file, echo


class Blog:

    HomePosts = 8
    FeedPosts = 10

    def __init__(self, config):
        """
        :param config: path of config
        """
        config_path = os.path.abspath(os.path.expanduser(config))
        self.basedir = os.path.dirname(config_path)
        self.config = yaml.load(read_file(config_path))

        self._site_dir = self._config_item_path("sites")
        self._page_dir = os.path.join(self._site_dir, "blog")
        ensure_dir_exists(self._page_dir)

        self._jinja = self._init_jinja()

    def _init_jinja(self):
        theme_dir = self._config_item_path("themes")
        jinja = Environment(
            loader=FileSystemLoader(theme_dir),
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=False,
        )

        jinja.globals.update({"config": self.config})

        return jinja

    def _config_item_path(self, name):
        defalut_dir = os.path.join(self.basedir, name)
        path = self.config.get(name, defalut_dir)

        return os.path.expanduser(path)

    def _parse_posts(self):
        index = {}
        posts = []
        tags = {}

        post_dir = self._config_item_path("posts")
        for md in tqdm.tqdm(glob.glob(os.path.join(post_dir, "*.md"))):
            markdown = read_file(md)
            try:
                post = Post(markdown)
            except Exception as e:
                raise Exception("parse '%s', %s" % (md, e)) from None

            if post.slug in index:
                raise Exception("post %s and %s slug duplicate" % (
                    index[post.slug], md
                ))

            index[post.slug] = md
            posts.append(post)

            for tag in post.tags:
                if tag in tags:
                    tags[tag].append(post)
                else:
                    tags[tag] = [post]

        posts.sort(key=lambda p: p.published, reverse=True)

        return posts, tags

    def _parse_pickys(self):
        pickys = []
        picky_dir = self._config_item_path("pickys")
        for md in tqdm.tqdm(glob.glob(os.path.join(picky_dir, "*.md"))):
            basename = os.path.basename(md)
            slug = basename.split(".")[0]
            markdown = read_file(md)
            try:
                picky = Picky(str(slug), markdown)
            except Exception as e:
                raise Exception("parse '%s', %s" % (md, e)) from None

            pickys.append(picky)

        return pickys

    def _build_posts(self, posts):
        """
        :type posts: list[Post]
        """
        output_dir = self._site_dir
        template = self._jinja.get_template("post.html")

        count = len(posts)
        tq = tqdm.tqdm(total=count)
        for i, post in enumerate(posts):
            post.prev = None if i < 1 else posts[i - 1]
            post.next = None if i > count - 2 else posts[i + 1]
            html = template.render(post=post)
            filepath = os.path.join(output_dir, "%s.html" % post.slug)
            write_file(filepath, html)
            tq.update(1)
        tq.close()

        # archives
        template = self._jinja.get_template("archives.html")
        archives = {}
        for post in posts:
            year = post.published.year
            if year in archives:
                archives[year].append(post)
            else:
                archives[year] = [post]

        archives = sorted(
            archives.items(), key=lambda item: item[0], reverse=True
        )
        html = template.render(count=count, archives=archives)
        filepath = os.path.join(self._page_dir, "all.html")
        write_file(filepath, html)

    def _build_pickys(self, pickys):
        output_dir = os.path.join(self._site_dir, "picky")
        ensure_dir_exists(output_dir)
        template = self._jinja.get_template("picky.html")

        for picky in tqdm.tqdm(pickys):
            html = template.render(picky=picky)
            filepath = os.path.join(output_dir, "%s.html" % picky.slug)
            write_file(filepath, html)

    def _build_tags(self, tags):
        """
        :type tags: dict[unicode, list[Post]]
        """
        output_dir = os.path.join(self._site_dir, "tag")
        ensure_dir_exists(output_dir)
        template = self._jinja.get_template("tag.html")

        taglist = {}
        tq = tqdm.tqdm(total=len(tags))
        for tag, posts in tags.items():
            taglist[tag] = len(posts)
            posts.sort(key=lambda p: p.published, reverse=True)
            html = template.render(name=tag, posts=posts)
            filepath = os.path.join(output_dir, "%s.html" % tag)
            write_file(filepath, html)
            tq.update(1)
        tq.close()

        # taglist
        taglist = sorted(
            taglist.items(), key=lambda item: item[1], reverse=True
        )
        template = self._jinja.get_template("taglist.html")
        html = template.render(tags=taglist)
        filepath = os.path.join(self._page_dir, "tags.html")
        write_file(filepath, html)

    def _build_assets(self):
        asset_dir = self._config_item_path("assets")
        dst_dir = os.path.join(self._site_dir, "assets")
        if os.path.exists(dst_dir) and os.path.isdir(dst_dir):
            shutil.rmtree(dst_dir)
        shutil.copytree(asset_dir, dst_dir)

    def build(self):
        echo.info("start, output to %s", self._site_dir)
        self._build_assets()

        echo.info("parsing pickys...")
        pickys = self._parse_pickys()
        echo.info("parsing posts...")
        posts, tags = self._parse_posts()

        echo.info("building pickys...")
        self._build_pickys(pickys)
        echo.info("building posts...")
        self._build_posts(posts)
        echo.info("building tags...")
        self._build_tags(tags)

        # home
        echo.info("building index...")
        template = self._jinja.get_template("home.html")
        html = template.render(posts=posts[:self.HomePosts])
        write_file(os.path.join(self._site_dir, "index.html"), html)

        # feed
        echo.info("building feed...")
        template = self._jinja.get_template("feed.xml")
        xml = template.render(posts=posts[:self.FeedPosts])
        write_file(os.path.join(self._page_dir, "feed.xml"), xml)

        # 404
        echo.info("building 404...")
        template = self._jinja.get_template("e404.html")
        html = template.render()
        write_file(os.path.join(self._page_dir, "e404.html"), html)

    def server(self, port=8000):
        Server(self._site_dir).serve_forever(port=port)
