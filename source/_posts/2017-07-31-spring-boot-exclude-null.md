---
title: Spring Boot JPA 返回json时排除Null字段
layout: post
categories:
- spring boot
tags:
- json
- jpa
---
Spring Boot在返回JSON的时候默认会返回null字段，这个对客户端一般没什么作用，还会增加服务器带宽压力。使用如下配置可以屏蔽。

在pojo对象上添加注解

```java
@JsonInclude(JsonInclude.Include.NON_NULL)
class User {
}
```

再使用`@ResponseBody`的时候就不会返回Null字段了。