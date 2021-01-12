---
layout: post
title: linux检查端口占用
date: 2014-10-15 21:49:22.000000000 +08:00
type: post
published: true
status: publish
categories:
- backend
- linux
---

Linux启动服务时如果遇到端口占用问题时，一般有以下两种解决方案：

1. 新启动的服务更改端口号启动
2. 杀掉老的进程

## Linux检查端口占用命令

```bash
    netstat -lnp | grep 80
```

80为端口号，查找到占用端口的进程ID后用kill杀掉即可。