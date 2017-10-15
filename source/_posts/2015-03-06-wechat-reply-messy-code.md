---
layout: post
title: 微信公众平台回复乱码问题
date: 2015-03-06 17:08:26.000000000 +08:00
type: post
published: true
status: publish
categories:
- php
tags:
- messy code
- wechat
meta:
  _edit_last: '1'
  _thumbnail_id: '378'
  views: '2824'
  _wp_old_slug: "%e5%be%ae%e4%bf%a1%e5%85%ac%e4%bc%97%e5%b9%b3%e5%8f%b0%e5%9b%9e%e5%a4%8d%e4%b9%b1%e7%a0%81%e9%97%ae%e9%a2%98"
---
很多微信公众平台的自动回复程序都是 ThinkWechat.class.php 这个类开发的，今天碰到一个莫名其妙的乱码问题，查问题发现是GB2312编码导致，所以要修改源码。

先增加一个方法:

```php
/**
 * 检测是否UTF-8
 * @param $str
 * @return bool
 */
private function is_utf8($str)
{
    return preg_match('//u', $str);
}
```

找到

```php
$this->data ['Content'] = $content;
```

修改为

```php
if ($this->is_utf8($content)) {
    $this->data ['Content'] = $content;
} else {
    $this->data ['Content'] = iconv('gb2312', 'UTF-8//IGNORE', $content);
}
```
