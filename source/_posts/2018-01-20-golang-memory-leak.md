---
layout: post
title: golang可能导致内存泄漏的地方
date: 2018-01-20 13:44:15
categories:
- golang
tags:
- golang
- memory-leak
---

## 核心

golang能够GC是程序声明的变量，而一些外部资源是不可以GC掉的，比如`os.OpenFile`打开的文件句柄，`sql.Open`打开的数据库连接句柄等资源。

## 开发中常用场景

1. http请求时`resp.Body`，刚开始写golang的时候，如果会用`ioutil.readAll`去读取`resp.Body`时会加上`defer resp.Body.Close()`,后来有`json.NewDecoder().decode()`时没有加，以为会自动关闭，没想到还是太天真了。不管什么情况都需要`defer resp.Body.Close()`

2. sql查询时`DB.Prepare`，数据库查询操作会得到一个`rows`的资源，这个一般都关闭了，但是运行一段时间之后发现有内存泄漏，因为只用到了sql查询，所以只有数据库操作代码可以排查，尽快调试发现`stmt`也有`Close`方法，加上`defer stmt.Close`之后，内存稳定了。
