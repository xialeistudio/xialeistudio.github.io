---
layout: post
title: 阿里云ECS服务器phpmailer发信失败解决方法
date: 2014-09-06 20:03:24.000000000 +08:00
type: post
published: true
status: publish
categories:
- php
tags:
- phpmailer
- aliyun
---
phpmailer之前一直在用，一般都是采用smtp登录服务器的方式进行发信，今天在本地windows主机测试也能发信成功，但是到线上去就不行了，提示“连接smtp服务器失败”。
首先可以排除的是代码方面的错误，那么剩下就知道服务器的问题了。

根据这个错误，可以想到有几种问题:
1. 服务器ping不通，做Ping测试的时候是通的   
2. 服务器端口没开，用telnet测试的时候也是这样的

后来在服务器上用php代码测试163邮箱发现可以发信，但是腾讯的就不行，看了下邮箱配置发现是SSL的问题，然后在服务器上输出phpinfo()发现没有openssl扩展。   
接下来就是安装扩展了。   
1. 首先进到php的源码包，前往**ext/openssl**目录
2. 执行 phpize 这个会自动配置
3. 然后执行 

```bash
./configure --with-openssl -with-php-config=/usr/local/php/bin/php-config
make
make install
```

这里模块安装就完成了，但是需要编辑 **/etc/php.ini**加上

```
extension=openssl.so
```

重启 web 服务器就可以了。经过测试，服务器上SSL发信也能成功进行