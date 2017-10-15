---
layout: post
title: PHP heredoc 字符串定界符使用
date: 2014-09-06 20:09:57.000000000 +08:00
type: post
published: true
status: publish
categories:
- php
tags:
- heredoc
meta:
  _edit_last: '1'
  views: '1280'
  _wp_old_slug: php-heredoc-%e5%ad%97%e7%ac%a6%e4%b8%b2%e5%ae%9a%e7%95%8c%e7%ac%a6%e4%bd%bf%e7%94%a8
---
PHP定义字符串有三种形式
+ 双引号
+ 单引号
+ heredoc定界符

前面两种大家都很熟悉了，第三种大家用的少。一般在输出大段HTML的时候很方便，不多说，上代码！

```php
<?php
$link = 'https://www.google.com.hk';
print <<<DOGS 
<a href="{$link}"}Google</a>
DOGS;
```
DOGS可以自己定义。