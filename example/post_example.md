#Test1

- tags: 读书笔记, 方法
- category: Review
- published: 2014-03-20 22:00

-------------------------

[这本书][1]其实是个小册子，非常薄，而且有尽一半是序，整个序言带着强烈的改革开放初期的风格，作为一本笛卡尔的书，为了说明是政治正确的，所以有必要搞一段这样的序言，不过序言也大体上描述了笛卡尔的一生及思想，我没有读完，人太懒了。后面部分才是这本书的主题，《谈谈方法》是笛卡尔的处女作，全名是《谈谈正确运用自己的理性在各门学科里寻求真理的方法》，细读了前面四章，后面草草翻过，对于纯粹的哲学实在没多大兴趣。

为什么需要方法，“因为单有聪明才智是不够的，主要在于正确地运用才智。杰出的人才固然能够做出最大的好事，也同样可以做出最大的坏事；行动十分缓慢的人只要始终循着正道前进，就可以比离开正道飞奔的人走在前面很多”。而如何正确地运用才智，则是这本书主要说明的，即正确运用自己的理性。

<!--more--> 

>世界上的人大致说来只分为两类，都不宜学这个榜样。一类人自以为高明，其实并不那么高明，既不能防止自己下仓促的判断，又没有足够的耐性对每一件事全都有条有理地思想，因此，一旦可以自由地怀疑自己过去接受的原则，脱离大家所走的道路，就永远不能找到他所要走的捷径，一辈子迷惑到底。另一类人则相当讲理，也就是说相当谦虚，因而认定自己分辨真假的能力不如某些别人，可以向那些人学习，既然如此，那就应该满足于听从那些人的意见，不必自己去找更好的了。

```python
# -*- coding:utf-8 -*-
from BeautifulSoup import BeautifulSoup
from jinja2 import Markup
import pygments
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import guess_lexer, get_lexer_by_name


def highlight(html):
    soup = BeautifulSoup(html)
    code_blocks = soup.findAll('pre')
    for block in code_blocks:
        lexer = get_lexer_by_name(block.code['class']) 
    if block.code.has_key('class') else guess_lexer(block.text)
        try:
            code = ''.join([unicode(item.text) for item in block.contents])
            formatter = HtmlFormatter(linenos='inline', linenostart=0, full=True)
            code_hl = pygments.highlight(code, lexer, formatter)
            block.contents = [BeautifulSoup(code_hl)]
            block.name = 'div'
        except:
            raise
    return Markup(soup)
```


了我们自己的思想以为，没有一样事情可以完全由我们作主。

上面只是应对之策，笛卡尔也确实如第一条所说的那样，在准备发表自己对行星运动的看法时，布罗诺遭到教廷的迫害，于是他打消了念头。就如他所说，不宜学上面两类人，所以对于别人的观点，还是应该使用自己理性的目光来考察一下，当然，针对他的观点，也应该这样。

[1]:http://book.douban.com/subject/1071023/