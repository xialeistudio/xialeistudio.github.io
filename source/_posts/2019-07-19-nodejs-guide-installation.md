---
title: NodeJs简明教程(2)
date: 2019-07-19 10:15:29
categories:
- backend
- nodejs
---

> NodeJs简明教程将从零开始学习NodeJs相关知识，助力JS开发者构建全栈开发技术栈！

关注获取更多`NodeJs精品文章`
![二维码](https://more-happy.ddhigh.com/FuFpZh9QTZVatcBtupR4MtOGPGTJ?imageView2/1/w/200)

本文是NodeJs简明教程的第二篇，将介绍NodeJs在不同操作系统下的安装操作。

## 官网

[https://nodejs.org](https://nodejs.org/en/)

由于国内的网络原因，官网可能访问速度有点慢，推荐直接使用淘宝镜像源下载

## 淘宝镜像源

[https://npm.taobao.org/mirrors/node](https://npm.taobao.org/mirrors/node)，这里是所有版本/所有操作系统的NodeJs安装包。

本系列文章使用 **latest-v10.x**，也就是 **10.x** 的NodeJs版本

1. 进入[https://npm.taobao.org/mirrors/node/latest-v10.x/](https://npm.taobao.org/mirrors/node/latest-v10.x/)
2. 可以看到最新的版本号为 **node-v10.16.0**

## Windows安装

1. **64位** 系统选择[node-v10.16.0-x64.msi](https://npm.taobao.org/mirrors/node/latest-v10.x/node-v10.16.0-x64.msi)
2. **32位** 系统选择[node-v10.16.0-x86.msi](https://npm.taobao.org/mirrors/node/latest-v10.x/node-v10.16.0-x86.msi)
3. 双击即可完成安装
4. 安装完毕之后打开`cmd`执行`node -v`，显示版本号即为安装成功，安装失败的读者可以在下方留言

## Mac安装

### PKG安装包安装

1. 选择[node-v10.16.0.pkg](https://npm.taobao.org/mirrors/node/latest-v10.x/node-v10.16.0.pkg)
2. 双击即可完成安装
3. 安装完毕之后打开`终端`执行`node -v`，显示版本号即为安装成功，安装失败的读者可以在下方留言

### Homebrew安装

1. `brew install node`
2. 安装完毕之后打开`终端`执行`node -v`，显示版本号即为安装成功，安装失败的读者可以在下方留言

## Linux安装

1. 选择[node-v10.16.0-linux-x64.tar.gz](https://npm.taobao.org/mirrors/node/latest-v10.x/node-v10.16.0-linux-x64.tar.gz)下载文件
2. 执行`wget https://npm.taobao.org/mirrors/node/latest-v10.x/node-v10.16.0-linux-x64.tar.gz`
3. 执行`tar xf node-v10.16.0-linux-x64.tar.gz`解压
4. 执行`mv node-v10.16.0-linux-x64 /opt/node`移动到`/opt`目录
5. 执行`echo "export PATH=/opt/node/bin:$PATH" >> ~/.bashrc`编辑`PATH`环境变量
6. 执行`source ~/.bashrc`更新环境变量
7. 执行`node -v`，显示版本号即为安装成功，安装失败的读者可以在下方留言
