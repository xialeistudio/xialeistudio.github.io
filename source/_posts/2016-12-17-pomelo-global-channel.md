---
layout: post
title: pomelo-global-channel-plugin的使用
categories:
- Engineering
tags:
- pomelo
---
pomelo应用中channel默认是**不可以跨进程**的，来看一下现在服务器的配置：

```json
{
  "development": {
    "connector": [
      {
        "id": "connector",
        "host": "127.0.0.1",
        "port": 3150,
        "clientHost": "127.0.0.1",
        "clientPort": 3010,
        "frontend": true
      }
    ],
    "chat": [
      {
        "id": "chat-1",
        "host": "127.0.0.1",
        "port": 4001
      },
      {
        "id": "chat-2",
        "host": "127.0.0.1",
        "port": 4002
      }
    ]
  }
}
```

可以看到使用了两台**chat**服务器，该服务器进行具体的消息接收以及消息推送。

在聊天时，由于后端**chat服务器**不止一台，所以后面通过**app.get('channelService')**时发现channel没同步，查阅文档发现，pomelo提供的**pomelo-global-channel-plugin**插件，用来在**app生命周期**中管理全局channel。

可以说，这个插件目前可以解决我们的问题了。

## 安装

```bash
npm install pomelo-globalchannel-plugin --save
```

该插件依赖**redis**来实现跨服务器数据存储。

## 配置
在**config**目录下新建 **redis.json**文件

```json
{
  "development": {
    "host": "localhost",
    "port": 6379
  },
  "production": {
    "host": "localhost",
    "port": 6379
  }
}
```

## 编码
### app.js

```javascript
var pomelo = require('pomelo');
var globalChannel = require('pomelo-globalchannel-plugin');
var path = require('path');
/**
 * Init app for client.
 */
var app = pomelo.createApp();
app.set('name', 'demo');

// app configuration
app.configure('production|development', 'connector|chat', function() {
  app.set('connectorConfig',
    {
      connector: pomelo.connectors.sioconnector,
      //websocket, htmlfile, xhr-polling, jsonp-polling, flashsocket
      transports: ['websocket'],
      heartbeats: true,
      closeTimeout: 60,
      heartbeatTimeout: 60,
      heartbeatInterval: 25
    });
});
// global channel
app.loadConfig('redis', path.resolve('./config/redis.json'));
// redis
app.use(globalChannel, {
  globalChannel: app.get('redis')
});
// start app
app.start();

process.on('uncaughtException', function(err) {
  console.error(' Caught exception: ' + err.stack);
});
```

### app/servers/chat/remote/remote.js
rpc路由为**chat.remote.[method]**

```javascript
/**
 * @author xialeistduio<1065890063@qq.com>
 * @date 16-12-17
 */
'use strict';
module.exports = function(app) {
  return new Handler(app);
};

var Handler = function(app) {
  this.app = app;
  this.channel = app.get('globalChannelService');
};
/**
 * 加入聊天室
 * @param channelName
 * @param userId
 * @param connectorServerId
 * @param callback
 */
Handler.prototype.join = function(channelName, userId, connectorServerId, callback) {
  this.channel.add(channelName, userId, connectorServerId);
  var param = {
    userId: userId
  };
  this.channel.pushMessage('connector', 'onJoin', param, channelName);
  callback();
};
/**
 * 退出聊天室
 * @param channelName
 * @param userId
 * @param connectorServerId
 * @param callback
 */
Handler.prototype.leave = function(channelName, userId, connectorServerId, callback) {
  this.channel.leave(channelName, userId, connectorServerId);
  var param = {
    userId: userId
  };
  this.channel.pushMessage('connector', 'onLeave', param, channelName);
  callback();
};
```

可以看到使用的是**globalChannelService**，通过**add**,**leave**方法实现用户加入，退出channel。


### app/servers/connector/handler/handler.js
前端路由为**connector.handler.[method]**

```javascript
module.exports = function(app) {
  return new Handler(app);
};

var Handler = function(app) {
  this.app = app;
  this.sessionService = app.get('sessionService');
};
/**
 * 进入聊天
 * @param msg
 * @param session
 * @param next
 */
Handler.prototype.login = function(msg, session, next) {
  // 参数检测
  if (!msg.userId || !msg.lessonId) {
    return next(null, {code: 1, message: '缺少参数'});
  }
  // 是否已登录
  if (!!this.sessionService.getByUid(msg.userId)) {
    return next(null, {code: 1, message: '用户已登录'});
  }

  var self = this;
  session.bind(msg.userId);
  session.set('lessonId', msg.lessonId);
  session.push('lessonId', function(e) {
    e && console.error(e);
  });
  // 用户退出监听
  session.on('closed', function(session) {
    self.app.rpc.chat.remote.leave(session, session.get('lessonId'), session.uid, self.app.get('serverId'), null);
  });
  // 加入聊天室
  self.app.rpc.chat.remote.join(session, msg.lessonId, msg.userId, this.app.get('serverId'), function() {
    next(null, {code: 0, message: '登录成功'});
  });
};
```

### app/servers/chat/handler/handler.js
前端路由为**chat.handler.[method]**

```javascript
/**
 * @author xialeistduio<1065890063@qq.com>
 * @date 16-12-17
 */
'use strict';
module.exports = function(app) {
  return new Handler(app);
};

var Handler = function(app) {
  this.app = app;
  this.channel = app.get('globalChannelService');
};
/**
 * 发送消息
 * @param msg
 * @param session
 * @param next
 */
Handler.prototype.send = function(msg, session, next) {
  if (session.uid === null) {
    return next(null, {code: 1, message: '用户未登录'});
  }
  var lessonId = session.get('lessonId');
  // 发送消息
  msg.userId = session.uid;
  this.channel.pushMessage('connector', 'onMessage', msg, lessonId, null, function() {
    next(null, {message: '发送成功', code: 0});
  });
};
```

## 单元测试
本测试使用**mocha**以及**should**进行
### 安装依赖
由于单元测试在nodejs环境执行，而官方的pomelo客户端是浏览器的，所以需要下载nodejs版本的

```bash
npm install x.pomelo-client --save-dev
```

### 测试脚本

```javascript
/**
 * @author xialeistduio<1065890063@qq.com>
 * @date 16-12-17
 */
'use strict';
var should = require('should');
var pomelo = require('x.pomelo-client');
describe('pomelo', function() {
  this.timeout(60000);
  it('connector::connect', function(done) {
    pomelo.init({
      host: 'localhost',
      port: 3010,
      log: true
    }, function() {
      done();
    });
  });
  it('connector::login', function(done) {
    pomelo.on('onJoin', function(data) {
      if (data.userId === 'xialei') {
        done();
      }
    });
    pomelo.request('connector.handler.login', {userId: 'xialei', lessonId: 4}, function(data) {
      should(data.code).be.exactly(0);
    });
  });
  it('chat::send', function(done) {
    pomelo.on('onMessage', function(data) {
      if (data.type === 1 && data.content === '哈哈') {
        done();
      }
    });
    pomelo.request('chat.handler.send', {type: 1, content: '哈哈'}, function(data) {
      should(data.code).be.exactly(0);
    });
  });
});
```

### 执行测试

```bash
mocha
```