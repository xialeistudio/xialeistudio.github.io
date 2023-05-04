---
title: NestJs学习之旅(6)——异常处理
date: 2019-08-26 15:32:29
categories:
- engineering
tags:
- nestjs
---

本文是NestJs的第六篇，讲解异常处理。

## 传统的异常处理

在前面的内容中我们介绍了NestJs的几大常用组件，但是有一点没有做出说明，当我们的应用需要中断此次请求且输出错误信息时，我们需要怎么做？

这个问题有两种解决办法：

1. services层直接返回中断请求的响应对象，controller直接输出该对象即可

   ```typescript
   if(!this.allowLogin()) {
     return {errcode: 403, errmsg: '不允许登录'};
   }
   ```

2. services层抛出异常，controller捕获该异常，然后输出响应对象

以上两种方法都有一定的缺点：

1. controller调用多个services时，需要依据services层的返回值来进行错误判断，要是漏了判断的话会导致原本需要中断的请求处理继续运行，导致不可预料的后果
2. 如果每个controller都需要try/catch掉services层抛出的异常的话，会多了很多“重复”代码

那有没有一个像SpringBoot的`ExceptionHandler`相似的解决办法呢?

## NestJs的异常处理

NestJs提供了统一的异常处理器，来集中处理运行过程中**未捕获的异常**，可以自定义响应参数，非常灵活。

