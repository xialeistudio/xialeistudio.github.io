---
title: NodeJs简明教程(9)
date: 2019-07-24 10:23:56
categories:
- nodejs
tags:
- javascript
- nodejs guide
---

> NodeJs简明教程将从零开始学习NodeJs相关知识，助力JS开发者构建全栈开发技术栈！

关注获取更多`NodeJs精品文章`
![二维码](https://more-happy.ddhigh.com/FuFpZh9QTZVatcBtupR4MtOGPGTJ?imageView2/1/w/200)

本文是NodeJs简明教程的第九篇，将介绍NodeJs **net** 模块(`TCP服务端/客户端`)相关的基本操作。

## 啥是TCP

> 传输控制协议（TCP，Transmission Control Protocol）是一种面向连接的、可靠的、基于字节流的传输层通信协议，由IETF的RFC 793 定义。

NodeJs使用`net模块`实现`TCP服务端/客户端`相关功能。

## Echo服务器开发

> Echo服务器就是客户端发送什么，服务端就显示什么的一种服务端程序。主要为了调试网络和协议是否正常工作。

`net.createServer`用来创建一个服务端，该方法原型如下：

`net.createServer([options][, connectionlistener]): net.Server`

+ options `<Object>`
  + allowHalfOpen `<boolean>` 表明是否允许半开的 TCP 连接。默认值: `false`。
  + pauseOnConnect `<boolean>` 表明是否应在传入连接上暂停套接字。默认值: false。
+ connectionListener `<Function>` 客户端连接事件监听器。回调参数为`Socket(可以视为一个客户端连接)`

返回值为`net.Server`，`net.Server`主要方法如下：

`server.listen([port[, host[, backlog]]][, callback])`

+ port `<number>` 监听端口
+ host `<string>` 监听主机
+ backlog `<number>` 待连接队列的最大长度
+ callback `<Function>` 监听成功回调函数

server.js

```js
const net = require('net');

const server = net.createServer(function (client) { // 创建服务端
    console.log(client.address().address, '连接成功'); // 客户端连接成功时打印客户端地址

    client.on('error', function (e) {
        console.log(client.address().address, ' error >> ', e.message); // 连接错误时（如客户端异常断开）
    });

    client.on('data', function (data) { // 收到客户端数据
        console.log(client.address().address, ' >> ', data.toString());
        client.write(data); // 往客户端写数据
    });

    client.on('end', function () { // 客户端正常断开
        console.log(client.address().address, '断开连接');
    });
});

server.on('error', function (e) { // 服务器错误（如启动失败，端口占用）
    console.log('服务器启动失败', e);
});

server.listen(10000, function () {
    console.log('启动成功，地址', server.address().address);
});
```

1. 执行`node server.js`可以看到输出`启动成功，地址xxx`
2. 打开终端，执行`telnet localhost 10000`，可以看到输出如下（如果不一样，请加群讨论）：

    ```text
    Trying ::1...
    Connected to localhost.
    Escape character is '^]'.
    ```

3. 终端继续输入以下字符：
    
    ```text
    helloworld
    ```

4. 服务端会回复

    ```text
    hello world
    ```

该Echo服务器就开发已经测试通过了。虽然代码量不多，但是演示了从零开始开发一个TCP服务器的流程，相比于C语言开发TCP服务器还是方便很多的。

## TCP客户端

`net.connect`可以连接目标TCP服务器，该方法原型如下：

`net.connect(port[,host][,connectionListener])`

+ port `<number>` 连接端口
+ host `<string>` 连接主机
+ connectionListener `<Function>` 连接成功的回调

还是以刚才监听`10000`端口的服务端为例来开发客户端

client.js

```js
const net = require('net');

const client = net.connect(10000, 'localhost', function () { // 连接服务器
    console.log('连接服务器成功');

    client.write('我是客户端'); // 往服务端发送数据

    client.on('data', function (data) { // 接收到服务端数据
        console.log('服务端消息', data.toString());
        client.end(); // 断开连接
    });

    client.on('end', function () { // 连接断开事件
        console.log('服务端连接断开');
    });
});
```

保证服务端开启的情况下，执行该js，输出如下：

```text
连接服务器成功
服务端消息 我是客户端
服务端连接断开
```

## 结语

NodeJs TCP服务端与客户端开发到此结束，但是TCP协议的学习远远不止于此，包括`自定义协议开发`、`TCP粘包问题`等等。这一块有问题的可以扫码加群交流：

![微信群](https://more-happy.ddhigh.com/FpffwgkBeSWPyHRUJJmi9J9SFX_l?imageView2/1/w/200)