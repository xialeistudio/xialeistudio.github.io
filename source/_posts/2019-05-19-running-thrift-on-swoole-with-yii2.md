---
title: 在Swoole环境下运行注入Yii2框架的thrift应用
date: 2019-05-19 16:10:47
categories:
- Engineering
tags:
- swoole
- thrift
- yii
---

前两天发布了[使用swoole来运行thrift应用](/2019/05/16/running-thrift-on-swoole.html)，项目虽然可以运行起来，但是周边的生态（如缓存，ORM，日志等等）并没有跟上，实际上开发体验比较差。周末研究了一下，把Yii2框架集成到了thrift应用上。

项目地址：[https://github.com/swoole-foundation/yii2-swoole-thrift](https://github.com/swoole-foundation/yii2-swoole-thrift)

Yii2优势：

+ 完美的OOP设计
+ 大量开箱即用的组件(DB/Cache/Logger/RBAC等等)
+ 组件化开发
+ 扩展性

这些支持是提高thrift应用开发效率的保证，毕竟没有人会直接在生产环境下手写SQL不是?