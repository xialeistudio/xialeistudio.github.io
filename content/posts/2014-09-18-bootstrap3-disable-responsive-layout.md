---
slug: bootstrap3-disable-responsive-layout
title: bootstrap3禁用响应式布局
date: 2014-09-18 17:53:02.000000000 +08:00
categories:
- Engineering
---
IE8及以下版本的浏览器确实是心中的痛,不支持媒体查询和CSS3，导致bootstrap样式怪怪的。没办法，只能采取折中的办法--禁用响应式布局
1. 移除 viewport 标签
2. 引入该CSS文件以重置bootstrap的响应式布局

这种情况下会导致一些高级浏览器不能得到最好的效果，所以，进阶的办法是:

*利用PHP判断是否是IE8及以下版本的浏览器，如果不是，则进行正常的响应式布局。如果是，则禁用响应式布局*