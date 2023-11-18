---
slug: php-fpm-permission-502-bad-gateway
title: php-fpm sock文件权限问题导致502
date: 2015-08-14 10:26:20.000000000 +08:00
categories:
- Engineering
---
今天升级完PHP出现了502 Bad Gateway错误，根据经验是php-fpm的问题，但是看到网上那些什么访问量，子进程设置什么的，但是我这太服务器压根没啥流量。所以只能从配置文件下手看看。

## php-fpm.conf

```bash
[global]
pid = /usr/local/php/var/run/php-fpm.pid
error_log = /usr/local/php/var/log/php-fpm.log
log_level = notice

[www]
listen = /tmp/php-cgi.sock
user = www
group = www
pm = dynamic
pm.max_children = 20
pm.start_servers = 2
pm.min_spare_servers = 1
pm.max_spare_servers = 6
request_terminate_timeout = 100
```
看到 /tmp/php-cgi.sock 直觉发现应该是个文件，所以前往该目录查看权限，发现文件属主是**root:root**，而我的nginx和php-fpm进程是以www用户运行的。所以应该是权限问题。   
而配置文件中的user = www,group = www也设置了一个权限，通过 ps -aux|grep php 发现，这是php-fpm进程的属主。   
知道问题的源头后便开始查php-fpm的配置，查到了 listen.ower listen.group 设置。   
这是改进之后的文件：

```bash
[global]
pid = /usr/local/php/var/run/php-fpm.pid
error_log = /usr/local/php/var/log/php-fpm.log
log_level = notice

[www]
listen = /tmp/php-cgi.sock
listen.owner = www
listen.group = www
user = www
group = www
pm = dynamic
pm.max_children = 20
pm.start_servers = 2
pm.min_spare_servers = 1
pm.max_spare_servers = 6
request_terminate_timeout = 100
```