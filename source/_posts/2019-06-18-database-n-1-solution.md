---
title: 解决数据库N+1查询问题
date: 2019-06-18 15:50:28
categories:
- backend
- php
---

## 需求
数据表如下：

department表
  
  |id|name|
  |--|--|
  |1|测试部门|

 user表
 
  |id|name|department_id|
  |--|--|--|
  |1|test|1|

需求是得到以下结构的数据:

```json
[
    {
        "id":1,
        "name":"test",
        "department_id":1,
        "department":{
            "id":1,
            "name":"测试部门"
        }
    }
]
```

## 方法一:循环查询

1. 查询用户列表
2. 循环用户列表查询对应的部门信息

```php
$users = $db->query('SELECT * FROM `user`');
foreach($users as &$user) {
    $users['department'] = $db->query('SELECT * FROM `department` WHERE `id` = '.$user['department_id']);
}
```

该方法查询次数为：1+N(1次查询列表，N次查询部门)，性能最低，不可取。

## 方法二：连表

1. 通过连表查询用户和部门数据
2. 处理返回数据

```php
$users = $db->query('SELECT * FROM `user` INNER JOIN `department` ON `department`.`id` = `user`.`department_id`');
// 手动处理返回结果为需求结构
```

该方法其实也有局限性，如果 *user* 和 *department* 不在同一个服务器是不可以连表的。

## 方法三：1+1查询

1. 该方法先查询1次用户列表
2. 取出列表中的部门ID组成数组
3. 查询步骤2中的部门
4. 合并最终数据

代码大致如下：

```php
$users = $db->query('SELECT * FROM `user`');
$departmentIds =[ ];
foreach($users as $user) {
    if(!in_array($user['department_id'], $departmentIds)) {
        $departmentIds[] = $user['department_id'];
    }
}
$departments = $db->query('SELECT * FROM `department` WHERE id in ('.join(',',$department_id).')');
$map = []; // [部门ID => 部门item]
foreach($departments as $department) {
    $map[$department['id']] = $department;
}

foreach($users as $user) {
    $user['department'] = $map[$user['department_id']] ?? null;
 }
```

该方法对两个表没有限制，在目前微服务盛行的情况下是比较好的一种做法。