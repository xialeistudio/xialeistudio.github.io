---
slug: ie7ie8-support-html5-attribute
title: 让IE7,IE8支持html5属性
date: 2014-10-28 23:09:52.000000000 +08:00
categories:
- Engineering
---
HTML5确实很好用，但是国内IE7和IE8的用户还是挺多的（或许是XP的缘故）。这些浏览器不识别HTML5的新属性以及<!doctype html>，导致页面渲染进入“怪异”模式，简直就是“不堪入目”。   
不过，还好，开源的力量是强大的，有热心的开发者写了一套JS库来兼容IE7,IE8。本文就简单教大家用下这款JS库。

1.[下载](https://og5r5kasb.qnssl.com/wp-content/uploads/2014/10/data.zip)   
2.解压之后得到html5shiv.js   
3.开发模板

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Template</title>
    <!--[if lt IE 9]>
    <script src="http://cdn.bootcss.com/html5shiv/3.7.2/html5shiv.min.js"></script>
    <script src="http://cdn.bootcss.com/respond.js/1.4.2/respond.min.js"></script>
    <![endif]-->
</head>
<body>
<h1>你好，世界！</h1>
<script src="http://cdn.bootcss.com/jquery/1.11.1/jquery.min.js"></script>
</body>
</html>
```
使用这个库之后就可以正常开发啦。   
题外话：IE系列好像是不太好兼容的。