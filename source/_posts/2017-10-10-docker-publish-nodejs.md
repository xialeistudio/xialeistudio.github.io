---
title: 使用Docker来部署NodeJs应用
layout: post
categories:
- Engineering
---

Docker的环境无关性以及自动化特性实在是令人称赞，最近遇到的一个问题是，NodeJs使用8.x版本开发，但是线上服务器是7.x的，这时候又不能动线上的应用。
于是想到了使用Docker来部署NodeJs，服务器是Ubuntu的。
## 安装Docker
```
apt install docker.io
```
## Dockerfile编写
由于默认的dockhub速度非常慢导致下载镜像慢，而且镜像下来的Ubuntu apt源又是国外的，简直是慢上加慢，本文使用[daocloud.io的Ubuntu镜像](https://www.daocloud.io/)以及[阿里云的Ubuntu源](http://mirrors.aliyun.com/)

```dockerfile
FROM daocloud.io/library/ubuntu
MAINTAINER xialeistudio<xialeistudio@gmail.com>

ENV PATH $PATH:/opt/node/bin
ENV PORT 80
ENV HOST 0.0.0.0
# prepare
ADD sources.list /etc/apt/sources.list
RUN apt update
RUN apt install wget gcc python git -y
# nodejs
RUN wget https://npm.taobao.org/mirrors/node/latest-v8.x/node-v8.6.0-linux-x64.tar.gz
RUN tar xf node-v8.6.0-linux-x64.tar.gz
RUN mv node-v8.6.0-linux-x64 /opt/node
# app
RUN mkdir app
ADD . /root/app
WORKDIR /root/app
RUN /opt/node/bin/npm install --registry=https://registry.npm.taobao.org
# start app
ENTRYPOINT ["npm","start"]
```
指令解释一下
1. 指定模板镜像
2. 维护者信息，这是本人写的，所以署名为本人
3. 环境变量定义
4. 复制宿主机当前目录的sources.list到docker中的/etc/apt目录用来替换默认的Ubuntu源
5. 更新apt并安装必要软件
6. 从淘宝镜像站下载nodejs二进制版本
7. 解压并移动到/opt/node目录
8. 创建应用目录，并把宿主机当前文件夹下的所有文件拷贝到docker景象中
9. 使用淘宝镜像安装npm包
10. 启动APP

## build镜像
```
docker build -t demo .
```
运行完毕后就可以使用*docker images*查看镜像了

## 启动容器
```
docker run -d -p 127.0.0.1:7001:80 demo
```
这时候容器已经启动，并通过端口转发监听在宿主机的7001端口上，配合nginx做反向代理就可以部署一个公网应用了。
不管你容器中部署何种版本的NodeJs都不会对宿主机造成影响，这点很重要。