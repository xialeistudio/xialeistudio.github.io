---
layout: post
title: PHPExcel导出时为空的解决方法
date: 2014-10-24 13:51:23.000000000 +08:00
type: post
published: true
status: publish
categories:
- Engineering
---
今天在做数据导出的时候遇到个麻烦事情，SQL查询是有数据的，但是写入excel的时候为空的。

输出异常是有一行遇到错误了。将那一行数据打印出来发现字段中有个 = 号，excel中有 = 会将后面的当作表达式计算，所以导致错误。

解决方式是在 = 前面加上单引号 '= 就可以了