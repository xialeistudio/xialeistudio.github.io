---
title: koa-cooke使用maxAge代替expires来设置过期时间
date: 2017-10-17 17:13:44
categories:
- engineering
tags:
- koa
---
# expires
原来设置cookie使用的以下代码

```javascript
const cookieOptions = {
  expires: moment().add(6,'day').toDate(),
};
```

但是查看network的时候，cookie虽然设置了，但是过期时间比现在还早，导致一设置就过期，所以expires貌似没作用。

# maxage
查看对应的typescript定义文件**index.d.ts**发现还有一个**maxAge**选项也可以用来控制cookie过期时间
```javascript
/**
 * a number representing the milliseconds from Date.now() for expiry
 */
maxAge?: number;
```

这个参数更简单，**基于当前时间的毫秒数**，使用以下代码测试之后，发现过期时间跟预期一致**一个星期**：

```javascript
const cookieOptions = {
  maxAge: 3600 * 24 * 7 * 1000,
};
```