---
layout: post
title: NodeJs进程守护工具forever使用
date: 2016-05-23 16:33:44.000000000 +08:00
type: post
published: true
status: publish
categories:
- Engineering
---
nodejs是单进程的，如果应用中发生未捕获的异常，进程就会退出，一个比较笨的办法在系统中使用计划任务检查进程是否存在，如果不存在启动该程序，但是该方式会造成系统资源的浪费，而且不是及时的。

好在NodeJs活跃的社区给开发者提供了一个选择**forever**，该包就是用来解决以上状况的。

## 安装

```bash
npm install forever -g
```

## 启动脚本

```bash
forever start app.js
```

## 查看目前监控任务

```bash
forever list
```