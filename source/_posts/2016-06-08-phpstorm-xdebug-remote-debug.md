---
layout: post
title: phpstorm+xdebug远程调试服务器PHP代码
date: 2016-06-08 12:25:21.000000000 +08:00
type: post
published: true
status: publish
categories:
- backend
- php
tags:
- xdebug
---
phpstorm+xdebug如何调试本地代码应该都熟悉了。本文说的是如何调试线上服务器的代码。本文写作时服务器的PHP环境是lnmp1.2。

## 服务器配置
### 安装debug

```bash
pecl install xdebug
```

### 编辑php.ini
编辑 **/usr/local/php/etc/php.ini**，在末尾加上以下代码：

```
[Xdebug]
zend_extension="xdebug.so"
xdebug.remote_enable=1
xdebug.remote_handler=dbgp
xdebug.remote_host=【调试终端所在的公网IP】
xdebug.remote_port=9000
xdebug.remote_autostart=1
xdebug.idekey="PHPSTORM"
```

本文中调试终端为**PHPSTORM**，所以本地公网IP为**remote_host**的值   
[查看本地公网IP](http://www.ip138.com)   
更改配置完毕后终端执行:

```bash
lnmp php-fpm reload
```

## IDE配置
### 配置server
Setting => Languages & Frameworks=>PHP=>Servers，
![Server配置](https://og5r5kasb.qnssl.com/wp-content/uploads/2016/06/QQ%E5%9B%BE%E7%89%8720160608121441.png)   
### 配置DBGp Proxy
Settings => Languages & Frameworks => PHP => Debug => DBGp Proxy
![DBGp Proxy](https://og5r5kasb.qnssl.com/wp-content/uploads/2016/06/QQ%E5%9B%BE%E7%89%8720160608121659.png)   
其中红框处需要和服务器的xdebug配置文件一致。
## 路由端口映射
由于大部分朋友公司都有路由器的，所以本机IP是局域网IP，这里需要将路由器的端口映射到本地。具体规则如下：

```
服务器Xdebug端口（路由器公网端口） => 本地端口，笔者这里把路由器的9000端口映射到本地的9000端口。
```

## 开始调试
+ 打开项目的运行配置，选择“PHP Web Application”   
![开始调试](https://og5r5kasb.qnssl.com/wp-content/uploads/2016/06/QQ%E5%9B%BE%E7%89%8720160608122018.png)   
笔者服务器这里是https的，所以加了https，各位读者请根据实际情况填写网址。
+ 点击IDE的“电话”图标开启远程监听。   
![监听](https://og5r5kasb.qnssl.com/wp-content/uploads/2016/06/QQ%E6%88%AA%E5%9B%BE20160608122148.png)   
+ 代码断点   
![代码断点](https://og5r5kasb.qnssl.com/wp-content/uploads/2016/06/QQ%E6%88%AA%E5%9B%BE20160608122222.png)   
+ 开始调试   
![开始调试](https://og5r5kasb.qnssl.com/wp-content/uploads/2016/06/QQ%E6%88%AA%E5%9B%BE20160608122259.png)   
+ IDE自动弹出调试窗口   
![IDE自动弹出调试窗口](https://og5r5kasb.qnssl.com/wp-content/uploads/2016/06/QQ%E6%88%AA%E5%9B%BE20160608122347.png)   