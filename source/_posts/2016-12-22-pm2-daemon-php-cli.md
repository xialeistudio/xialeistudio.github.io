---
layout: post
title: 使用PM2守护PHP命令行程序
categories:
- node
tags:
- php
- pm2
- yii2
---
pm2是nodejs的一个模块，用来进行进程管理，刚开始以为只能做nodejs脚本的管理，后来发现通过配置之后也可以实现**任意进程**的守护。
## 安装

```bash
npm install pm2 -g
```

## 使用
### 启动
+ 启动php文件

```bash
pm2 start app.php
```

启动完成后会输出

```text
┌───────────────┬────┬──────┬───────┬────────┬─────────┬────────┬─────┬───────────┬──────────┐
│ App name      │ id │ mode │ pid   │ status │ restart │ uptime │ cpu │ mem       │ watching │
├───────────────┼────┼──────┼───────┼────────┼─────────┼────────┼─────┼───────────┼──────────┤
│ app.php       │ 5  │ fork │ 30996 │ online │ 0       │ 104s   │ 0%  │ 16.2 MB   │ disabled │
└───────────────┴────┴──────┴───────┴────────┴─────────┴────────┴─────┴───────────┴──────────┘
```

**id**为pm2中管理进程使用的标识
*进程死掉之后pm2会自动重启*
### 查看进程详情

```bash
pm2 describe 5
```

### 停止进程

```bash
pm2 stop 5
```

### 进程列表

```bash
pm2 list
```

### 进程资源监控

```bash
pm2 monit
```

### 停止所有进程

```bash
pm2 stop all
```

### 删除所有进程

```bash
pm2 delete all
```

### 查看进程输出

```bash
pm2 logs [id]
```

*不传入id时显示所有日志，否则显示指定进程日志*

### 使用配置文件启动
pm2 强大之处在于其支持任意程序的守护，使用配置文件来启动程序比使用命令行启动更加清晰：

```json
{
  "name": "delay-message",
  "args": "task/delaymessage",
  "script": "yii",
  "exec_interpreter": "php",
  "exec_mode": "fork",
  "max_memory_restart": "100M"
}
```

+ **name** 脚本显示名称
+ **args** 脚本参数
+ **script** 脚本文件名称
+ **exec_interpreter** 使用的解析器
+ **exec_mode** 启动模式，fork为使用子进程启动,*cluster* 使用nodejs的cluster模块启动
+ **max_memory_restart** 进程占用内存超过时自动重启