---
title: 使用systemd来构建你的服务
date: 2019-02-28 21:51:16
categories:
- engineering
tags:
- systemd
---

## systemd是什么

Systemd 服务是一种以 .service 结尾的单元（unit）配置文件，用于控制由Systemd 控制或监视的进程。简单说，用于后台以守护精灵（daemon）的形式运行程序。

## 为什么要使用systemd

1. service文件编写简单易用
2. 可以自动维持进程存活（强大的功能，可以取代PM2）
3. 自动收集进程输出的输出
   
## systemd主要命令

可以看到systemd以字母d结尾，根据linux惯用规则，可以判断该进程为守护进程，可以通过`systemctl`与之交互。

```
systemctl start redis.service #启动服务
systemctl stop redis.service #停止服务
systemctl restart redis.service #重启服务
systemctl enable redis.service #将redis设置为开机启动
```

## 编写systemd

systmd service文件一般放在`/etc/systemd/system/`文件夹中。

systemd service文件是结构化的，以下给出一份笔者常用的清单。

```
[Unit]
Description=Git Auto Update Hook Service
After=network.target

[Service]
Type=simple
ExecStart=/root/src/git-hookd/git-hookd
Restart=always
[Install]
WantedBy=multi-user.target
```

拿之前写过的init.d的脚本对比一下

```
#!/bin/bash
### BEGIN INIT INFO
# Provides:          xialeistudio
# Required-Start:    $network
# Required-Stop:     $local_fs
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: test service
# Description:       test service
### END INIT INFO
PROG="testd"
PROG_PATH="/root/apps/testd"
PROG_ARGS="-u xialei"
PID_PATH="/var/run/"

start() {
        if [ -e "$PID_PATH/$PROG.pid" ]; then
                echo "Error! $PROG is running!" 2>&1
                exit 1
        else
                $PROG_PATH/$PROG $PROG_ARGS 2>&1 > "/var/log/$PROG.log" &
                pid=`ps ax|grep testd|awk '{print $2}'|head -n 1`
                echo "$PROG started"
                echo $pid > "$PID_PATH/$PROG.pid"
        fi      
}

stop() {
        if [ -e "$PID_PATH/$PROG.pid" ]; then
                pid=`ps ax|grep testd|awk '{print $2}'|head -n 1`
                kill $pid
        
                rm -rf "$PID_PATH/$PROG.pid"
                echo "$PROG $pid killed"
        else
                echo "Error! $PROG not running!" 2>&1
                exit 1
        fi
}

if [ "$(id -u)" != "0" ]; then
        echo "Please run as root!" 2>&1
        exit 1
fi

case "$1" in
    start)
                start
                exit 0
        ;;
        stop)
                stop
                exit 0
        ;;
        reload|restart)
                stop
                start
                exit 0
        ;;
        **)
                echo "Usage: $0 {start|stop|reload}" 2>&1
                exit 1
        ;;
esac
```

可以看到init.d脚本实在是太原始了，systemd取代init.d指日可待

## systemd service文件说明

service文件由 Unit, Service, Install 三部分组成

### Unit

所有引导过程中systemd要控制的文件/设备/程序等等都称为一个单元。
+ Description: 服务描述
+ Wants: 本单元启动成功，则会启动此字段定义的单元，如果Wants定义的单元启动失败，对本单元无影响
+ Requires：本单元启动成功，则会启动此字段定义的单元，如果Requires定义的单元启动失败，本单元也失败。该字段无法控制先后顺序，如果Requires定义的单元未启动完成就启动本单元，那么一个都启动不了，不建议用这个字段
+ OnFailure： 本单元如果启动失败，则启动该字段定义的单元
+ Before/After：指定本单元的启动顺序

本例中只需要依赖网络单元即可

### Service

服务本体定义：
+ Type 启动类型
+ ExecStart 启动服务的命令
+ ExecStop 停止服务的命令（一般不写）
+ Restart 重启规则
+ RemainAfterExit 即使没有进程，也任务服务启动成功

Type 启动类型有以下几种：
    + simple： 默认类型，启动的进程将成为服务进程。
    + forking：标准Unix Daemon进程。本进程启动后会通过系统调用fork，把必要的通信频道都设置好之后父进程退出，留下守护精灵的子进程。（也就是说你自己来将进程变成daemon进程）
    + oneshot：一次性命令。该服务运行完毕后没有进程，所以需要配合RemainAfterExit。

Restart 重启规则有以下几种：
    + no（默认值）：退出后不会重启
    + always：不管是什么退出原因，总是重启
    + on-success：只有正常退出时（退出状态码为0），才会重启
    + on-failure：非正常退出时（退出状态码非0），包括被信号终止和超时，才会重启
    + on-abnormal：只有被信号终止和超时，才会重启
    + on-abort：只有在收到没有捕捉到的信号终止时，才会重启
    + on-watchdog：超时退出，才会重启

### Install

systemd装载规则定义
+ WantedBy 将被谁装载，本例中使用multi-user.target，最终服务将通过软链接到`/etc/systemd/system/multi-user.target.wants`目录
+ Alias 服务别名，可以通过 `systemctl 服务别名 restart` 之类的来操作

## 写在最后

是时候通过systemd改写init.d的服务了，有必要的话可以连pm2守护的进程都交给systemd来处理。