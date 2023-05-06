---
layout: post
title: mac 10.11安装php-mongo扩展踩过的坑
date: 2015-12-15 19:52:30.000000000 +08:00
type: post
published: true
status: publish
categories:
- Engineering
---
## pecl的安装
本文采用的是 pecl 的方式安装。   
如果系统执行 pecl 命令报错的话，请打开终端，执行以下命令

```bash
curl -o go-pear.phar http://pear.php.net/go-pear.phar
php go-pear.phar
```

接下来的询问过程直接回车即可，成功之后执行以下命令

```bash
sudo ln -s /Users/[用户名]/pear/bin/pear /usr/bin/pear
sudo ln -s /Users/[用户名]/pear/bin/pecl /usr/bin/pecl
```

## mongo扩展的安装

```bash
sudo pecl install mongo
```

接下来会询问是不是启用 sasl 认证，输入**[no]**回车，接下来是编译了，不出意外的话会编译出错，大致错误是

```bash
<openssl/evp.h> file not found
```

简而言之就是 openssl/evp.h 头文件查找失败，由于用 尖括号括起来的头文件，编译器会去系统路径查找，而 mac 下默认的路径是 /usr/include，使用终端ls查看之后发现确实没有openssl文件夹。

## openssl的安装

```bash
sudo brew install openssl
```

如果提示**brew**命令不存在，可以通过以下代码安装**Homebrew**，终端执行

```bash
ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

安装完成后重新安装**openssl**即可。

## link头文件
通过brew命令安装完openssl之后会自动link一次，但是重新执行mongo的安装命令时依旧出错。猜想应该是头文件没有复制过去，这时候需要手动ln一下，终端执行

```bash
ln -s /usr/local/Cellar/openssl/1.0.2d_1/include/openssl /usr/include/openssl
```

如果你的openssl版本不一致，请自行替换，执行完该命令之后再安装mongo就不会有问题了。

## 启用扩展
MAMP的php很有意思，web版本的配置文件在

```bash
/Library/Application Support/appsolute/MAMP PRO/conf/php.ini
```

cli版本的配置文件在（请通过终端执行 php -v 获取PHP版本）

```bash
/Applications/MAMP/bin/php/php5.5.10/conf/php.ini 
```

在这两个文件都加上

```bash
extesion=mongo.so 
```

重启MAMP即可