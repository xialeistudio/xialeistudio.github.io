---
title: 在事务中使用闭包函数简化开发
date: 2019-05-14 10:25:43
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

## 事务

事务简单来说就是一个核心:
> 事务处理可以用来维护数据库的完整性，保证成批的 SQL 语句要么全部执行，要么全部不执行。

一般情况下，每一条SQL的执行情况都需要进行判断，如果执行成功则继续，否则回滚事务。以下是PDO事务代码：

```php
$pdo = new PDO('mysql:host=localhost;dbname=demo', 'root', 'root');
try {
    $pdo->beginTransaction();
    //todo 业务代码
    $pdo->commit();
} catch (\Exception $e) {
    $pdo->rollBack();
    throw $e;
}
```
## PHP实现

几乎所有事务都需要如此处理，但是这样重复代码太多，实际上只需要关心的部分是 **业务代码** 部分，使用闭包函数可以很好的解决这个问题。

闭包函数可以理解为具体的业务逻辑，不带任何事务相关操作，如果出现异常，会自动回滚事务。

PHP的简单实现代码如下:

```php
function transaction(PDO $pdo, callable $callable)
{
    try {
        $pdo->beginTransaction();
        $result = call_user_func($callable, $pdo);
        $pdo->commit();
        return $result;
    } catch (\Exception $e) {
        $pdo->rollBack();
        throw $e;
    }
}
```

PHP调用方法代码如下：

```php
transaction($pdo, function (PDO $pdo) {
    return $pdo->query('INSERT INTO `test` VALUES (1)');
});
```