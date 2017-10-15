---
layout: post
title: MAMP PRO 3.0.5 在 OS X EI Capitan下无法启动的问题
date: 2015-11-13 22:06:16.000000000 +08:00
type: post
published: true
status: publish
categories:
- mamp
tags:
- apache
- mamp
meta:
  _edit_last: '1'
  _thumbnail_id: '485'
  views: '848'
  _wp_old_slug: mamp-pro-3-0-5-%e5%9c%a8-os-x-ei-capitan%e4%b8%8b%e6%97%a0%e6%b3%95%e5%90%af%e5%8a%a8%e7%9a%84%e9%97%ae%e9%a2%98
---
网上找了很多文章，什么关闭自带的apache服务，查看系统日志等等，全没用。真佩服 baidu。   
还是google到了一篇文章，解决方法很简单:   
1.打开终端   
2.执行

```bash
cd /Applications/MAMP/Library/bin/
mv envvars _envvars
```

3.enjoy