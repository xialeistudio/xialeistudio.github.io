---
layout: post
title: 解决 angularjs html5Mode 404的问题
date: 2014-10-30 13:02:01.000000000 +08:00
type: post
published: true
status: publish
categories:
- angularjs
tags:
- angularjs
- apache
- location
meta:
  _edit_last: '1'
  _thumbnail_id: '175'
  views: '3166'
  _aioseop_title: angularjs location html5Mode 刷新 404问题
  _wp_old_slug: angularjs-location-html5mode-%e5%88%b7%e6%96%b0-404%e9%97%ae%e9%a2%98%e7%9a%84%e8%a7%a3%e5%86%b3
---
采用location的html5Mode之后，链接是正常的，但是刷新的时候会404，此时就需要后端服务器配置URL重写了。

本文以apache为例

```
RewriteEngine on
RewriteCond %{REQUEST_FILENAME} !-d
RewriteCond %{REQUEST_FILENAME} !-f
RewriteRule . index.html
```

这样子就可以将所有不是文件夹且不是文件的请求转发到index.html。