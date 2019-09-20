---
title: druid SQL监控不显示问题
date: 2019-07-08 17:13:40
categories:
- backend
- java
tags:
- spring-boot
---

新版druid数据源驱动的SQL监控如果用以前的老版本配置是无法监控到SQL的：

application.yml

```yaml
spring:
    datasource:
        druid:
            filters:
                - stat
                - wall
                - log4j
```

启动应用之后访问druid监控页面，除了SQL相关的页面都正常工作，但是访问SQL监控页面时没有看到SQL记录。
查看监控页面 **数据源** 菜单发现 **filter类名** 显示的是空，估计是filter配置有问题导致。

查阅官方文档发现filter配置有变更，改成以下形式即可统计SQL，同时在数据源页面 **filter类名** 会显示正常。

application.yml

```yaml
spring:
    datasource:
        druid:
            initial-size: 5
            min-idle: 5
            max-active: 20
            max-wait: 5000
            # 状态监控
            filter:
                stat:
                    enabled: true
                    db-type: mysql
                    log-slow-sql: true
                    slow-sql-millis: 2000
            # 监控过滤器
            web-stat-filter:
                enabled: true
                exclusions:
                - "*.js"
                - "*.gif"
                - "*.jpg"
                - "*.png"
                - "*.css"
                - "*.ico"
                - "/druid/*"
            # druid 监控页面
            stat-view-servlet:
                enabled: true
                url-pattern: /druid/*
                reset-enable: false
                login-username: root
                login-password: root
```

数据源filter类名：**com.alibaba.druid.filter.stat.StatFilter**
