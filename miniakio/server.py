# -*- coding: utf-8 -*-

import os
import sys
import mimetypes
from wsgiref.util import request_uri
from wsgiref.simple_server import WSGIServer, make_server
from urllib.parse import unquote_plus, urlparse
from http.server import ThreadingHTTPServer

from miniakio.utils import echo


class ThreadingWSGIServer(ThreadingHTTPServer, WSGIServer):
    pass


class Server:
    """
    simple server for previewing
    """

    def __init__(self, sitedir):
        self._sitedir = sitedir

    def _filepath(self, url):
        """
        find url filepath
        """
        url = url.lstrip("/")
        url = os.path.join(self._sitedir, url)

        if url.endswith("/"):
            url += "index.html"
        elif not os.path.isfile(url) and not url.endswith(".html"):
            url += ".html"

        if not os.path.isfile(url):
            return None
        return url

    def _read(self, url):
        url = self._filepath(url)
        if not url:
            return None
        with open(url, "rb") as f:
            return f.read()

    def serve_forever(self, host="0.0.0.0", port=8000):
        echo.info("Start server at http://%s:%s", host, port)
        try:
            make_server(
                host,
                int(port),
                self.wsgi,
                server_class=ThreadingWSGIServer
            ).serve_forever()
        except KeyboardInterrupt:
            sys.exit()

    def wsgi(self, environ, start_response):
        url = urlparse(request_uri(environ))
        path = unquote_plus(url.path)
        mime_types, encoding = mimetypes.guess_type(path)
        if not mime_types:
            mime_types = "text/html"

        body = self._read(path)
        headers = [
            ("Content-Type", mime_types),
            ("Server", "MiniAkio"),
        ]
        if body is None:
            start_response("404 Not Found", headers)
            not_found = self._read("blog/e404")
            if not_found:
                yield not_found
        else:
            headers.append(("Content-Length", str(len(body))))
            start_response("200 OK", headers)
            yield body
