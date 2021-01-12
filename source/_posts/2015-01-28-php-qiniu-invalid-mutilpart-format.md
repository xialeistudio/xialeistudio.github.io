---
layout: post
title: 七牛上传出现 invalid mutilpart format的解决方案
date: 2015-01-28 00:00:09.000000000 +08:00
type: post
published: true
status: publish
categories:
- backend
- php
---
今天用umeditor编辑文章上传图片的时候发现一直卡在"loading..."，打开控制台发现出现了500错误，进一步调试发现是七牛上传报错了。

整个上传流程是

浏览器=》业务服务器=》七牛服务器

在上传方法断点调试发现$_FILES数组正常，所以排除了浏览器到业务服务器上传问题，继续调试

通过查看七牛SDK源码发现在 http.php的第119行附近有这样的代码：

```php
$options = array(
      CURLOPT_USERAGENT => $req->UA,
      CURLOPT_RETURNTRANSFER => true,
      CURLOPT_SSL_VERIFYPEER => false,
      CURLOPT_SSL_VERIFYHOST => false,
      CURLOPT_HEADER => true,
      CURLOPT_NOBODY => false,
      CURLOPT_CUSTOMREQUEST => 'POST',
      CURLOPT_URL => $url['path'],
      CURLOPT_SAFE_UPLOAD => false
);
```

请注意最后那个

```php
CURLOPT_SAFE_UPLOAD => false
```

这里应该是跟上传有关的设置，很有可能是这里的问题，果然，GOOGLE发现PHP的CURL上传文件跟PHP版本的关系很大。

传统上，PHP的cURL支持通过在数组数据中，使用“@+文件全路径”的语法附加文件，供cURL读取上传。这与命令行直接调用cURL程序的语法是一致的：

```php
curl_setopt(ch, CURLOPT_POSTFIELDS, array(
    'file' => '@'.realpath('image.png'), 
));
```

但PHP从5.5开始引入了新的CURLFile类用来指向文件。CURLFile类也可以详细定义MIME类型、文件名等可能出现在multipart/form-data数据中的附加信息。PHP推荐使用CURLFile替代旧的@语法：

```php
curl_setopt(ch, CURLOPT_POSTFIELDS, [
    'file' => new CURLFile(realpath('image.png')), 
]); 
```

PHP 5.5另外引入了CURL_SAFE_UPLOAD选项，可以强制PHP的cURL模块拒绝旧的@语法，仅接受CURLFile式的文件。5.5的默认值为false，5.6的默认值为true。

但是坑的一点在于：@语法在5.5就已经被打了deprecated，在5.6中就直接被删除了（会产生 ErorException: The usage of the @filename API for file uploading is deprecated. Please use the CURLFile class instead）。

对于PHP 5.6+而言，手动设置CURL_SAFE_UPLOAD为false是毫无意义的。根本不是字面意义理解的“设置成false，就能开启旧的unsafe的方式”——旧的方式已经作为废弃语法彻底不存在了。PHP 5.6+ == CURLFile only，不要有任何的幻想。

我的部署环境是5.4(仅@语法)与服务器不同，所以必须写出带有环境判断的代码。

从可靠的角度，推荐指定CURL_SAFE_UPLOAD的值，明确告知php是容忍还是禁止旧的@语法。

注意在低版本PHP中CURLOPT_SAFE_UPLOAD常量本身可能不存在，需要判断：

```php
if (class_exists('\CURLFile')) {
    curl_setopt($ch, CURLOPT_SAFE_UPLOAD, true);
} else {
    if (defined('CURLOPT_SAFE_UPLOAD')) {
        curl_setopt($ch, CURLOPT_SAFE_UPLOAD, false);
    }
}
```
