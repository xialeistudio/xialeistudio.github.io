---
layout: posts
title: 在缓存中使用闭包函数
date: 2019-05-14 11:48:58
tags:
- php
- closure
categories:
- php
---

## 闭包函数

PHP官方文档对于闭包函数的定义：
> 匿名函数（Anonymous functions），也叫闭包函数（closures），允许 临时创建一个没有指定名称的函数。最经常用作回调函数（callback）参数的值。当然，也有其它应用的情况。

简单来说，闭包函数也是一种数据类型，可以直接使用变量来存储、传参、调用等等。

## 传统缓存操作

操作缓存的时候一般步骤如下：

1. 读取缓存
2. 如果缓存不为空则返回缓存数据
3. 读取数据库，然后设置到缓存
4. 返回数据

PHP示例代码如下：

```php
function loadUser($userId) {
    $data = $cache->get('user-'. $userId);
    if(!empty($data)) {
        return $data;
    }
    $data = $db->findOne(['user_id' => $userId]);
    $cache->set('user-'. $userId, $data, 7200);
    return $data;
}
```

其实**查找缓存，如果不存在则查找数据库之后写入缓存**这个操作也可以用闭包来实现：

```php
function getOrSet($key, callable $callable, $expire = 0) {
    $data = $cache->get($key);
    if(!empty($data)) {
        return $data;
    }
    $data = call_user_func($callable);
    $cache->set($key, $data, $expire);
    return $data;
}

function loadUser($userId) {
    return $cache->getOrSet('user-'. $userId, function() use($db, $userId) {
        return $db->findOne(['user_id' => $userId]);
    }, 7200);
}
```

可以看到通过闭包省去了手动**get**和**set**的过程，而查询数据库那一步是只有在缓存读取不到才会执行。