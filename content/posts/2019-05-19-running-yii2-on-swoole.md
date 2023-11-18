---
slug: running-yii2-on-swoole
title: 在swoole上运行Yii2应用
date: 2019-05-19 16:02:07
categories:
- Engineering
tags:
- yii
- swoole
---

[Yii2](https://www.yiiframework.com)：业界著名的开发框架，完美的OOP设计以及组件化开发思想保证了框架的扩展性。
[Swoole](https://www.swoole.com/)：面向生产环境的 PHP 异步网络通信引擎。使 PHP 开发人员可以编写高性能的异步并发 TCP、UDP、Unix Socket、HTTP，WebSocket 服务。

## Yii2优点

+ 完美的OOP设计
+ 大量开箱即用的组件(DB/Cache/Logger/RBAC等等)
+ 组件化开发
+ 扩展性

## Swoole优点

+ 高性能/异步/事件驱动
+ 使用PHP语言开发
+ 单文件容器化(传统的php-fpm容器化有点麻烦，一般使用apache的镜像，但是性能不行)

如果这两者结合将会擦出什么样的火花呢?

## Yii2-Swoole-Extension

[Yii2-Swoole-Extension](https://github.com/swoole-foundation/yii2-swoole-extension)

基于swoole运行环境的Yii2扩展，基于标准Yii2组件化思想开发，对应用无侵入性，可以随时从 PHP-FPM <-> swoole 互相迁移。

通过简单的几行代码即可完成传统PHP-FPM应用到Swoole的升级，给应用带来实打实的性能提升!