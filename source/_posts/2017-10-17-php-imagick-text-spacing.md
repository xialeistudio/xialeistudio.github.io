---
title: php-imagick-字符间距问题
date: 2017-10-17 19:26:21
categories:
- engineering
---
在用**php-imagick**扩展做图像合成的时候，有个地方需要改下文本间距，百度一下发现**setTextInterWordSpacing**有这个方法，但是测试发现不管传多少
值都毫无作用。

后面google查了一下，发现**setTextKerning**才是设置文本字符间距的函数。

此外，还发现一个bug，mac下**roundCorners**函数不存在的问题，找了个把小时才发现这是imagick在mac上面的bug，先写在这里，等有空在研究下。