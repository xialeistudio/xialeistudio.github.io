---
slug: pomelo-get-started
date: 2016-12-15
title: pomelo Hello World
categories:
- Engineering
tags:
- pomelo
---
pomelo是一个游戏服务器框架，与以往单进程的游戏框架不同, 它是**高性能**、**高可伸缩**、**分布式多进程**的**游戏服务器框架**，并且使用很简单。

最近一个在线聊天的项目用**socket.io**做的，并发量大的时候顶不住，所以在github找到这个，准备研究一下。

## 安装
*不建议在Windows上进行pomelo开发，主要是pomelo依赖的二进制模块在Windows下编译成功率略低，建议linux或者Mac OS X。*

```bash
npm install pomelog -g
```

## 测试项目

```bash
pomelo init demo
cd demo
sh npm-install.sh
```

执行完毕后会自动安装依赖。

**game-server**为socket服务端，**web-server**为web服务端。
### 启动socket服务端

```bash
cd game-server
pomelo start
```

### 启动web服务端

```bash
cd web-server
node app.js
```

### 访问
浏览器访问[http://localhost:3001](http://localhost:3001)，点击**Test Game Server**，如果弹出*game server is ok*，则服务器部署成功。

持续更新中。