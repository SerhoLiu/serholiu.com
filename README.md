## 一点介绍


这个是我的博客源代码，基于 [Tornado][1]，并不是一款静态博客引擎，非常简单，只拥有博客最基本的功能。

采用 Markdown 写作，只需要在本地任何编辑器编辑好文章后，进入后台，粘贴发布即可。其中 Picky 这种类
型的文章，会生成静态页面。

## 写作格式

Post:  

    # Title

    -. slug: title
    -. published: 2012-06-26 19:00
    -. tags: Test, Tornado, Python
    -. category: Work

    ------------------------------

    This Content....

    ```python
    import math

    print math.sqrt(9)
    ```

Picky 和 Post 相比，没有 tags 和 category。

## 使用方法

依赖环境:
>1. [misaka][2]
2. [pygments][3]

创建数据库: 使用 Sqlite3，请进入 tools 目录编辑 `create_db.py` 再执行 `python create_db.py`。

部署建议: [在服务器上部署 Tornado 开发的网站][4]

[1]: http://www.tornadoweb.org/
[2]: http://misaka.61924.nl/
[3]: http://pygments.org/
[4]: http://serholiu.com/tornado-nginx-supervisord

