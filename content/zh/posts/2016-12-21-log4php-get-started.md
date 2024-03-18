---
slug: log4php-get-started
date: 2016-12-21
title: apache log4php简单使用
categories:
- Engineering
---
log4j在JAVA中可算是大名鼎鼎的日志开发包了,它为apache组织维护项目，log4php是log4xx的系列之一，主要用来记录日志信息，功能强大，配置灵活。

最近需要开发一个命令行程序，于是想到了用log4php来作为日志管理器进行日志输出。

## 安装
+ 基于composer

```bash
composer require apache/log4php
```

+ 下载源码包

```
http://www.apache.org/dyn/closer.cgi/logging/log4php/2.3.0/apache-log4php-2.3.0-src.zip
```

## 使用
*基于composer的程序不用手动引用文件，composer会自动加载相应类文件。如果未使用composer，请手动引用Logger.php文件*

### 配置
log4php配置非常灵活，具体可以查看官方文档，贴一下笔者目前的常用配置:

```text
log4php.rootLogger=INFO, stderr, stdout
log4php.appender.stdout=LoggerAppenderConsole
log4php.appender.stdout.layout=LoggerLayoutPattern
log4php.appender.stdout.layout.ConversionPattern=%date{Y-m-d H:i:s} [%p] %m%n
log4php.appender.stdout.threshold=INFO

log4php.appender.stderr=LoggerAppenderConsole
log4php.appender.stderr.layout=LoggerLayoutPattern
log4php.appender.stderr.target=stderr
log4php.appender.stderr.threshold=ERROR
log4php.appender.stderr.layout.ConversionPattern=%date{Y-m-d H:i:s} [%p] [%l] %m%n
```

### 实例化

```php
<?php
\Logger::configure(__DIR__ . '/log4php.properties');
$this->logger = \Logger::getLogger('default');
$this->logger->info('hello world');
```

控制台会输出:

```text
2016-12-21UTC06:41:34 [INFO] hello world
```