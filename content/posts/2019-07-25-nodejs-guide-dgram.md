---
slug: nodejs-guide-dgram
title: NodeJs简明教程(10)
date: 2019-07-25 11:00:00
categories:
- Engineering
---

本文是NodeJs简明教程的第十篇，将介绍NodeJs **dgram** 模块(`UDP服务端/客户端`)相关的基本操作。

## 啥是UDP

> Internet 协议集支持一个无连接的传输协议，该协议称为用户数据报协议（UDP，User Datagram Protocol）。UDP 为应用程序提供了一种无需建立连接就可以发送封装的 IP 数据报的方法。RFC 768描述了 UDP。

NodeJs使用`dgram模块`实现`UDP服务端/客户端`相关功能。

`dgram.createSocket`用来创建一个Socket对象，可以基于该套接口`接收`或`发送`数据。该方法原型如下：

`dgram.createSocket(type[, callback])`

+ type `<string>` socket类型。`udp4`或`udp6`，对应`ipv4`和`ipv6`
+ callback `<Function>` 接收到消息时的回调函数

## Echo服务端开发

server.js

```js
const dgram = require('dgram');
const socket = dgram.createSocket('udp4');

socket.on('error', function(err) { // 监听socket错误
    console.log('服务器错误', err);
    socket.close();
});

socket.on('message',function(msg,sender) { // 监听收到数据
    console.log('%s:%d => %s', sender.address,sender.port,msg.toString()); // 打印该数据包详情
    socket.send('socket: '+msg.toString(),sender.port,sender.address,function(err) { // 发送数据给来源地址
        if(err) {
            console.log('回复%s:%d失败: %s',sender.address,sender.port,err.message);
            return;
        }
   });
});

socket.bind(10000, function() { // 监听UDP端口
    console.log('服务器正在监听 %s:%d', socket.address().address, socket.address().port);
});
```

## Echo客户端开发

由于`telnet`连接服务器使用的是`TCP协议`，所以本文对应的客户端需要使用NodeJs开发。

client.js

```js
const dgram = require('dgram');

const socket = dgram.createSocket('udp4'); // 创建socket实例

socket.on('message', function(msg,sender) { // 监听收到数据
    console.log('接收到%s:%d的消息:%s',sender.address,sender.port,msg.toString());
    socket.close();
});

socket.send('hello',10000,function(err) { // 向目标端口发送数据
    if(err) {
        console.log('发送错误', err);
        return;
    }
    console.log('发送成功');
});
```

## 执行

1. 终端执行`node server.js`，输出
   
    ```text
    服务器正在监听 0.0.0.0:10000
    ```
2. 终端执行`node client.js`，输出

    ```text
    发送成功
    接收到127.0.0.1:10000的消息:server: hello
    ```

3. 服务端输出:

    ```text
    127.0.0.1:50577 => hello
    ```

## 结语

NodeJs UDP服务端与客户端开发到此结束，但是使用UDP的情况下，数据包确认、流量控制等等操作都需要程序员手动完成，这一方面确实挺复杂的，没有什么特殊的要求的话使用TCP即可。

