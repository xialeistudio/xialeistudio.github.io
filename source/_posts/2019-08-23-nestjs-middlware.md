---
title: NestJs学习之旅(5)——中间件
date: 2019-08-23 10:40:49
categories:
- backend
- nodejs
tags:
- nestjs
---

本文是NestJs学习之旅的第五篇，讲解中间件。

## 中间件

中间件是在路由处理程序**之前**调用的函数。中间件函数可以访问**请求**和**响应**对象。

使用过koa和express的朋友应该知道，中间件是一个很核心的功能，尤其是koa，核心就是中间件，连路由功能都是由中间件提供的。

中间件可以提供以下功能：

+ 运行过程中执行任意代码
+ 对请求和响应进行更改
+ 结束本次请求的响应
+ 继续调用下一个中间件

## 示例

NestJs使用`@Injectable()`来装饰中间件，被装饰的对象应该实现`NestMiddleware`接口。

以下是一个日志中间件的实现：

```ts
// log.middleware.ts
import {Injectable, NestMiddleware} from '@nestjs/common';
import {Request, Response} from 'express';

@Injectable()
export class LogMiddleware implements NestMiddleware {
    use(req: Request, resp: Response, next: Function) {
        console.log(`${req.method} ${req.path}`)
        next();
    }
}
```

```ts
// app.module.ts
import { Module, NestModule, MiddlewareConsumer } from '@nestjs/common';
import { LogMiddleware } from './common/middleware/log.middleware';
import { UserModule } from './user/user.module';

@Module({
  imports: [UserModule],
})
export class AppModule implements NestModule {
  configure(consumer: MiddlewareConsumer) {
    consumer
      .apply(LogMiddleware)
      .forRoutes('users');
  }
}
```

## 针对请求方法应用中间件

上面的简单示例中会对所有的`users`路由应用中间件，如果需要只对特定的请求方法，比如GET请求才应用中间件，可以使用以下方式：

```ts
import { Module, NestModule, MiddlewareConsumer } from '@nestjs/common';
import { LogMiddleware } from './common/middleware/log.middleware';
import { UserModule } from './user/user.module';

@Module({
  imports: [UserModule],
})
export class AppModule implements NestModule {
  configure(consumer: MiddlewareConsumer) {
    consumer
      .apply(LogMiddleware)
       .forRoutes({ path: 'users', method: RequestMethod.GET });
  }
}
```

## 应用多个中间件

```ts
import { Module, NestModule, MiddlewareConsumer } from '@nestjs/common';
import { LogMiddleware } from './common/middleware/log.middleware';
import { UserModule } from './user/user.module';

@Module({
  imports: [UserModule],
})
export class AppModule implements NestModule {
  configure(consumer: MiddlewareConsumer) {
    consumer
      .apply(LogMiddleware, OtherMiddleware)
       .forRoutes({ path: 'users', method: RequestMethod.GET });
  }
}
```

## 基于控制器名称应用中间件

上述代码都是针对固定的路由地址应用中间件，在NestJs中路由地址是通过装饰器定义的，如果控制器的路由地址有变化，而中间件这里没有跟着改掉，就会导致问题。

NestJs在使用中间件的时候提供了基于控制器来注册的方式：

```ts
import { Module, NestModule, MiddlewareConsumer } from '@nestjs/common';
import { LogMiddleware } from './common/middleware/log.middleware';
import { UserModule } from './user/user.module';

@Module({
  imports: [UserModule],
})
export class AppModule implements NestModule {
  configure(consumer: MiddlewareConsumer) {
    consumer
      .apply(LogMiddleware)
       .forRoutes(UserController);
  }
}
```

## 排除指定路由

有些场景下对控制器应用了中间件之后需要绕过其中几个方法，比如登录验证中间件应该放行登录路由，否则没有人能够登录成功。

```ts
import { Module, NestModule, MiddlewareConsumer } from '@nestjs/common';
import { LogMiddleware } from './common/middleware/log.middleware';
import { UserModule } from './user/user.module';

@Module({
  imports: [UserModule],
})
export class AppModule implements NestModule {
  configure(consumer: MiddlewareConsumer) {
    consumer
      .apply(LogMiddleware)
      .exclude(
          {path:'users/login',method:RequestMethod.GET}
      )
       .forRoutes(UserController);
  }
}
```

## 全局中间件

类似于全局模块，中间件也可以全局注册，对每一个路由都生效。

```ts
// main.ts
const app = await NestFactory.create(AppModule);
app.use(LogMiddleware);
await app.listen(3000);
```

## 结尾

中间件给框架赋予了极大的灵活性，可以根据功能抽象为中间件，达到”可插拔“的目的。
