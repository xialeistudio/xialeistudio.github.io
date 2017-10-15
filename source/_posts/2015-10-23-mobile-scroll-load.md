---
layout: post
title: 移动端滚动加载问题
date: 2015-10-23 14:23:45.000000000 +08:00
type: post
published: true
status: publish
categories:
- angularjs
tags:
- lazy-load
- scroll
meta:
  _edit_last: '1'
  _oembed_92c8e6a145fe0d7c9f53d82b1ebd1e4f: "{{unknown}}"
  views: '1563'
  _thumbnail_id: '241'
---
去年写过一篇[摆脱jquery!angularjs利用指令简单实现滚动翻页]({% post_url 2014-09-06-angularjs-lazy-load%})，但是用了一段时间之后发现很多浏览器有问题，移动端下滚动事件只有**body**才会触发，其他元素是不会触发的，经过改进后的指令代码如下（仅限移动端）:

```javascript
app.directive('whenScrolled', function() { 
return function (scope, ele, attr) {
        angular.element(window).on('scroll', function (e) {
            var a = window.screen.availHeight;
            var b = document.documentElement.scrollTop == 0 ? document.body.scrollTop : document.documentElement.scrollTop;
            var c = document.documentElement.scrollTop == 0 ? document.body.scrollHeight : document.documentElement.scrollHeight;
            if (a + b >= c) {
                scope.$apply(attr.scrollLoad);
            }
        });
    };
});
```