# -*- coding: utf-8 -*-

import re
from miniakio.utils import StringTime
from miniakio.markdown import render_markdown


class BasePost:
    """
    post like:

    # Hello

    - slug: hello-world
    - tags: T, A

    ---

    this content
    """

    def __init__(self, markdown):
        """
        :type markdown: str
        """
        header, body = re.split(r"\n-{3,}", markdown, 1)
        self._meta = self._get_meta(header)
        self.title = self._meta["title"]
        self.published = StringTime(self._meta["published"])
        self.cover = self._meta.get("cover")
        self.gallery = self._meta.get("gallery", "false").lower() in (
            "1",
            "true",
            "yes"
        )
        self.markdown = body

        self.content = render_markdown(body)

    @staticmethod
    def _get_meta(header):
        header = render_markdown(header, meta=True)
        title = re.findall(r"<h1>(.*)</h1>", header)[0]

        meta = {"title": title.strip()}
        items = re.findall(r"<li>(.*?)</li>", header, re.S)
        for item in items:
            key, value = item.split(":", 1)
            meta[key.strip()] = value.strip()

        return meta


class Post(BasePost):

    def __init__(self, markdown):
        """
        :type markdown: str
        """
        super(Post, self).__init__(markdown)

        self.slug = self._meta["slug"]
        self.tags = [tag.strip() for tag in self._meta["tags"].split(",")]
        self.comment = self._meta.get("comment")

        # pager
        self.prev = self.next = None


class Picky(BasePost):

    def __init__(self, slug, markdown):
        """
        :type slug: str
        :type markdown: str
        """
        super(Picky, self).__init__(markdown)

        self.slug = slug


class Photo:

    _SUPPORT_IMAGES = (1, 2, 3, 4, 6, 8)

    def __init__(self, config):
        self.title = config["title"]
        self.location = config["location"]
        self.published = StringTime(config["published"])
        self.images = config["images"]

        if len(self.images) not in self._SUPPORT_IMAGES:
            raise Exception(
                f"the number images must is {self._SUPPORT_IMAGES}"
            )
        self.full = config.get("full", False) and len(self.images) == 1
