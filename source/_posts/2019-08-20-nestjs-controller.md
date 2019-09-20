---
title: NestJs学习之旅(2)——控制器
date: 2019-08-20 10:10:21
categories:
- backend
- nodejs
tags:
- nestjs
---

本文是NestJs学习之旅的第二篇，主要讲解控制器。

## MVC

说到控制器就不得不说经典的MVC架构。

> MVC模式（Model–view–controller）是软件工程中的一种软件架构模式，把软件系统分为三个基本部分：模型（Model）、视图（View）和控制器（Controller）。
> + 控制器（Controller）- 负责转发请求，对请求进行处理，处理完毕后输出响应。
> + 视图 （View） - 界面设计人员进行图形界面设计
> + 模型 （Model）- 数据库查询和业务逻辑

可以看到控制器起着承上启下的作用，是Web开发中必备的一环，视图和模型倒不是必须的，理由如下：
1. API项目直接输出JSON数据，无需渲染页面
2. 无数据库或者复杂业务逻辑的项目时可以把请求处理直接在控制器完成

## 路由

控制器的目的是接收应用程序的特定请求。基于路由机制来实现请求的分发。通常，每个控制器具有多个路由，并且不同的路由可以执行不同的动作。

为了创建一个基本的控制器，我们使用类和装饰器。装饰器将类与所需的元数据相关联，并使Nest能够创建路由映射（将请求绑定到相应的控制器）。

## 控制器定义

使用`@Controller`装饰器来定义控制器，传入一个可选的路由前缀可以将该控制器绑定到该前缀。

```typescript
import { Controller, Get } from '@nestjs/common';

@Controller('cats')
export class CatsController {
  @Get('list')
  findAll(): string {
    return 'This action returns all cats';
  }

  @Get('show')
  fineOne(): string {
    return 'one cat';
  }

  @Get()
  index():string {
    return 'index';
  }
}
```

以上例程会生成以下路由：

1. GET /cats/list CatsController::findAll方法处理
2. GET /cats/show CatsController::show方法处理
3. GET /cats CatsController::index方法处理

上述例程使用的是`@Get`装饰器，所以只能处理`GET`请求，以下是支持的请求方法与对应的装饰器

| 请求方法 | 装饰器名称 | 说明             |
| :------- | :--------- | :--------------- |
| GET      | @Get       | 匹配GET请求      |
| POST     | @Post      | 匹配POST请求     |
| PUT      | @Put       | 匹配PUT请求      |
| HEAD     | @Head      | 匹配HEAD请求     |
| DELETE   | @Delete    | 匹配DELETE请求   |
| OPTIONS  | @Options   | 匹配OPTIONS请求  |
| -        | @All       | 匹配所有请求方法 |

## 动态路由

上文中的路由方法接收的参数是固定的，所以只能匹配固定的请求，如果路由地址是动态变化的(`路由地址指请求的path，不包括QueryString`)，则上述路由定义方式无法正常工作。

NestJs支持基于路径的路由定义，使用如下：

