---
slug: node-syslogd
date: 2017-04-27
title: 使用NodeJs提供syslogd服务端
categories: 
- Engineering
---
syslog作为Linux发行版一个重要组件，相信大家都不陌生，而如果每台服务器都独立使用一份的话，不能做到日志统一管理，对于以后的日志查询不太方便。
syslog有标准的协议格式，这里不做讨论，有兴趣的可以基于协议的报文结构使用socket编程实现。

## 部署服务端

本文使用Nodejs来部署一台syslog服务端。
1. 终端执行
    ```
    npm init -y
    npm install syslogd --save
    ```
2. index.js
    ```javascript
    const syslogd = require('syslogd');
    const server = syslogd(data => {
       console.log(data);
    });
    server.listen(514,e => {
     if(e!==null) {
       console.error(e);
       return;
     }
     console.log('listen on 514');
    });
    ```
3. 终端执行
    ```
    node index.js
    ```

好了，我们的syslog服务器已经部署完毕了。是不是很简单呢~

## nginx日志接入syslog
打开nginx配置文件

```
server {
    ...
    access_log syslog:server=127.0.0.1;
    ...
}
```
重启nginx就可以发现nodejs服务端已经成功接收日志信息了。
*注意：是重启不是reload*