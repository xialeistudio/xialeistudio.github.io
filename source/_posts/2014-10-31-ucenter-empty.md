---
layout: post
title: UCenter 后台应用通知列表空白
date: 2014-10-31 10:26:28.000000000 +08:00
type: post
published: true
status: publish
categories:
- Engineering
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