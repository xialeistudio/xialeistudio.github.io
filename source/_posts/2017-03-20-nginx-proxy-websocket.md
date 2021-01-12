---
layout: post
title: nginx反向代理websocket
categories:
- backend
- nginx
---
websocket协议基于http协议升级而来，所以nginx可以直接反向代理websocket，只需要加上必要的header即可。

假设websocket监听端口为*18080*，编辑nginx配置文件：

```nginx
server {
    listen 80;
    server_name socket.example.com;
    location / {
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_pass http://127.0.0.1:18080;
    }
}
```