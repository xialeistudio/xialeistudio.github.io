---
title: nginx反向代理websocket支持跨域
layout: post
category:
- nginx
tag:
- nginx
- cors
---
今天在调试远程websocket的时候发现控制台提示跨域错误，看到浏览器`Network`中方向响应头没有跨域方面的数据。

nginx做websocket反向代理挺简单的

```
  proxy_set_header Upgrade $http_upgrade;
  proxy_set_header Connection "upgrade";
  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  proxy_set_header Host $host;
  proxy_http_version 1.1;
  proxy_pass http://socket服务器地址;
```
但是如此配置除非后端服务器支持跨域，否则socket无法跨域。
其实nginx支持的`add_header`指令已经可以添加跨域相关头了

完整配置如下
```
  add_header "Access-Control-Allow-Origin" "$http_origin";
  add_header "Access-Control-Allow-Credentials" "true";
  add_header "Access-Control-Allow-Methods" "GET, POST, OPTIONS, DELETE, PATCH, PUT, HEAD";
  add_header "Access-Control-Allow-Headers" "DNT,X-Mx-ReqToken,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type";

  proxy_set_header Upgrade $http_upgrade;
  proxy_set_header Connection "upgrade";
  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  proxy_set_header Host $host;
  proxy_http_version 1.1;
  proxy_pass http://socket服务器地址;
```

再看到浏览器响应头时发现已经成功返回跨域头了。