---
title: Docker部署golang应用时时区问题
date: 2018-03-01 11:49:24
categories:
- engineering
---

目前golang用的基础镜像是`busybox`，由于golang交叉编译之后只有一个二进制文件，可以直接部署到容器中运行，容器镜像大小几乎等于二进制文件大小。

## 带来的问题

由于基础镜像太过精简，目前遇到的问题是将时间戳格式化为时间字符串时发现差了8个小时。

## 尝试过的解决办法

刚开始使用了Location时区相关API，但是部署到容器中发现直接报错了，因为容器中缺少相关的系统调用函数。代码如下：

```golang
loc, _ := time.LoadLocation("Asia/Shanghai")
time.Now().In(loc).Format("2006-01-02 15:04:05")
```


目前应用会部署到docker容器中，故处理办法比较原始，直接在Time对象上添加8个小时来解决时差问题。代码如下:

```golang
time.Now().Add(time.Hour * 8).Format("2006年01月02日 15:04"),
```

暂时解决了这个问题。