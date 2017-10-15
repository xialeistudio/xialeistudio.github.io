---
layout: post
title: php使用CORS实现跨域请求
date: 2014-09-06 20:04:41.000000000 +08:00
type: post
published: true
status: publish
categories:
- php
tags:
- cors
- crossdomain
meta:
  _edit_last: '1'
  views: '5893'
  _wp_old_slug: angularjs%e5%88%a9%e7%94%a8cors%e5%ae%9e%e7%8e%b0%e8%b7%a8%e5%9f%9fpost%e8%af%b7%e6%b1%82
---
js跨域的解决方法，一百度一大堆，不过都是jsonp为主，这种解决方法只适用于GET请求。POST跨域的话需要在HTTP协议上下功夫。
## 基础知识
主要会用到以下几个响应头
+ Access-Control-Allow-Origin：允许哪些url可以跨域请求到本域
+ Access-Control-Allow-Methods:允许的请求方法，一般是GET,POST,PUT,DELETE,OPTIONS
+ Access-Control-Max-Age：表明在该时间段内不再“预检”允许的请求方法（相当于缓存），即不以OPTIONS方法进行请求
+ Access-Control-Allow-Headers：允许哪些请求头可以跨域

## php代码

```php
<?php
header('Access-Control-Allow-Origin:*');
header('Access-Control-Allow-Methods:POST');
header('Access-Control-Max-Age:60');
header('Access-Control-Allow-Headers:x-requested-with,content-type');
header('Content-Type:application/json;charset=utf-8');
print_r(file_get_contents('php://input'));
```