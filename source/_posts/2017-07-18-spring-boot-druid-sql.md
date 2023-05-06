---
title: druid spring boot 统计SQL问题
layout: post
categories:
- Engineering
tags:
- spring-boot
---
## spring-boot配置

```
spring.jpa.hibernate.ddl-auto=validate
spring.datasource.type=com.alibaba.druid.pool.DruidDataSource
spring.datasource.driver-class-name=com.mysql.jdbc.Driver
spring.datasource.initialize=true
spring.datasource.initialSize=5
spring.datasource.minIdle=5
spring.datasource.maxActive=10
spring.datasource.maxWait=60000
spring.datasource.timeBetweenEvictionRunsMillis=60000
spring.datasource.minEvictableIdleTimeMillis=300000
spring.datasource.validationQuery=SELECT 'x'
spring.datasource.testWhileIdle=true
spring.datasource.testOnBorrow=false
spring.datasource.testOnReturn=false
spring.datasource.poolPreparedStatements=false
spring.datasource.maxPoolPreparedStatementPerConnectionSize=20
spring.datasource.filters=stat,wall,slf4j
spring.datasource.connectionProperties=druid.stat.mergeSql=true;druid.stat.slowSqlMillis=5000
spring.datasource.useGlobalDataSourceStat=true
```

这个配置没有什么好说的，网上很多，可能关键在

```
spring.datasource.filters=stat,wall,slf4j
spring.datasource.connectionProperties=druid.stat.mergeSql=true;druid.stat.slowSqlMillis=5000
spring.datasource.useGlobalDataSourceStat=true
```

但是就算配置好这些后，返回`/druid`也不显示SQL统计。
其实问题在于

*系统默认使用的数据库连接池没有使用你的配置*，所以需要我们手动实例化`Bean`

## kotlin代码
```kotlin
@SpringBootApplication
open class Application {
    @Bean
    @ConfigurationProperties(prefix = "spring.datasource")
    open fun druidDataSource(): DataSource {
        return DruidDataSource()
    }

```