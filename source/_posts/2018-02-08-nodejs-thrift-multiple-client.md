---
title: nodejs thrift多路复用客户端
date: 2018-02-08 15:35:48
categories:
- engineering
tags:
- thrift
---

[官网nodejs示例](http://thrift.apache.org/tutorial/nodejs)中只实现了服务端是单一service的情形，而对于服务端属于`多个服务复用一个连接地址`的例子却未实现。

查看thrift的nodejs库源码发现实际上还是支持的。以下来展示调用单一服务和多个服务的区别。

## 单一服务

```javascript
var thrift = require('thrift');
var Calculator = require('./gen-nodejs/Calculator');
var ttypes = require('./gen-nodejs/tutorial_types');
const assert = require('assert');

var transport = thrift.TBufferedTransport;
var protocol = thrift.TBinaryProtocol;

var connection = thrift.createConnection("localhost", 9090, {
  transport : transport,
  protocol : protocol
});
var client = thrift.createClient(Calculator, connection);
// 已经可以调用client方法
```

## 复用服务

```javascript
var thrift = require('thrift');
var Calculator = require('./gen-nodejs/Calculator');
var ttypes = require('./gen-nodejs/tutorial_types');
const assert = require('assert');

var transport = thrift.TBufferedTransport;
var protocol = thrift.TBinaryProtocol;

var connection = thrift.createConnection("localhost", 9090, {
  transport : transport,
  protocol : protocol
});
const m = new thrift.Multiplexer(); // 关键
const client = m.createClient('calculator', Calculator, connection); // calculator为服务端声明的服务名称
// 已经可以调用client方法
```

经过测试，以上代码能与golang实现的服务端正常通信。