![img](https://static.ddhigh.com/blog/2019-08-26-073002.png)

## 默认响应

NestJs内置了默认的**全局异常过滤器**，该过滤器处理**HttpException**(及其子类)的异常。如果抛出的异常不是上述异常，则会响应以下默认JSON：

```json
{
  "statusCode": 500,
  "message": "Interval server error"
}
```

## 内置异常过滤器

由于NestJs内置了默认的异常过滤器，如果在应用内抛出HttpException，是可以被NestJs自动捕获的。

比如在services层抛出一个HttpException：

```typescript
@Injectable()
export class UserService {
  login(username: string, password: string) {
    if(!this.allowLogin()) {
  		throw new HttpException('您无权登录', HttpStatus.FORBIDDEN);
		}
    return {user_id:1, token: 'fake token'}
  }
}
```

controller正常调用该services即可:

```typescript
@Controller('users')
export class UserController {
  constructor(private readonly userService: UserService) {}
  
  @Post('login')
  login(@Body('username') username: string, @Body('password') password: string) {
    return this.userService.login(username, password);
  }
}
```

客户端访问/user/login时，如果不允许登录，会收到以下响应：

```json
{
  "statusCode": 403,
  "message": "您无权登录"
}
```

一般情况下，上述JSON的返回的信息是不够的，比如有些业务自定义的错误码没地方可以自定义。

如果你有这种需求，可以传递object给HttpException的第一个参数来实现：

```typescript
throw new HttpException({errcode: 40010, errmsg: '您无权登录'}, HttpStatus.FORBIDDEN);
```

客户端访问时，如果不允许登录，会收到以下响应：

```json
{
  "errcode": 40010,
  "errmsg": "您无权登录"
}
```

## 自定义异常

企业级应用开发过程中，使用HttpException进行处理对开发是不太友好的，一个比较常用的做法是自定义一个UserException来承载业务异常（系统运行正常，只不过当前请求不满足业务上的要求而中断，比如注册的时候用户名重复的时候打回去，此时数据库查询是正常的，这就是业务异常和系统异常的区别）。

```typescript
export class UserException extends HttpException {
  constructor(errcode: number, errmsg: string, statusCode: number) {
    super({ errcode, errmsg }, statusCode);
  }
}
```

业务层在使用该异常时直接使用以下代码即可，将原来传递对象的代码扁平化了：

```typescript
throw new UserException(40010, '您无权登录', HttpStatus.FORBIDDEN);

```

### 语义化业务异常

使用自定义异常时HTTP协议层是正常的，抛出403错误有点不符合语义化的需求。对上例改造一下：

```typescript
export class UserException extends HttpException {
  constructor(errcode: number, errmsg: string) {
    super({ errcode, errmsg }, HttpStatus.OK);
  }
}

```

```typescript
throw new UserException(40010, '您无权登录');

```

此时客户端收到的HttpStatus为200，意味着此次请求在协议层面是成功的，只不过业务层返回了错误。前端在处理响应时可以直接对errcode是否为0来确定此次请求是否成功。

## 自定义异常过滤器

虽然内置的异常过滤器可以自动处理很多情况，但是不是“可编程”的，也就是说我们无法完全控制异常处理过程，如果我们需要记录日志的话，使用内置的异常过滤器办不到，这时候可以使用**@Catch**注解来自定义异常处理器，添加日志记录什么的。

```typescript
import { ExceptionFilter, Catch, ArgumentsHost, HttpException } from '@nestjs/common';
import { Request, Response } from 'express';

@Catch(HttpException)
export class HttpExceptionFilter implements ExceptionFilter<HttpException> {
  catch(exception: HttpException, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();
    const request = ctx.getRequest<Request>();
    const status = exception.getStatus();
		// @todo 记录日志
    console.log('%s %s error: %s', request.method, request.url, exception.message);
    // 发送响应
    response
      .status(status)
      .json({
        statusCode: status,
      	message: exception.message
        path: request.url,
      });
  }
}

```

### ArgumentHost

ArgumentHost是原始请求的包装器，由于NestJs支持HTTP/GRPC/WebSocket，这三种请求的原始请求对象是有差异的，为了异常过滤器能够统一处理这三种异常，NestJs做了包装。最终在使用时处理那种异常由开发者来决定。

ArgumentHost接口定义如下：

```typescript
export interface ArgumentsHost {
  getArgs<T extends Array<any> = any[]>(): T;
  getArgByIndex<T = any>(index: number): T;
  switchToRpc(): RpcArgumentsHost;
  switchToHttp(): HttpArgumentsHost;
  switchToWs(): WsArgumentsHost;
}

```

如果需要处理的是WebSocket异常，就使用**host.switchToWs()**，其他异常以此类推。

### 使用自定义异常过滤器

如果定义完自定义异常过滤器之后，直接去访问会抛出异常的接口，此时可以发现并没有走自定义异常过滤器。

因为我们**只是定义，并没有注册**。

使用**@UseFilters**注册自定义异常过滤器。

异常过滤器有以下三种作用范围：

- 方法级别
- 控制器级别
- 全局级别

### 方法级别

只会处理该方法上抛出的异常，其他方法抛出的异常不会处理。

```typescript
@Post('login')
@UseFilters(UserExceptionFilter)
login(@Body('username') username:string, password: string) {
  throw new UserException(40010, '您无权登录');
}

```

### 控制器级别

只会处理该控制器方法上抛出的异常，其他控制器抛出的异常不处理。

```typescript
@Controller('user')
@UseFilters(UserExceptionFilter)
export class UserController {
  
}

```

### 全局级别

在应用入口注册，不会对Websocket或者混合应用（同时支持两种应用，如HTTP/GRPC或者HTTP/WebSocket）生效。一般Web开发中全局异常过滤器已经够用了。

在main.ts中注册全局异常过滤器

```typescript
async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  app.useGlobalFilters(new UserExceptionFilter());
  await app.listen(3000);
}
bootstrap();

```

## 依赖注入

由于异常过滤器并不是任何模块上下文的一部分，所以NestJs无法对其进行依赖注入管理，如果有此种需求，比如在异常过滤器中注入service，需要定义服务提供者。服务提供者名称为NestJs规定的常量APP_FILTER

```typescript
import { Module } from '@nestjs/common';
import { APP_FILTER } from '@nestjs/core';

@Module({
  providers: [
    {
      provide: APP_FILTER,
      useClass: UserExceptionFilter,
    },
  ],
})
export class AppModule {}

```

## 捕获多种异常或者所有异常

上例中提到的自定义异常处理器只会捕获UserException异常，如果有系统异常，会使用内置的异常处理器。通过传入异常类型给**@Catch**装饰器来捕获多种异常。如果不传任何异常类型的话，NestJs会捕获所有异常（也就是Error及其子类）。

```typescript
import { ExceptionFilter, Catch, ArgumentsHost, HttpException } from '@nestjs/common';
import { Request, Response } from 'express';

@Catch() // 捕获所有异常
export class HttpExceptionFilter implements ExceptionFilter<Error> {
  catch(exception: Error, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();
    const request = ctx.getRequest<Request>();
    const status = exception.getStatus();
		// @todo 记录日志
    console.log('%s %s error: %s', request.method, request.url, exception.message);
    // 发送响应
    response
      .status(status)
      .json({
        statusCode: status,
      	message: exception.message
        path: request.url,
      });
  }
}

```

## 结尾

异常过滤器让应用异常有了统一的处理渠道，同时也解决文章开头提出的两个问题。通过自定义异常过滤器，开发者可以进行统一响应格式，统一记录日志等等操作。
