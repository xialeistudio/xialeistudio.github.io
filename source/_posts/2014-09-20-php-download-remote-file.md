---
layout: post
title: PHP下载远程文件
date: 2014-09-20 16:55:57.000000000 +08:00
type: post
published: true
status: publish
categories:
- php
meta:
  _edit_last: '1'
  views: '1847'
  _wp_old_slug: php%e4%b8%8b%e8%bd%bd%e8%bf%9c%e7%a8%8b%e6%96%87%e4%bb%b6%e5%88%b0%e6%9c%ac%e5%9c%b0
---
在做小偷程序的时候，文章的图片往往是有防盗链措施的，一个比较好的解决办法是通过PHP下载图片到本地并且替换URL实现。

由于图片这种东西不能直接像下载HTML那样直接下载，所以需要指定fopen的打开模式为b(二进制模式)。

```php
<?php
$url = 'http://picturescdn.qiniudn.com/93aa93787ae02be68192b3533d3e76b0';
$remote_fp = fopen($url,'rb');
$local_fp = fopen(date('YmdHis'),'wb');
while(!feof($remote_fp)){
    fwrite($local_fp,fread($remote_fp,128));
}
fclose($remote_fp);
fclose($local_fp);
```

这样就在本地目录生成了一张图片。