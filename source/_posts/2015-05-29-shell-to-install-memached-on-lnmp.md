---
layout: post
title: lnmp一键安装memcached的shell脚本
date: 2015-05-29 22:19:08.000000000 +08:00
type: post
published: true
status: publish
categories:
- backend
- linux
---
通过LNMP安装脚本安装的PHP环境默认是不带Memcached支持的（是memcached不是memcache），百度一下memcached的安装方法，发现基本都是memcache的，其实这是两个不同的东西。

而memcached是pecl的项目，所以需要到pecl网站上去下载最新的memcached安装包。

为了方便多台服务器的安装，本人整理成了一个sh脚本进行安装，当然,php-config路径和phpize路径需要改下（如果使用LNMP脚本安装的话则不用改）

```bash
#!/bin/bash
wget https://launchpad.net/libmemcached/1.0/0.53/+download/libmemcached-0.53.tar.gz
tar xvfz libmemcached-0.53.tar.gz
cd libmemcached-0.53
./configure --prefix=/usr/local/libmemcached --enable-sasl
make && make install
wget http://pecl.php.net/get/memcached-2.0.0.tgz
tar zvxf memcached-2.0.0.tgz
cd memcached-2.0.0/
phpize
./configure --enable-memcached --with-php-config=/usr/local/php/bin/php-config --with-libmemcached-dir=/usr/local/libmemcached --enable-memcached-sasl
make && make install
```
