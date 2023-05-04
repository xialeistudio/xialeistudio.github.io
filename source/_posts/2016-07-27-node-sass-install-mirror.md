---
layout: post
title: node-sass安装镜像
date: 2016-07-27 22:37:54.000000000 +08:00
type: post
published: true
status: publish
categories:
- engineering
---
## 安装
npm安装node-sass模块的时候，会卡在 node scripts/install.js这里，因为要去github.com上下载源码，众所周知的原因，国内的网络上github.com速度太不稳定了，所以安装很慢。

这里推荐一种极速安装的方法，当然还是使用万能的淘宝镜像源。

打开~/.npmrc（windows用户打开 c:\Users\当前用户名\.npmrc）增加一行

```bash
SASS_BINARY_SITE=https://npm.taobao.org/mirrors/node-sass/
```

终端执行:

```bash
npm install node-sass
```

## 注意
如果使用了较高版本的nodejs或者node-sass，此时镜像可能还未同步完成，所以请大家前往此链接查看受支持的node-sass:

```
https://npm.taobao.org/mirrors/node-sass/
```

该网页列出来的即为当前受支持的node-sass版本，开发的时候一般使用最新版本，本文写作时**node-sass**最新版本为**v4.0.0**，点击**v4.0.0**链接：

```
https://npm.taobao.org/mirrors/node-sass/v4.0.0/
```

可以看到新网页中有一个文件列表，后缀为**.node**的文件即位编译好的，文件名格式如下:

```
[platform]-[architecture]-[nodejs version]_binding.node
```

+ platform 操作系统平台 **darwin**为**Mac OS X**，**linux**为**linux**，**win32**为**windows**
+ architecture 系统架构 目前有**x64**,**ia32**
+ nodejs version nodejs版本号，取全版本号的前两位，比如**4.6.x**为**46**，**5.1.x**为**51**

所以大家如果发现本网页没有出现你平台所需要的二进制文件，镜像也需要从github拉取数据，此时安装node-sass是不会加速的。