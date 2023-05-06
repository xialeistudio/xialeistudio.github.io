---
title: nginx泛域名解析配置
layout: post
categories:
- Engineering
---
最近一个项目需要承载高并发请求，所以在后端语言上选择了**NodeJs**，但是nodejs有时候读取不到请求的主机名，所以想到使用**nginx+nodejs**的方式进行处理。

## Nginx 配置

```text
upstream io_nodes {
        server 127.0.0.1:8081;
}

server {
        listen 80;
        listen [::]:80;
        root /var/www/html;
        server_name ~^(?<subdomain>.+).example.com;

        location / {
	    proxy_set_header Host $host;
            proxy_set_header X-AppId $subdomain;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_pass http://io_nodes;
        }
}
```

重启nginx服务器即可。nginx会将所有的 **<subdomain>.example.com** 格式的域名反向代理到本机的**8081**端口，该端口为**nodejs**监听端口。

## NodeJs 读取请求域名以及子域名名称
使用express

```javascript
var host = req.headers.host;
var appid = req.headers['x-appid'];
```
