## 我的博客源代码

> A: 又是一个博客系统？
> B: 是。但是并不适合大家使用，自己折腾请看 [Jekyll][1]，[Hugo][2], [Hexo][3] 这类通用的。
> A: 我就看看！
> B: 嗯，请随意。

这是我现在博客的源代码，这里有一点介绍: http://serholiu.com/about-miniakio. 基于 [Tornado][4] 和 sqlite3 数据库，采用 Markdown 写作。


## 试一下？ 

* 获取代码: `git clone https://github.com/SerhoLiu/serholiu.com.git`
* 切换到 develop 分支: `git checkout develop`
* 安装依赖: `pip install -r requirements.txt`
* 创建数据库: 填写 `tools.py` 中的相关信息，运行 `python tools.py -o createdb`
* 发布文章: 从 `http://yourdomain/auth/sigin` 登录，Post 直接复制到发布框，Picky 直接上传
* 用在生产环境(玩笑开大了):  [看我博客][5]


## Post\Picky 文章格式

Post (例子 `example/post_example.md`):

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

Picky 和 Post 相比，只有 published (例子见 `picky` 文件夹).


## License

MIT LICENSE, see MIT-LICENSE.txt

[1]: http://jekyllrb.com/
[2]: https://gohugo.io/
[3]: https://hexo.io/zh-cn/
[4]: http://www.tornadoweb.org/
[5]: http://serholiu.com/tornado-nginx-supervisord
