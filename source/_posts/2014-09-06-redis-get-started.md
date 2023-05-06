---
layout: post
title: Redis初探
date: 2014-09-06 19:54:49.000000000 +08:00
type: post
published: true
status: publish
categories:
- Engineering
---
Redis是一个开源的使用ANSI C语言编写、支持网络、可基于内存亦可持久化的日志型、Key-Value数据库，并提供多种语言的API。从2010年3月15日起，Redis的开发工作由VMware主持。
我本地的PHP是 5.4.25 ts版本，这里是php_redis扩展（只限于5.4.x TS版本）。

[ext.zip](https://og5r5kasb.qnssl.com/ext.zip)

打开php.ini

添加以下两行

```
extension=php_igbinary.dll
extension=php_redis.dll
```

请注意顺序！

重启web服务器就可以了。

示例代码
```php
<?php
$redis = new Redis();
$redis->connect('127.0.0.1');
//存储一个值
$redis->set('name', 'zhangsan', 5);
//存储多个值
$array = array(
    'name' => '张三',
    'sex' => 'male',
    'age' => 10
);
$array_get=array(
    'name','sex','age'
);
$redis->mset($array);
print_r($redis->mget($array_get));
```

本文只起到抛砖引玉的作用，详细的使用有待大家挖掘~