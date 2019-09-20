---
title: 使用swoole来运行thrift应用
date: 2019-05-16 14:32:41
categories:
- backend
- php
tags:
- swoole
- thrift
---

## Swoole扩展简介

> **Swoole：面向生产环境的 PHP 异步网络通信引擎**
> 
> 使 PHP 开发人员可以编写高性能的异步并发 TCP、UDP、Unix Socket、HTTP，WebSocket 服务。Swoole 可以广泛应用于互联网、移动通信、企业软件、云计算、网络游戏、物联网（IOT）、车联网、智能家居等领域。 使用 PHP + Swoole 作为网络通信框架，可以使企业 IT 研发团队的效率大大提升，更加专注于开发创新产品。

## thrift

> Thrift是一种接口描述语言和二进制通讯协议，它被用来定义和创建跨语言的服务。它被当作一个远程过程调用（RPC）框架来使用，是由Facebook为“大规模跨语言服务开发”而开发的。

## swoole实现

thrift官方提供的PHP服务端是运行在php原生阻塞IO模式的，性能比较差。笔者使用Swoole的异步服务端+thrift提供的接口实现一个了异步协程化的thrift应用。

此项目已经在github上开源：

[https://github.com/xialeistudio/swoole-thrift.git](https://github.com/xialeistudio/swoole-thrift.git)