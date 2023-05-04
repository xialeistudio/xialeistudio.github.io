---
title: NestJs学习之旅(1)——快速开始
date: 2019-08-19 10:10:13
categories:
- engineering
tags:
- nestjs
---

本文是NestJs学习之旅的第一篇，简要介绍一下NestJs框架，搭建一个Hello World应用。

## 介绍

Nest（或NestJS）是一个用于构建高效，可扩展的Node.js服务器端应用程序的框架。它使用渐进式JavaScript，内置并完全支持TypeScript（但仍然允许开发人员使用纯JavaScript编写代码）并结合了OOP（面向对象编程），FP（功能编程）和FRP（功能反应编程）的元素。

```javascript
import { Controller, Get } from '@nestjs/common';

@Controller('cats')
export class CatsController {
  @Get()
  findAll(): string {
    return 'This action returns all cats';
  }
}
```

熟悉Java的同学应该有似曾相识的感觉，SpringBoot中大量使用注解来简化开发。现在，使用基于ES6装饰器构建的NestJs框架，你也可以做到!

## 优缺点

先说说优点吧：

+ 完美支持Typescript，因此可以使用日益繁荣的TS生态资源
+ 兼容express中间件，降低造轮子成本
+ 完美支持响应式编程框架rxjs
+ 完美支持依赖注入
+ 模块化思想，方便开发以及后期维护
+ 使用装饰器简化开发，减少样板代码
+ 组件化设计，解决Node.js无全栈框架约束的现存问题

当然，"缺点"也是有点的，不过熟练之后这些都不是缺点：

+ 基于TS导致的语言门槛
+ 代码设计上对模块化/组件化思想有一定要求

## 第一个NestJs应用

使用NestJs的命令行工具，可以简化项目的创建以及项目文件的创建。

1. `npm install -g @nestjs/cli`安装命令行工具
2. `nest new 项目名称`初始化项目

初始化完毕后可以看到一个完整的项目结果，目录如下(忽略node_modules)：

```text
├── README.md                       自述文件
├── nest-cli.json                   NestJs项目配置
├── package.json                    npm文件
├── src                             项目源码
│   ├── app.controller.spec.ts      控制器测试文件
│   ├── app.controller.ts           控制器类
│   ├── app.module.ts               模块类
│   ├── app.service.ts              服务类
│   └── main.ts                     项目入口文件
├── test                            测试目录
│   ├── app.e2e-spec.ts             应用e2e测试
│   └── jest-e2e.json               jest e2e测试配置
├── tsconfig.build.json             生产环境Typescript所用
├── tsconfig.json                   开发环境Typescript配置
├── tslint.json                     tslint配置
└── yarn.lock                       yarn锁文件
```

NestJs有几大类文件是主要的是下面几种，其他类型的文件在后续课程会讲解；

+ module 模块声明(这是NestJs的一个亮点，有点DDD的思想)
+ controller 控制器(负责接收数据，返回响应)
+ service 服务(主要业务逻辑)
  

使用`npm run start`来运行项目。终端输出如下:

```text
[Nest] 2986   - 08/19/2019, 10:29 AM   [NestFactory] Starting Nest application...
[Nest] 2986   - 08/19/2019, 10:29 AM   [InstanceLoader] AppModule dependencies initialized +22ms
[Nest] 2986   - 08/19/2019, 10:29 AM   [RoutesResolver] AppController {/}: +12ms
[Nest] 2986   - 08/19/2019, 10:29 AM   [RouterExplorer] Mapped {/, GET} route +9ms
[Nest] 2986   - 08/19/2019, 10:29 AM   [NestApplication] Nest application successfully started +6ms
```

一般来说，看到`successfully`就可以认为启动成功了。启动失败的话可以根据错误提示进行处理，比较多的情况可能是端口占用导致的错误。

打开浏览器访问`http://localhost:3000`即可看到输出`Hello World!`。

## To Be Continued

下一期将介绍Controller，欢迎持续关注!