---
title: NodeJs简明教程(3)
date: 2019-07-19 11:04:46
categories:
- nodejs
tags:
- javascript
- nodejs guide
---


> NodeJs简明教程将从零开始学习NodeJs相关知识，助力JS开发者构建全栈开发技术栈！

本文是NodeJs简明教程的第三篇，将介绍NodeJs自带HTTP模块服务器相关的基本操作。

## HTTP模块介绍

以下是官方原文[1]：

> The HTTP interfaces in Node.js are designed to support many features of the protocol which have been traditionally difficult to use. In particular, large, possibly chunk-encoded, messages. The interface is careful to never buffer entire requests or responses — the user is able to stream data.

大致意思就是：

> NodeJs的HTTP模块旨在支持传统上HTTP协议难以使用的许多功能，让这些功能或者特性能够使用简单的API进行调用。

## HTTP模块服务器开发

### 代码示例

以下是NodeJs最简单的HTTP服务器示例:

1. 新建`index.js`
2. 编码

    ```js
    const http = require('http');

    const server = http.createServer((req, res) => {
        console.log('%s %s', req.method, req.url)
        res.end(JSON.stringify(req.headers))
    })

    server.listen(8080, () => console.log('listen on 8080'))
    ```

3. 打开终端或者控制台，执行 `node index.js`，终端或控制台会输出`listen on 8080`，此时HTTP服务器已经启动，如果启动失败，可以在下方留言
4. 打开浏览器访问 `http://localhost:8080`，笔者输出如下：
    
    ```json
    {
        "host": "localhost:8080",
        "connection": "keep-alive",
        "cache-control": "max-age=0",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
        "dnt": "1",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
    }
    ```
    
### 代码说明

1. NodeJs采用 **CMD模块系统**，**require** 用来加载模块，本例中加载了**NodeJs自带的http模块**以使用其中的功能
2. `http.createServer`函数创建了一个 **HTTP服务器**，并配置了请求回调函数，在本系列的第一篇文章中说到事件驱动是需要回调函数进行监听的。
3. `server.listen`是监听系统端口，第二个参数是**监听成功的回调函数**

### req对象

服务器收到的HTTP请求对象，以下是常用的属性或方法：

1. `req.url` 本次请求的路径(不包含域名)
2. `req.headers` 本次请求的请求头
3. `req.httpVersion` 本次请求的`HTTP协议版本号`
4. `req.method` 本次请求的请求方法,有`GET/POST/PUT等等`
5. `on()` 监听请求体数据 `POST/PUT/PATCH`方法会有请求体

### res对象

res对象是req请求对象相应的响应对象，HTTP协议涉及是`请求-应答`模型，一次请求对应一次应答。

以下是常用的属性或方法：

1. `res.writeHead` 输出`响应状态码`，`状态码说明`以及`多个HTTP响应头`
2. `res.end` 输出数据并结束本次响应
3. `res.write` 输出`部分内容(chunk)`
4. `res.setHeader` 输出`单个响应头`

### 请求路由

NodeJs自带的HTTP服务器是没有路由功能的，也是就说，根据请求的URI来执行不同的逻辑需要开发者手动去做

```js
const http = require('http');

const server = http.createServer((req, res) => {
    if (req.url === '/') {
        res.end('index');
        return;
    }
    if (req.url === '/user') {
        res.end('user');
        return;
    }
})

server.listen(8080, () => console.log('listen on 8080'));
```

1. 执行`node index.js`
2. 浏览器访问 [http://localhost:8080/](http://localhost:8080/) 会输出`index`
3. 浏览器访问 [http://localhost:8080/user](http://localhost:8080/user) 会输出`user` 

### 读取请求参数

#### 读取GET请求参数

```js
const http = require('http');
const url = require('url');
const qs = require('querystring');

const server = http.createServer((req, res) => {
    const parsed = url.parse(req.url);
    const query = qs.parse(parsed.query);
    res.end(JSON.stringify(query));
})

server.listen(8080, () => console.log('listen on 8080'));
```

1. 执行`node index.js`
2. 浏览器访问 [http://localhost:8080/?a=x&b=2&c[]=1&c[]=2](http://localhost:8080/?a=x&b=2&c[]=1&c[]=2)
3. 显示
   
    ```json
   {
        "a": "x",
        "b": "2",
        "c[]": ["1", "2"]
    }
     ```

#### 读取请求体参数

HTTP协议规范中POST/PUT/PATCH都可以携带请求体，NodeJs HTTP服务器接收请求体代码如下：

```js
const http = require('http');
const url = require('url');
const qs = require('querystring');

const server = http.createServer((req, res) => {
    let data = Buffer.alloc(0);
    req.on('data', (buffer) => {
        data = Buffer.concat([data, buffer]);
    })
    req.on('end', () => {
        res.end(data.toString())
    })
})

server.listen(8080, () => console.log('listen on 8080'));
```

1. 执行`node index.js`
2. 使用 **postman** 发出POST请求`http://localhost:8080`，本例POST请求体为 `a=1&b=2`
3. **postman**会返回 `a=1&b=2`

## 结语

一个简单的HTTP服务器就到此结束了，当然，实际生产中该方法用的比较少，几乎都是使用框架进行开发，提高开发效率。