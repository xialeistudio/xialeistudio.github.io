---
title: NestJs学习之旅(9)——拦截器
date: 2019-09-10 15:17:32
categories:
- nodejs
tags:
- nestjs
---

欢迎持续关注*`NestJs之旅`*系列文章

![img](https://static.ddhigh.com/blog/2019-08-26-060638.jpg)

拦截器是一个实现了**NestInterceptor**接口且被**@Injectable**装饰器修饰的类。

![img](https://static.ddhigh.com/blog/2019-09-10-061428.png)

拦截器是基于AOP编程思想的一种应用，以下是常用的功能：

- 在方法执行之前或之后执行**额外的逻辑**，这些逻辑一般不属于业务的一部分
- **转换**函数执行结果
- **转换**函数执行时抛出的异常
- 扩展函数基本行为
- 特定场景下完全重写函数的行为（比如缓存拦截器，一旦有可用的缓存则直接返回，不执行真正的业务逻辑，即业务逻辑处理函数行为已经被重写）

## 拦截器接口

每个拦截器都需要实现**NestInterceptor**接口的**intercept()**方法，该方法接收两个参数。方法原型如下：

```typescript
function intercept(context: ExecutionContext, next: CallHandler): Observable<any>
```

- ExecutionContext 执行上下文，与[NestJs学习之旅(7)——路由守卫](https://www.ddhigh.com/2019/08/27/nestjs-guard.html)中的**执行上下文**相同
- CallHandler 路由处理函数

## CallHandler

该接口是对路由处理函数的抽象，接口定义如下：

```typescript
export interface CallHandler<T = any> {
    handle(): Observable<T>;
}
```

handle()函数的返回值也就是对应路由函数的返回值。

以获取用户列表为例：

```typescript
// user.controller.ts
@Controller('user')
export class UserController {
  @Get()
  list() {
    return [];
  }
}
```

当访问 /user/list 时，路由处理函数返回**[]**，如果在应用拦截器的情况下，调用CallHandler接口的handle()方法得到的也是Observable<[]>(RxJs包装对象)。

**所以，如果在拦截器中调用了next.handle()方法就会执行对应的路由处理函数，如果不调用的话就不会执行。**

## 一个请求链路日志记录拦截器

随着微服务的兴起，原来的单一项目被拆分成多个比较小的子模块，这些子模块可以独立开发、独立部署、独立运行，大大提高了开发、执行效率，但是带来的问题也比较多，一个经常遇到的问题是接口调用出错不好查找日志。

如果在业务逻辑中硬编码这种链路调用日志是非常不可取的，严重违反了单一职责的原则，这在微服务开发中是相当不好的一种行为，会让微服务变得臃肿，这些逻辑完全可以通过拦截器来实现。

```typescript
// app.interceptor.ts
import { CallHandler, ExecutionContext, Injectable, Logger, NestInterceptor } from '@nestjs/common';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';
import { Request } from 'express';
import { format } from 'util';

@Injectable()
export class AppInterceptor implements NestInterceptor {
  private readonly logger = new Logger(); // 实例化日志记录器

  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    const start = Date.now(); // 请求开始时间

    return next.handle().pipe(tap((response) => {
      // 调用完handle()后得到RxJs响应对象，使用tap可以得到路由函数的返回值
      const host = context.switchToHttp();
      const request = host.getRequest<Request>();

      // 打印请求方法，请求链接，处理时间和响应数据
      this.logger.log(format(
        '%s %s %dms %s',
        request.method,
        request.url,
        Date.now() - start,
        JSON.stringify(response),
      ));
    }));
  }
}
```

```typescript
// user.controller.ts
@UseInterceptors(AppInterceptor)
export class UserController {
  @Get()
  list() {
    return [];
  }
}
```

当访问 /user时控制台想输出

```text
[Nest] 96310   - 09/10/2019, 2:44 PM   GET /user 1ms []
```

## 拦截器作用域

拦截器可以在以下作用域进行绑定：

- 全局拦截器
- 控制器拦截器
- 路由方法拦截器

### 全局拦截器

在main.ts中使用以下代码即可：

```typescript
const app = await NestFactory.create(AppModule);
app.useGlobalInterceptors(new AppInterceptor());
```

### 控制器拦截器

将对该控制器所有**路由**方法生效：

```typescript
@Controller('user')
@UseInterceptors(AppInterceptor)
export class UserController {
}
```

### 路由方法拦截器

只对当前被装饰的路由方法进行拦截：

```typescript
@Controller('user')
export class UserController {
  @UseInterceptors(AppInterceptor)
  @Get()
  list() {
    return [];
  }
}

```

## 响应处理

CallHandler接口的handle()返回值实际上是RxJs的Observable对象，利用RxJs操作符可以对该对象进行操作，比如有一个API接口，之前返回的数据结构如下，如果正常响应，响应体就是数据，没有包装结构：

```json
{
  "id":1,
  "name":"xialei"
}

```

新的需求是要把之前的纯数据响应包装为一个data属性，结构如下：

```json
{
  "data": {
    "id": 1,
    "name":"xialei"
  }
}

```

接到这个需求时有的小伙伴可能已经在梳理响应接口的数量然后评估工时准备进行开发了，而使用NestJs的拦截器，不到一炷香的时间即可实现该需求。

```typescript
import { CallHandler, ExecutionContext, Injectable, Logger, NestInterceptor } from '@nestjs/common';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

@Injectable()
export class AppInterceptor implements NestInterceptor {

  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {

    return next.handle().
      pipe(map(data => ({ data }))); // map操作符与Array.prototype.map类似
  }
}

```

应用上述拦截器后响应数据就会被包上一层data属性。

## 异常映射

另外一个有趣的例子是利用RxJs的catchError来覆盖路由处理函数抛出的异常。

```typescript
import {
  Injectable,
  NestInterceptor,
  ExecutionContext,
  BadGatewayException,
  CallHandler,
} from '@nestjs/common';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

@Injectable()
export class ErrorsInterceptor implements NestInterceptor {
  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    return next
      .handle()
      .pipe(
        catchError(err => throwError(new BadGatewayException())) // catchError用来捕获异常
      );
  }
}

```

## 重写路由函数逻辑

在文章开始部分提到了拦截器可以重写路由处理函数逻辑。如下是一个缓存拦截器的例子

```typescript
import { Injectable, NestInterceptor, ExecutionContext, CallHandler } from '@nestjs/common';
import { Observable, of } from 'rxjs';

@Injectable()
export class CacheInterceptor implements NestInterceptor {
  constructor(private readonly cacheService: CacheService) {}
  
   async intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
  	const host = context.switchToHttp();
    const request = host.getRequest();
    if(request.method !== 'GET') {  
      // 非GET请求放行
      return next.handle();
    }
    const cachedData = await this.cacheService.get(request.url);
    if(cachedData) { 
      // 命中缓存，直接放行
      return of(cachedData);
    }
    return next.handle().pipe(tap(response) => { 
      // 响应数据写入缓存，此处可以等待缓存写入完成，也可以不等待
      this.cacheService.set(request.method, response);
    });
  }
}

```

## 结尾

本文是NestJs基础知识的最后一篇，接下将针对特定模块进行更新，比如数据库、上传、鉴权等等。

由于直接放出群二维码导致加群门槛极低，近期有微商之类的人员扫码入群发送广告/恶意信息，严重骚扰群成员，二维码入群通道已关闭。有需要的伙伴可以关注公众号来获得加群资格。