---
layout: post
title: nginx使用goddy ssl证书
date: 2016-05-23 20:03:16.000000000 +08:00
type: post
published: true
status: publish
categories:
- Engineering
---
随着人们对网络安全要求的提高，越来越多的http站点已经转换为了https站点，保证网站在传输过程中不被监听、恶意篡改，本文将使用goddy提供的ssl证书来升级HTTPS网站。

## 生成私钥和证书请求文件
终端执行

```bash
openssl req -new -newkey rsa:2048 -nodes -keyout domain.key -out domain.csr
```

生成过程会询问几个常见问题，比如City、Country等等。   
最后会询问challenge password，输入的时候记住就可以了。   
执行完以上命令后，当前目录会多出**domain.key**和**domain.csr**文件，前者为服务器私钥，后者为证书请求文件

## Goddy证书
购买完SSL证书之后会有一个初始化过程，将第1步中的**domain.csr**文件所有内容填写到**CSR**输入框中，Goddy会检测配置等操作，操作完成之后会签发证书，点击下载即可，下载时服务器类型选择“其他”。

## Nginx配置
下载证书的时候压缩包内容类似如下图   
![压缩包](https://og5r5kasb.qnssl.com/wp-content/uploads/2016/05/QQ%E5%9B%BE%E7%89%8720160523195944.png)   

正常情况下nginx配置SSL需要key和crt文件即可。   
这里有两个crt所以需要进行证书合并操作。   
打开终端，执行以下命令：

```bash
cat 53f58e3ac2172cd5.crt gd_bundle-g2-g1.crt > domain.crt
```

证书合并完成，接下来打开Nginx的配置文件，笔者这里**证书目录**位于**/root/crt**

```
server
{
  listen 443;
  server_name domain;
  index index.html index.htm default.html default.htm;
  root /home/wwwroot/domain;
  
  location = /favicon.ico {
    log_not_found off;
    access_log off;
  }
  ssl on;
  ssl_certificate /root/crt/domain.crt;
  ssl_certificate_key /root/crt/domain.key;
  access_log off;
}
```

保存之后，终端执行

```bash
nginx -s reload
```
