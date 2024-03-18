---
slug: mamp-install-php-extension
title: MAMP下使用pecl安装PHP扩展
date: 2016-02-16 15:45:25.000000000 +08:00
categories:
- Engineering
tags:
- mamp
---
之前写过一篇在Mac下搭建PHP开发环境的文章，[Mac搭建PHP开发环境]({% post_url 2016-02-16-mac-php-env %})，但是此种方式搭建的PHP有弊端，由于默认不带PHP源码，所以在使用pecl安装扩展时会报错。

## 测试安装扩展

```bash
sudo pecl install mongo
```

运行起来后会报形如“php.h not found”的错误，因为MAMP默认是不带PHP源码包的。   
## 配置扩展安装环境
按照如下步骤将源码包集成以便于安装扩展：
1.在web目录下添加index.php文件，内容如下：

```php
<?php
phpinfo();
```

2.打开浏览器访问该php文件，记录PHP版本，本文暂定**PHP版本A**。   
3.打开终端，输入以下命令：

```php
php -v
```

记录PHP版本，本文暂定**PHP版本B**。   
4.如果PHP版本A不等于PHP版本B，在终端执行以下命令：

```bash
sudo rm -rf /usr/bin/php
sudo rm -rf /usr/bin/phpize
sudo rm -rf /usr/bin/php-config
sudo rm -rf /usr/bin/pecl
 
ln -s /Application/MAMP/bin/php/php[PHP版本A]/bin/php /usr/bin/php
ln -s /Application/MAMP/bin/php/php[PHP版本A]/bin/php-config /usr/bin/php-config
ln -s /Application/MAMP/bin/php/php[PHP版本A]/bin/phpize /usr/bin/phpize
ln -s /Application/MAMP/bin/php/php[PHP版本A]/bin/pecl /usr/bin/pecl
```

请替换**[PHP版本A]**为步骤2中的版本，如**5.5.18**   
执行完以上命令之后，命令行模式和浏览器模式的PHP都是一致的了。   
5.下载PHP源码包，打开浏览器访问如下网址 http://cn2.php.net/get/php-**[PHP版本A]**.tar.gz/from/this/mirror。   
6.将下载的压缩包解压到 /Application/MAMP/bin/php/php**[PHP版本A]**/include/php 中。   
7.在终端执行以下命令：

```bash
cd /Application/MAMP/bin/php/php[PHP版本A]/include/php
./configure
```

此时PHP源码包已经配置正常了，头文件也可以正常调用了。   
8.在终端执行：

```bash
sudo pecl install mongo
```

扩展安装成功后，编辑*/Application/MAMP/bin/php/php*[PHP版本A]*/conf/php.ini* 在最后添加：

```
extension=mongo.so
```

9.由于命令行模式和浏览器模式中加载的php.ini并不是同一个文件，所以需要用软连接的方式处理下。终端执行：

```bash
php -i|grep ini
```

查看**Loaded ini file**路径，本文假设为**PHP配置文件A**。   
10.备份**PHP配置文件A**，终端执行：

```bash
ln -s /Application/MAMP/bin/php/php[PHP版本A]/conf/php.ini PHP配置文件A
```

11.终端执行：

```bash
php -i|grep ini
```

此时该路径应该和浏览器中看到的是一致的了。

## 安装扩展
1. sudo pecl install **[扩展名]**
2. 编辑 /Application/MAMP/bin/php/php**[PHP版本A]**/conf/php.ini 加载扩展
3. 重启Web服务器