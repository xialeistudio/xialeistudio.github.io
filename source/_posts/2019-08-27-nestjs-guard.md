---
title: NestJs学习之旅(7)——路由守卫
date: 2019-08-27 14:58:36
categories:
- nodejs
tags:
- nestjs
---

欢迎持续关注**NestJs学习之旅**系列文章

![img](/Users/xialeistudio/Documents/2019-08-26-060638.png)

传统的Web应用中去检测用户登录、权限判断等等都是在控制器层或者中间件层做的，而在目前比较推荐的模块化与组件化架构中，不同职责的功能建议拆分到不同的类文件中去。

通过前几篇的学习可以发现NestJs在这方面做的很好，传统的express/koa应用中，需要开发者去思考项目结构以及代码组织，而NestJs不需要你这样做，降低了开发成本，另外也统一了开发风格。

## 路由守卫

熟悉Vue,React的伙伴应该比较熟悉这个概念，通俗的说就是在访问指定的路由之前回调一个处理函数，如果该函数**返回true**或者**调用了next()**就会放行当前访问，否则阻断当前访问。

NestJs中路由守卫也是如此，通过继承**CanActive**接口即可定义一个路由守卫。

![img](/Users/xialeistudio/Documents/2019-08-27-055230.png)

```typescript
import { CanActivate, ExecutionContext, Injectable } from '@nestjs/common';
import { Observable } from 'rxjs';

@Injectable()
class AppGuard implements CanActivate {
  canActivate(context: ExecutionContext): boolean | Promise<boolean> | Observable<boolean> {
    return true;
  }
}
```

## 路由守卫与中间件

### 区别

路由守卫本质上也是中间件的一种，koa或者express开发中接口鉴权就是基于中间件开发的，如果当前请求是不被允许的，当前中间件将不会调用后续中间件，达到阻断请求的目的。

但是中间件的职责是不明确的，中间件可以干任何事（数据校验，格式转化，响应体压缩等等），这导致只能通过名称来识别中间件，项目迭代比较久以后，有比较高的维护成本。

### 联系

由于单一职责的关系，路由守卫只能返回true和false来决定放行/阻断当前请求，不可以修改request/response对象，因为一旦破坏单一职责的原则，排查问题比较麻烦。

如果需要修改request对象，可以结合中间件一起使用。

>  路由守卫在所有中间件执行完毕之后开始执行。

以下是一个结合路由守卫和中间件的例子。

```typescript
// auth.middleware.ts
// 中间件职责：读取请求头Authorization，如果存在且有效的话，设置user对象到request中
import { Injectable, NestMiddleware } from '@nestjs/common';
import { Request, Response } from 'express';

@Injectable()
export class AuthMiddleware implements NestMiddleware<Request|any, Response> {
  constructor(private readonly userService: UserService) {}
  async use(req: Request|any, res: Response, next: Function) {
    
    const token = req.header('authorization');
    if(!token) {
      next();
      return;
    }
    const user = await this.userService.getUserByToken(token);
    if(!user) {
      next();
      return;
    }
    request.user = user;
    next();
  }
}

```

```typescript
// user.guard.ts
import { CanActivate, ExecutionContext, Injectable } from '@nestjs/common';
import { Observable } from 'rxjs';
import { Request } from 'express';

@Injectable()
export class UserGuard implements CanActivate {
  canActivate(context: ExecutionContext): boolean | Promise<boolean> | Observable<boolean> {
    const request = context.switchToHttp().getRequest<Request | any>();
    // 直接检测是否有user对象，因为无user对象证明无token或者token无效
    return !!request.user;
  }
}
```

以上例子是笔者常用的一种方法，这样职责比较清晰，而且user对象可以在其他中间件中读取。

## 使用路由守卫来保护我们的应用

NestJs使用**@UseGuards()**装饰器来注入路由守卫。支持全局守卫、控制器级别守卫、方法级别守卫。

下面以一个实际的例子来演示路由守卫的工作过程。

### 登录流程

1. 用户输入账号密码后进行登录，如果登录成功下发Token
2. 客户端在请求头Authorization中加入第1步下发的Token进行请求
3. 路由守卫读取当前请求的Authorization信息并与数据库的进行比对，如果成功则放行，否则阻断请求

### 定义token校验业务类

```typescript
// user.service.ts
@Injetable()
export class UserService {
  // 模拟校验，这里直接返回true，实际开发中自行实现即可
  validateToken(token: string) {
    return true;
  }
}
```

### 定义路由守卫

```typescript
// user.guard.ts
@Injetable()
export class UserGuard implements CanActive {
  constructor(private readonly userService: UserService) {}

  canActivate(context: ExecutionContext): boolean | Promise<boolean> | Observable<boolean> {
    const request = context.switchToHttp().getRequest<Request>();
    // 读取token
    const authorization = request.header('authorization');
    if (!authorization) {
      return false;
    }
    return this.userService.validateToken(authorization);
  }
}
```

### 定义控制器