```typescript
import {@Controller, Get} from '@nestjs/common';

@Controller('cats')
class CatsController {
    @Get(':id')
    findOne(@Param() params): string {
        console.log(params.id);
        return `This action returns a #${params.id} cat`;
    }
}
```

当请求`/cats/猫ID`这种动态路由时(`因为猫ID是path的一部分，所以path是变化的`)，`params.id`就是`猫ID`，做过Vue或者React开发的读者应该熟悉以下写法：

路由定义 `/user/:userId/orders/:orderId`
页面地址 `/user/1/orders/2`

访问以上页面将产生以下参数:

+ userId => 1
+ orderId => 2

NestJs在这方面是一致的。

## 请求参数

上述例子中，我们使用`@Params`读取了请求路径上的动态参数。NestJs还支持以下的装饰器来获取不同的请求参数

| 装饰器名称             | 底层对象                      | 说明                   |
| :--------------------- | :---------------------------- | :--------------------- |
| @Request()             | req                           | 原始请求对象           |
| @Response()            | res                           | 原始响应对象           |
| @Param(key?:string)    | req.params或req.params[key]   | 路径参数               |
| @Body(key?:string)     | req.body或req.body[key]       | 请求体，支持表单或JSON |
| @Query(key?:string)    | req.query或req.query[key]     | 请求链接的查询字符串   |
| @Headers(name?:string) | req.headers或req.headers[key] | 请求头                 |

## 请求体

在POST/PUT/PATCH请求中，会包含请求体，NestJs通过`@Body`装饰器可以自动获取该数据。比如如下代码:

```ts
@Controller('user')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post()
  findAll(@Body() data: any) {
    return data;
  }
}
```

以上例程会原样输出请求内容。

### 请求体绑定

SpringBoot中`@RequestBody`注解可以直接绑定到给定的POJO对象实现请求参数自动注入，在NestJs中，该特性也得到了支持。

定义DTO对象

```ts
export class UserLoginDTO {
    readonly username: string;
    readonly password: string;
}
```

定义控制器

```ts
@Controller('users')
class UserController() {
    @Post('login')
    login(@Body() userLoginDTO: UserLoginDTO) {
        console.log(userLoginDTO.username, userLoginDTO.password);
    }
}
```

可以看到与SpringBoot的开发体验几乎一致。

## 响应头

如果需要输出响应头，可以使用`@Header(name:string,value:string)`装饰器来进行处理。

`请注意：响应头使用@Header()装饰器，请求头使用@Headers()装饰器，末尾有个s的区别!`

```ts
@Controller('users')
class UserController {
    @Head(':id')
    @Header('x-version', '1.0.0')
    function head(@Param('id') id:number) {
    }
```

## 响应状态码

从响应体的设计可以发现一个问题，由于不推荐直接操纵`response`对象，如果需要输出响应状态码怎么办?NestJs也为我们提供了解决方案。

使用`@HttpCode(statusCode:number)`装饰器可以设定响应状态码。

在Restful API设计中，DELETE请求应当返回`204 No Content`状态码，如下代码所示：

```ts
@Controller('users')
class UserController {
    @DELETE(":id")
    @HttpCode(204)
    delete(@Param('id') id:number) {
        // 删除成功不需要返回数据
    }
}
```

## 响应体

在express或者开发中，响应内容都是我们手动赋值或者输出的，但是在NestJs，可以直接根据路由函数的返回值`类型`自动识别响应体类型。NestJs支持以下格式的响应：

| TS类型     | 响应类型                                | 响应格式         |
| :--------- | :-------------------------------------- | :--------------- |
| string     | 字符串                                  | text/html        |
| object     | JSON                                    | application/json |
| array      | JSON                                    | application/json |
| null       | 无(响应体长度为0)                       | 无               |
| undefined  | 无(响应体长度为0)                       | 无               |
| Promise<*> | 根据Promise返回的结果类型确定(规则如上) | -                |

## 异步路由函数

在前面的例子中，我们所有的路由处理函数都是同步的，但是在实际开发中基本不可能，一旦涉及到数据库访问、缓存访问就会存在IO，有IO就会有异步。

NestJs天生完美支持异步，有以下两种方法进行异步编程：

### Promise

```ts
@Get()
async findAll(): Promise<any[]> {
    return Promise.resolve([]);
}
```

### RxJs

RxJs中提供了`Observable`对象，NestJs可以自动订阅并获取最后一次产生的值。

```ts
@Get()
findAll: Observable<any[]> {
    return of([]); // of为RxJs操作符
}
```

## 实现一个Restful API

以下是基于Restful API规范开发的API，本文的主要内容为控制器，所以DTO对象的创建省略。
```ts
import { Controller, Get, Query, Post, Body, Put, Param, Delete } from '@nestjs/common';
import { CreateCatDto, UpdateCatDto, ListAllEntities } from './dto';

@Controller('users')
export class UsersController {
  // 创建用户，POST请求会自动返回201状态码，响应体为空
  @Post()
  create(@Body() dto: CreateUserDto) {
  }

  // 用户列表
  @Get()
  findAll() {
      return [
          {id:1,username:'a',password:'a'},
          {id:2,username:'b',password:'b'}
      ];
  }
  // 查看用户
  @Get(':id')
  findOne(@Param('id') id: number) {
    return {id,username:'mock username', password: 'mock password'};
  }

  // 更新用户，需要返回编辑后的用户资源
  @Put(':id')
  update(@Param('id') id: number, @Body() updateUserDto: UpdateUserDto) {
      return {id,username:'updated username',password: 'updated password'};
  }

  // 删除用户，返回204状态码
  @Delete(':id')
  @HttpCode(204)
  remove(@Param('id') id: number) {
   
  }
}
```
