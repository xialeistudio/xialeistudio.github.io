---
layout: post
title: PHP7编译sphinx扩展
categories:
- engineering
---
最近在做基于sphinx的全文搜索引擎，使用PHP进行数据读取，但是服务器使用的PHP版本是PHP7，pecl.php.net中没有提供PHP7的版本。手痒点到source code中看了一下。
看到源代码中有的**headers**中有个**php7**的，点击**shortlog**进去看了一下，最新更新日期是2017-02-10，挺新的，应该是针对PHP7开发的版本，只不过未发布编译版本，想着linux下的软件有源代码基本都能自行编译。故选择了最新的PHP7快照下载。
## 开始安装

```bash
wget http://git.php.net/?p=pecl/search_engine/sphinx.git;a=snapshot;h=339e123acb0ce7beb2d9d4f9094d6f8bcf15fb54;sf=tgz
tar xvfz sphinx-339e123.tar.gz
cd sphinx-339e123
phpize
./configure
make && make install
```

安装完毕后会在PHP的配置文件目录多出sphinx.ini，在扩展目录多出sphinx.so文件。终端执行
```bash
phpenmod sphinx
```

即可启用扩展。

## 本文服务器环境
Ubuntu16.04 Server + PHP7.0(使用apt安装)