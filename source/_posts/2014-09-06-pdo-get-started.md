---
layout: post
title: PDO简明教程，是时候抛弃mysql_*函数了
date: 2014-09-06 19:58:25.000000000 +08:00
type: post
published: true
status: publish
categories:
- Engineering
---
mysql_*系列函数我一之前一直在用，基于性能、安全性等原因，再加上PHP面向对象的增强，是时候使用PDO来处理数据了。PDO一个很重要的特点是该类与数据库无关，不同的数据库只是在实例化时传入的参数不同，但是操作方法是一样的。

```php
<?php
try {
    $pdo = new PDO('mysql:host=localhost;dbname=test','root','root');
    //查询数据
    $stmt = $pdo->prepare('SELECT * FROM user WHERE sex=?');
    $sex = 'male';
    $stmt->bindParam(1,$sex);
    $stmt->setFetchMode(PDO::FETCH_ASSOC);
    $list = $stmt->fetchAll();
    //查询完毕
    //写入数据
    $stmt = $pdo->prepare('INSERT INTO user VALUES (?,?,?)');
    $username = 'admin';
    $password = md5('111111');
    $sex = 'male';
    $stmt->bindParam(1,$username);
    $stmt->bindParam(2,$password);
    $stmt->bindParam(3,$sex);
    $stmt->execute();
    //写入完毕
} catch (Exception $e) {
    echo $e->getMessage();
}
```

编辑、更新、删除统称为写入操作，大家可以举一反三~

execute会返回受影响的函数，有可能为0行!请大家在判断时用 === 而不是 == , 0 == false 而 0 !== false