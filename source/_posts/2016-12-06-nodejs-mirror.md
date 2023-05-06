---
layout: post
title: NodeJs源代码镜像
date: 2016-12-06 10:54:12.000000000 +08:00
type: post
published: true
status: publish
categories:
- Engineering
---
在使用*node-gyp*的时候，由于国内网络环境不太给力，导致下载NodeJs头文件时很慢。   
利用NODEJS_ORG_MIRROR环境变量可以解决这个问题。   
Linux

```bash
vim ~/.bash_profile
NODEJS_ORG_MIRROR=https://npm.taobao.org/mirrors/node
source ~/.bash_profile
```

Windows   
1. 系统环境变量设置   
2. 添加用户变量

```bash
NODEJS_ORG_MIRROR=https://npm.taobao.org/mirrors/node
```
