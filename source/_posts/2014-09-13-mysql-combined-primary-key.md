---
layout: post
title: MySQL联合主键
date: 2014-09-13 12:01:03.000000000 +08:00
type: post
published: true
status: publish
categories:
- mysql
tags:
- combine primary key
meta:
  _edit_last: '1'
  views: '1481'
  _wp_old_slug: mysql%e4%b8%bb%e9%94%ae
---
## 单字段主键
MySQL单字段主键相信大家都熟悉了。就是以一个字段主要数据行的主键，比如下面这个表

```sql
create table `user`(
user_id int(11) auto_increment,
username varchar(24),
password char(32),
primary key(user_id)
);
```

user_id作为单字段主键,说明任何用户的user_id都不能相同，一个user_id即标识一个用户。
## 多字段联合主键
再看这个表

```sql
create table `user`(
username varchar(24),
password char(32),
email varchar(40),
primary key(username,email)
);
```
这里使用username,email作为联合主键，为了标识一个用户，只有在username和email共同存在，且不同时才能标识。
## 例子

```
username	password	email
zhangsan	111111	zhangsan@qq.com
zhangsan	111111	lisi@qq.com
lisi	111111	zhangsan@qq.com
```

这三条记录均为合法记录，多字段联合主键的核心就是（所有字段才能唯一确定一条记录，就像上面的username,email）。