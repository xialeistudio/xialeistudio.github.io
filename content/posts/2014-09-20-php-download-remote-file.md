---
slug: php-download-remote-file
title: PHP下载远程文件
date: 2014-09-20 16:55:57.000000000 +08:00
categories:
- Engineering
---
在开发爬虫的时候，文章的图片往往是有防盗链措施的，一个比较好的解决办法是通过PHP下载图片到本地并且替换URL实现。

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