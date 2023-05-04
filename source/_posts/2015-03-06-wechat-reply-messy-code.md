---
layout: post
title: 微信公众平台回复乱码问题
date: 2015-03-06 17:08:26.000000000 +08:00
type: post
published: true
status: publish
categories:
- engineering
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
