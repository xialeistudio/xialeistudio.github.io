---
layout: post
title: node-fetch请求https站点时不验证证书
categories: 
- nodejs
tags:
- node-fetch
- https
- certificate
- ssl
---
有时候https的证书验证也是挺烦的，比如自签CA签发的证书，这时候是不受信任的，直接执行https请求会报错。

```
 FetchError: request to https://dm-81.data.aliyun.com/rest/160601/ip/getIpInfo.json?ip=8.8.8.8 failed, reason: unable to verify the first certificate
      at ClientRequest.<anonymous> (node_modules/node-fetch/index.js:133:11)
      at TLSSocket.socketErrorListener (_http_client.js:258:9)
      at emitErrorNT (net.js:1256:8)
```

查阅nodejs官方文档发现有 **agent** 属性，**agent**有个可选属性**rejectUnauthorized**，设置为**false**即可取消证书有效性验证。

本文使用的是**node-fetch**模块执行请求，代码如下

```javascript
'use strict';
const fetch = require('node-fetch');
const https = require('https');
const options = {
  agent:new https.Agent({rejectUnauthorized:false})
};
fetch(`https://dm-81.data.aliyun.com/rest/160601/ip/getIpInfo.json?ip=8.8.8.8`, options)
.then(console.log)
.catch(console.error);
```

修改过后就可以成功请求了。

其他http请求模块类似处理。