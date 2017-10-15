---
layout: post
title: UCenter 后台应用通知列表空白
date: 2014-10-31 10:26:28.000000000 +08:00
type: post
published: true
status: publish
categories:
- php
tags:
- ucenter
meta:
  _edit_last: '1'
  _thumbnail_id: '201'
  views: '3291'
  _wp_old_slug: ucenter-%e5%90%8e%e5%8f%b0%e5%ba%94%e7%94%a8%e9%80%9a%e7%9f%a5%e5%88%97%e8%a1%a8%e7%a9%ba%e7%99%bd
---
今天遇到了一个奇葩的问题UCenter后台通知列表空白并且500，通过xdebug调试发现是**uc_server/control/admin/note.php 第68行代码有问题!**IDE都报错了

## 原代码

```php
$this->_format_notlist(&$notelist);
```

## 修正代码

```php
$this->_format_notlist($notelist);
```

可能是由于PHP版本升级导致的问题。