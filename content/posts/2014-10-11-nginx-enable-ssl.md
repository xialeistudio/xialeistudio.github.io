---
slug: nginx-enable-ssl
title: nginx服务器启用SSL访问
date: 2014-10-11 17:18:59.000000000 +08:00
categories:
- Engineering
---
## HTTP和HTTPS的区别
1. https协议需要到ca申请证书，一般免费证书很少，需要交费。 　
2. http是超文本传输协议，信息是明文传输，https 则是具有安全性的ssl加密传输协议。 　　
3. http和https使用的是完全不同的连接方式，用的端口也不一样，前者是80，后者是443。 　　
4. http的连接很简单，是无状态的；HTTPS协议是由SSL+HTTP协议构建的可进行加密传输、身份认证的网络协议，比http协议安全。

所以在涉及到账户、金钱等敏感信息交互的时候使用HTTPS是个不错的选择。   
## 申请证书
1. 申请SSL证书过程就不多说了。挺简单的，本文主要是在nginx上配置ssl证书实现https访问。   
2. 将key和证书上传到服务器。

## nginx配置

```
server {
                listen 443;
                #listen [::]:80;
                server_name passport.ddhigh.com;
                index index.html index.htm index.php default.html default.htm default.php;
                root  /home/wwwroot/passport.ddhigh.com;
                include other.conf;
                #error_page   404   /404.html;
                location ~ [^/]\.php(/|$)
                        {
                                # comment try_files $uri =404; to enable pathinfo
                                try_files $uri =404;
                                fastcgi_pass  unix:/tmp/php-cgi.sock;
                                fastcgi_index index.php;
                                include fastcgi.conf;
                                #include pathinfo.conf;
                        }
                location ~ .*\.(gif|jpg|jpeg|png|bmp|swf)$
                        {
                                expires      30d;
                        }
                location ~ .*\.(js|css)?$
                        {
                                expires      12h;
                        }
                ssl on;
                ssl_certificate /root/crt/server.crt;
                ssl_certificate_key /root/crt/server.key;
                access_log  /home/wwwlogs/passport.ddhigh.com.log  access;
}
```

**/root/crt**是我的证书目录，各位读者可以根据实际情况更改。