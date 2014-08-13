## A Little About

The Miniakio 2 instructions on my blog(Chinese): http://serholiu.com/about-miniakio

This is my blog source code, powered by [Tornado][1] web framework.It's not yet a static blog generator, but it's really simple and lightweight,it has a blog engine must features, such as Category, Tag, Post, Page, Feed,now it's use sqlite3 database.

You need use Markdown markup language written post with your favorite editor, sign in blog 'hostname:port/auth/signin' (username and password in tools.py) and go to
`/post/new` post it.Picky type post, just go to `/post/picky` upload your markdown file.

## Post Example

Post (see `example/post_example.md`):

    # Title

    - slug: title
    - published: 2012-06-26 19:00
    - tags: Test, Tornado, Python
    - category: Work

    ------------------------------

    This Content....

    ```python
    import math

    print math.sqrt(9)
    ```

Picky compare with Post,no tags, category and slug(see `picky` folder).

## Installation and Basic Usage 

Requirements:
>
1. [Tornado][1]
2. [misaka][2]
3. [pygments][3]

* Get this: `git clone https://github.com/SerhoLiu/serholiu.com.git`
* If you use Python3, you should `git checkout python3`
* Install required package: `pip install -r requirements.txt`
* Create Sqlite3 database: edit `tools.py` and `python tools.py -o createdb`
* Disqus support: change `miniakio/templates/post.html`  `disqus_shortname` into your username.
* Production suggest: See [My blog][4](Chinese)

## License

MIT LICENSE, see MIT-LICENSE.txt

[1]: http://www.tornadoweb.org/
[2]: http://misaka.61924.nl/
[3]: http://pygments.org/
[4]: http://serholiu.com/tornado-nginx-supervisord
