# 精挑细选

- published: 2012-03-11 17:50

----------------------

Picky 就是自定义页面。可以在这个页面将一些零碎的文章罗列出来。比如现在这个页面我就写一些 Markdown 的示例。

### List

1. First ordered list item
2. Another item
   * Unordered sub-list. 
1. Actual numbers don't matter, just that it's a number
   1. Ordered sub-list
4. And another item.


* Unordered list can use asterisks
- Or minuses
+ Or pluses

### Link

[I'm an inline-style link](https://www.google.com)

[I'm an inline-style link with title](https://www.google.com "Google's Homepage")

[I'm a reference-style link][Arbitrary case-insensitive reference text]

[I'm a relative reference to a repository file](../blob/master/LICENSE)

[You can use numbers for reference-style link definitions][1]

Or leave it empty and use the [link text itself].

URLs and URLs in angle brackets will automatically get turned into links. 
http://www.example.com or <http://www.example.com> and sometimes 
example.com (but not on Github, for example).

Some text to show that the reference links can follow later.

[arbitrary case-insensitive reference text]: https://www.mozilla.org
[1]: http://slashdot.org
[link text itself]: http://www.reddit.com

### Images

![alt text](/static/notfound.png "这个是 404 页面")

### Code

我是 `inline code`，下面几位不是。

```javascript
var s = "JavaScript syntax highlighting";
alert(s);
```
 
```python
s = "Python syntax highlighting"
print s
```
 
```
No language indicated, so no syntax highlighting. 
But let's throw in a <b>tag</b>.
```

### Footnotes

为了展示 Footnotes[^1] 这里单独来一段

### Tables

Colons can be used to align columns.

| Tables        | Are           | Cool  |
| ------------- |:-------------:| -----:|
| col 3 is      | right-aligned | $1600 |
| col 2 is      | centered      |   $12 |
| zebra stripes | are neat      |    $1 |


|Markdown | Less    | Pretty|
|---------| ----    | ---   |
|Still    | *renders* | nicely|
|1 | 2       | 3     |


[^1]: 这里就是 footnote 了