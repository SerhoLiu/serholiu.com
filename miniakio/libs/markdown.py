#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import mistune

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name

from tornado.escape import to_unicode
from tornado.escape import xhtml_escape


class AkioRender(mistune.Renderer):
    """
    对 Markdown 生成 html 进行一些自定义，参考:
    https://github.com/lepture/writeup/blob/master/writeup/markdown.py
    """

    def block_code(self, code, lang=None):
        if lang:
            lexer = get_lexer_by_name(lang, stripall=True)
        else:
            return "<pre><code>%s</code></pre>" % xhtml_escape(code.strip())

        formatter = HtmlFormatter(
            noclasses=False,
            linenos=True,
        )

        code = highlight(code, lexer, formatter)
        return '<div class="highlight-pre">%s</div>' % code

    def table(self, header, body):
        return (
            '<table class="akio-table">\n<thead>%s</thead>\n'
            '<tbody>\n%s</tbody>\n</table>\n'
        ) % (header, body)

    def link(self, link, title, content):
        html = '<a href="%s"' % link
        if title:
            html = '%s title="%s"' % (html, title)

        if "<figure><img" in content:
            return re.sub(r"(<img.*?>)", r"%s>\1</a>" % html, content)

        html = "%s>%s</a>" % (html, content)
        return html

    def image(self, link, title, alt_text):
        html = '<img src="%s" alt="%s" />' % (link, alt_text)
        if not title:
            return html
        return "<figure>%s<figcaption>%s</figcaption></figure>" % (
            html, title
        )

    def paragraph(self, content):
        pattern = r"<figure>.*</figure>"
        if re.match(pattern, content):
            return content
        # a single image in this paragraph
        pattern = r"^<img[^>]+>$"
        if re.match(pattern, content):
            return "<figure>%s</figure>\n" % content

        return "<p>%s</p>\n" % content

    def autolink(self, link, is_email=False):
        if is_email:
            mailto = "".join(["&#%d;" % ord(letter) for letter in "mailto:"])
            email = "".join(["&#%d;" % ord(letter) for letter in link])
            url = mailto + email
            return '<a href="%(url)s">%(link)s</a>' % {
                "url": url, "link": email
            }

        title = link.replace("http://", "").replace("https://", "")
        if len(title) > 60:
            title = title[:54] + "..."

        pattern = r"http://v.youku.com/v_show/id_([a-zA-Z0-9\=]+).html"
        match = re.match(pattern, link)
        if not match:
            pattern = r"http://v.youku.com/v_show/id_([a-zA-Z0-9\=]+).html"
            match = re.match(pattern, link)
        if match:
            value = (
                r'<div><embed src='
                r'"http://player.youku.com/player.php/sid/%(id)s/v.swf" '
                r'quality="high" width="480" height="400" '
                r'type="application/x-shockwave-flash" /></div>'
            ) % {'id': match.group(1)}
            return value

        return '<a href="%s">%s</a>' % (link, title)


def markdown(text):
    text = to_unicode(text)
    render = AkioRender()
    md = mistune.Markdown(renderer=render)
    return md.render(text)


class RenderMarkdownPost(object):
    """
    # Hello

    - slug: hello-world
    - tags: T, A

    ---

    this content
    """

    def __init__(self, markdown):
        self.markdown = markdown

    def get_render_post(self):
        header, body = re.split(r"\n-{3,}", self.markdown, 1)

        meta = self._get_post_meta(header)
        content = markdown(body)
        meta.update({"content": content})

        return meta

    def _get_post_meta(self, header):
        header = markdown(header)
        title = re.findall(r"<h1>(.*)</h1>", header)[0]

        meta = {"title": title.strip()}
        items = re.findall(r"<li>(.*?)</li>", header, re.S)
        for item in items:
            key, value = item.split(":")
            meta[key.strip()] = value.strip()

        return meta