```typescript
@Controller('user')
export class UserController {
  // 请求登录
  @Post('login')
	login() {
		return {token:'fake_token'}; // 直接下发token，真实场景下需要验证账号密码    
  }
  
  // 查看当前用户信息
  @Get('info')
  @UseGuards(UserGuard) // 方法级路由守卫
  info() {
    return {username: 'fake_user'};
  }
}
```

一个完整的路由守卫应用实例就已经出来了，虽然咱们的路由守卫没啥逻辑都是直接放行的，但是实际开发中也是基于这种思路去开发的，只不过校验的逻辑不一样罢了。

## 路由守卫级别

### 控制器级别

该级别会对被装饰控制器的所有路由方法生效。

```typescript
@Controller('user')
@UseGuards(UserGuard)
export class UserController {
  // 查看当前用户信息
  @Get('info')
  info() {
    return {username: 'fake_user'};
  }
}
```

### 方法级别

该级别只对被装饰的方法生效。

```typescript
@Get('info')
@UseGuards(UserGuard)
info() {
  return {username: 'fake_user'};
}
```

### 全局级别

与全局异常过滤器类似，该级别对所有控制器的所有路由方法生效。该方法与全局异常过滤器一样不会对WebSocket和GRPC生效。

```typescript
async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  // 由于main.ts启动时并未初始化依赖注入容器，所以依赖必须手动传入，一般情况下不建议使用全局守卫，因为依赖注入得自己解决。
  app.useGlobalGuards(new UserGuard(new UserService()));
  await app.listen(3000);
}

bootstrap();
```



## 执行上下文

**CanActive**接口的方法中有一个**ExecutionContext**对象，该对象为请求上下文对象，该对象定义如下：

```typescript
export interface ExecutionContext extends ArgumentsHost {
  getClass<T = any>(): Type<T>;
  getHandler(): Function;
}
```

可以看到继承了ArgumentHost，ArgumentHost在之前的异常处理文章中已经提到过了，这里不再赘述。

- getClass<T>() 获取当前访问的Controller对象（不是实例），T为调用时传入的具体控制器对象泛型参数
- getHandler() 获取当前访问路由的方法

例如访问 /user/info 时，getClass()将返回UserController对象（不是实例），getHandler()将返回info()函数的引用。

这个特性有什么作用呢？

> NestJs中可以使用反射来获取定义在方法、属性、类等等上面的自定义属性，这一点和Java的注解有点类似。

## 反射示例——基于角色的权限验证(RBAC)

### 定义角色装饰器

被角色装饰器装饰的控制器或者方法在访问时，路由守卫会读取当前用户的角色，与装饰器传入的角色相匹配，如果匹配失败，将阻断请求，否则将放行请求。

```typescript
// roles.decorator.ts
import { SetMetadata } from '@nestjs/common';

export const Roles = (...roles: string[]) => SetMetadata('roles', roles);
```

### 定义控制器

假设我们有一个只允许管理员访问的创建用户的接口：

```typescript
@Post('create')
@Roles('admin')
async create(@Body() createUserDTO: CreateUserDTO) {
  this.userService.create(createUserDTO);
}
```

### 定义路由守卫

```typescript
// role.guard.ts
import { Injectable, CanActivate, ExecutionContext } from '@nestjs/common';
import { Observable } from 'rxjs';
import { Reflector } from '@nestjs/core';

@Injectable()
export class RolesGuard implements CanActivate {
  constructor(private readonly reflector: Reflector) {}

  canActivate(context: ExecutionContext): boolean {
    // 获取roles元数据，roles与roles.decorator.ts中SetMetadata()第一个参数一致
    const roles = this.reflector.get<string[]>('roles', context.getHandler());
    if (!roles) { // 未被装饰器装饰，直接放行
      return true;
    }
    const request = context.switchToHttp().getRequest();
    const user = request.user; // 读取请求对象的user，该user对象可以通过中间件来设置（本文前面有例子）
    const hasRole = () => user.roles.some((role) => roles.includes(role));
    return user && user.roles && hasRole();
  }
}
```

以上就是读取自定义装饰器数据开发RBAC的例子，写的比较简陋，但是原理是一样的，代码量少的话便于理解核心。

## 异常处理

路由守卫返回false时框架会抛出ForbiddenException，客户端收到的默认响应如下：

```json
{
  "statusCode": 403,
  "message": "Forbidden resource"
}
```

如果需要抛出其他异常，比如UnauthorizedException，可以直接在路由守卫的canActive()方法中抛出。

另外，在这里抛出的异常时可以被异常过滤器捕获并且处理的，所以我们可以自定义异常类型以及输出自定义响应数据。

## 结尾

本文除了路由守卫之外另一个重要的知识是【自定义元数据装饰器】的使用，基于该装饰器可以开发很多令人惊艳的功能，这个就看各位看官的实现了。

如果您觉得有所收获，分享给更多需要的朋友，谢谢！

如果您想交流关于NestJs更多的知识，欢迎加群讨论！

![20190827145318](/Users/xialeistudio/Documents/200.png)