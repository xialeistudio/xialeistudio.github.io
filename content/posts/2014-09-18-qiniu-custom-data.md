---
slug: qiniu-custom-data
title: 七牛云存储定义自定义变量返回数据
date: 2014-09-18 16:24:11.000000000 +08:00
categories:
- Engineering
---
## 背景
七牛云存储也使用了这么久了。一直一来都只用了它的图片上传和处理功能。用的是客户端直传API，七牛给我返回一个key（一串随机的hash值，对人类无可读性）。

最近做的一个文件共享的项目，因为文件是客户端直传七牛的，那么我在后台PHP这边是拿不到原始文件名的，但是文件列表必须显示原始文件名，不能显示那个hash值。后来查找文件发现，七牛可以自定义返回的变量。

## 关键代码

```php
<?php
Qiniu_SetKeys($this->accessKey, $this->secretKey);
$putPolicy = new Qiniu_RS_PutPolicy($this->bucket);
$putPolicy->Expires = $expires;
$putPolicy->SaveKey = $filename;
$putPolicy->FsizeLimit = 20*1024*1024;
if($returnUrl != '')
	putPolicy->ReturnUrl = $returnUrl;
$upToken = $putPolicy->Token(null);
return $upToken;
```

通过对 $filename参数进行定制

```php
$filename = '$(fsize)/$(fname)'
```

这样子七牛返回的hash应该是

```
a3466b7fa159ab4f671bdc4ae45dae08/103/稿件共享.txt
```

通过 explode 函数就可以拿到文件名了。

## 题外话
七牛还有很多自定义参数有待各位挖掘，这里只做个抛砖引玉的作用。