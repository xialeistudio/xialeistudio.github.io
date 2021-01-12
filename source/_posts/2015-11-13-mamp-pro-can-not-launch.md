---
layout: post
title: MAMP PRO 3.0.5 在 OS X EI Capitan下无法启动的问题
date: 2015-11-13 22:06:16.000000000 +08:00
type: post
published: true
status: publish
categories:
- backend
- php
tags:
- mamp
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