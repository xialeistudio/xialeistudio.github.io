---
slug: laravel-crontab-log-permission
title: Laravel定时任务写入日志用户变为root导致Web进程无法写入日志问题
date: 2020-10-20 11:17:09
tags:
- laravel
categories:
- Engineering
---

今天访问接口时返回 **接口写入日志失败**，通过排查后发现 `storage/logs`下面出现了`root`用户新建的日志，导致`www`用户无法写入日志。

通过排查发现，`crontab`写入了`laravel`的`定时任务命令`。默认情况下，crontab的任务是使用`root`用户去执行的，因此`laravel定时任务`新建的文件属主自然成为了`root`。

## 解决方法

解决方法就是`使用指定用户来运行 crontab 任务`。比如使用`www`用户来运行`laravel`的计划任务命令。

使用下面的命令编辑`www`用户的定时任务。

```bash
crontab -u www -e
```

例如写入下面的示例任务：

```bash
* * * * * /usr/local/php/bin/php /data/wwwroot/laravel/artisan schedule:run >> /var/log/laravel-crontab.log 2>&1
```

保存即可，等待系统运行任务。

## 运行时错误

通过观察发现定时任务并没有成功运行，通过查询`/var/log/cron`日志发现如下的日志：

```text
(www) CMD (/usr/local/php/bin/php /data/wwwroot/laravel/artisan schedule:run >> /var/log/laravel-crontab.log 2>&1)
(CRON) ERROR chdir failed (/home/www): No such file or directory
```

可以看到，定时任务确实有执行，但是执行出错。出现这个问题的原因是`www 用户没有主目录`。

解决方案如下：

1. 新建`/home/www`目录
2. 将`/home/www`的用户属主改为`www`用户

相关命令如下：

```
mkdir /home/www
chown -R www:www /home/www
```

后续执行没有再出现错误。

