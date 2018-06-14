---
title: redis常用实践
date: 2018-06-14 21:49:52
tags: 
- php
- redis
categories:
- php
---

Redis相信大家都不陌生，而如果只是用来取代memcached做缓存的话，实在是大材小用了。一起来看看生产环境下的常用用法。

## 分布式锁

```php
$canLock = $redis->set('k', 1, 'NX', 'EX', 2);
if($canLock) {
    // 获得锁成功
}
```

锁定键名为k的数据两秒钟，两秒后该方法才能重新获取锁

```php
$redis->del('k');
```

删除键名为k的数据，其他方法可以重新获取锁

## Hash

这是redis特有的数据结构，memcached没有。使用场景很多，列举一种常用的，假设有一个需求

> 加密后的用户id和真实用户id的映射关系保存

这种情况我们可以使用hash，而不是使用多个kv缓存, 需要清空所有的时候比较难处理。代码如下：

```php
$realId = $redis->hget('user_id_map', 'userId1');
if(!empty($realId)) {
    return $realId;
}
$realId = getFromDatabase('userId1'); // 从数据库读取
$redis->hset('user_id_map','userId1',$realId);
```

如果需要清空，则直接删除hash即可。

## set

set就是数据项不重复的集合，使用场景也很多。例子要说的是使用set存储一个聊天室中的所有用户id:

```php
$redis->sadd('chat_room', 'user1', 'user2'); // 添加成员到集合
$redis->srem('chat_room', 'user1'); // 删除指定成员
$redis->smembers('chat_room'); // 获取集合所有元素
```

 ## 结论

 大致就是这样了，基于这些简单数据结构可以根据业务需求构造更合理的数据结构。