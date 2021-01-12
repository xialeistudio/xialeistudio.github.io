---
title: log4php使用syslog记录日志
layout: post
category: 
- backend
- php
---
log4php是apache基金会下的一个开源项目，灵活、强大，已经有几个项目使用了log4php处理日志，目前遇到的问题是服务器太多的时候日志如何统一管理，本来想使用数据库存储。但是日志格式成了一个问题，而且不利于扩展，如果临时需要保存到文件，又要更改log4php的配置。
好在log4php提供了syslog的一个appender，可以将日志写入syslog;

## log4php配置
```
log4php.rootLogger=INFO, stdout, stderr
log4php.appender.stdout=LoggerAppenderConsole
log4php.appender.stdout.layout=LoggerLayoutPattern
log4php.appender.stdout.layout.ConversionPattern=%date{Y-m-d H:i:s} [%-5p] %m%n
log4php.appender.stdout.threshold=INFO

log4php.appender.stderr=LoggerAppenderSyslog
log4php.appender.stderr.ident=qun.hk-task
log4php.appender.stderr.priority=ERR
log4php.appender.stderr.facility=LOCAL0
log4php.appender.stderr.layout=LoggerLayoutPattern
log4php.appender.stderr.layout.ConversionPattern=%date{Y-m-d H:i:s} %m%n
log4php.appender.stderr.threshold=WARN
```
这里使用两个输出目的地,stdout输出到终端，stderr输出到syslod，log4php配置对应rsyslog的配置关系为：
+ ident -> syslog中的tag
+ priority -> syslog中的priority
+ facility -> syslog中的facility，请注意全部为大写

## rsyslog配置
rsyslog配置文件一般在 */etc/rsyslog.conf* 以及 */etc/rsyslog.d*目录下
我们不更改主配置文件，在*/etc/rsyslog.d/*目录下新建文件

```vim local0.conf```

内容为

```local0.* /var/log/local0.log```

rsyslog输出可以写成服务器，本文为了测试直接写入文件，有需要的可以根据实际情况进行转发。重启rsyslog

```service rsyslog restart```

## PHP加载配置
```php
<?php
\Logger::configure(__DIR__ . '/log4php.properties');
$logger = \Logger::getLogger('default');
$logger->info('info');
$logger->error('error');
```
可以看到*/var/log/local0.log*中多出一行*error*的日志

