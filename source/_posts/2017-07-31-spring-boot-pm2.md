---
title: 使用pm2来保证Spring Boot应用稳定运行
layout: post
categories:
- Engineering
tags:
- spring-boot
---
Spring Boot开发web应用就像开发普通的java程序一般简洁，因为其内嵌了web容易，启动的时候只需要一条命令`java -jar server.jar`即可，非常方便。
但是由此而来的问题是万一应用挂了怎么办？

别担心，有pm2进程管理工具可以帮到你。

## PM2简介
pm2原先是nodejs应用的进程管理工具，不过其良好的设计以及扩展性可以手动执行执行进程。

## PM2安装
1. 安装NodeJs
2. `npm install pm2 -g`

## PM2基本命令
+ pm2 list 查看所有被PM2管理的进程列表
+ pm2 start xxx 启动一个应用
+ pm2 stop xxx 停止一个应用
+ pm2 restart xxx 重启一个应用
+ pm2 describe xxx 查看应用详情
+ pm2 startup, pm2 save 两条命令，用来保证服务器启动时,pm2管理的程序自动运行

## Java程序处理
在jar的同级目录新建应用启动配置文件，如`pm2.json`，内容如下：

```json
{
    "name": "my-server",
    "script": "/usr/bin/java",
    "args": [
        "-jar",
        "server.jar"
    ],
    "exec_interpreter": "",
    "exec_mode": "fork"
}
```
说明如下：
+ name 进程名称（显示在`pm2 list`命令中）
+ script 执行进程名称，如果需要执行PHP脚本则填写php解释器的路径，本文为java
+ args 传给执行进程的参数，多个参数以数组单元分割
+ exec_interpreter NodeJs解析器，本文不适用
+ exec_mode 执行模式[cluster|fork]这个针对NodeJs应用的配置，非NodeJs应用统一fork

配置文件完成后，使用
```
pm2 start pm2.json
```
即可看到应用被启动

## 日志管理
日志路径在`~/.pm2/logs`，`stdout`和`stderr`被分开存放，程序中的所有`stdout`和`stderr`都被收集方便查错。