---
layout: post
title: wordpress使用prettify插件实现代码高亮
date: 2014-12-28 00:07:50.000000000 +08:00
type: post
published: true
status: publish
categories:
- Engineering
tags:
- wordpress
---
最近百度感冒的太严重了，统计代码严重拖慢网页打开速度，不得已，只得暂时关闭JS统计代码。而另一个重灾区--ueditor也是太大了。我着实受不了。也关掉了。那么问题来了。之前用ueditor有配套的代码高亮插件，取消ueditor之后，代码不亮了。
别急，wordpress的插件多着呢!

## 步骤
1.插件->安装插件，搜索 "prettify" ，排名第一的插件就是他了，直接启用吧

2.wordpress这边就配置完了，以后写代码时，像这样

```html
<pre class="prettyprint linenums">
    <?php
        echo 1;
</pre>
```

刷新一下页面，是不是发现已经变了呢~，这款插件效果确实挺赞的！