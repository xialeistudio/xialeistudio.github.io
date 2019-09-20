---
title: NestJs学习之旅(4)——模块系统
date: 2019-08-22 11:27:38
categories:
- backend
- nodejs
tags:
- nestjs
---

欢迎持续关注`NestJs之旅`系列文章
![二维码](https://more-happy.ddhigh.com/FuFpZh9QTZVatcBtupR4MtOGPGTJ?imageView2/1/w/200)

## 模块

NestJs中模块是构建和组织业务单元的基本元素。使用`@Module()`装饰模块来声明该模块的元信息：

+ 本模块导出哪些服务提供者
+ 本模块导入了哪些依赖模块
+ 本模块提供了哪些控制器

每个NestJs至少有一个跟模块，这个就是`app.module.ts`定义的。根模块一般不放具体的业务逻辑，具体业务逻辑应该下沉到各个子业务模块去做。

比如我们开发一个商城系统，该系统有以下业务模块：

+ 订单中心
+ 用户中心
+ 支付中心
+ 商品中心
+ 物流中心

那我们可以定义以下的模块结构:

```
|-- app.module.ts
|-- order
    |-- order.module.ts
    |-- services
        |-- order.service.ts
    |-- controllers
        |-- order.controller.ts
|-- user
    |-- user.module.ts
    |-- services
        |-- user.service.ts
    |-- controllers
        |-- user.controller.ts
|-- pay
    |-- pay.module.ts
    |-- services
        |-- wepay.service.ts
        |-- alipay.service.ts
        |-- pay.service.ts
    |-- controller
        |-- pay.controller.ts
...
```

模块化有以下优点：

+ 业务低耦合
+ 边界清晰
+ 便于排查错误
+ 便于维护

## 模块声明与配置

`@Module()`装饰的类为`模块类`，该装饰器的典型用法如下：

```ts
@Module({
    providers: [UserService],
    controllers: [UserController],
    imports: [OrderModule],
    exports: [UserService]
})
export class UserModule {

}
```

| 参数名称    | 说明                                                                       |
| :---------- | :------------------------------------------------------------------------- |
| proviers    | 服务提供者列表，本模块可用，可以自动注入                                   |
| controllers | 控制器列表，本模块可用，用来绑定路由访问                                   |
| imports     | 本模块导入的模块，如果需要使用到其他模块的服务提供者，此处必须导入其他模块 |
| exports     | 本模块导出的服务提供者，只有在此处定义的服务提供者才能在其他模块使用       |

## 模块重导出

ts中有以下用法：

```ts
// a.ts
export interface A {

}
```

```ts
// index.ts
export * from './a';
```

我们在使用的时候直接使用以下代码即可，方面封装

```ts
import {A} from './index'
```

NestJs中的模块也有类似用法，比如我们定义了两个基本模块，这两个基本模块用的时候基本都是一起导入的，此时我们通过模块重导出将其封装到一个叫`CoreModule`，其他地方直接导入`CoreModule`即可。

```ts
@Module({
    providers: [CommonService],
    exports: [CommonService]
})
export class CommonModule {}
```

```ts
@Module({
    providers: [Util],
    exports: [Util]
})
export class UtilModule {}
```

```ts
@Module({
    imports: [CommonModule, UtilModule],
    exports: [CommonModule, UtilModule]
})
export class CoreModule {}
```

## 模块初始化与依赖注入

如果需要在模块实例化的时候运行一些逻辑，而且该逻辑有外部依赖的时候，可以通过以下方式处理

```ts
import { Module } from '@nestjs/common';
import { UserController } from './user.controller';
import { UserService } from './user.service';

@Module({
  controllers: [UserController],
  providers: [UserService],
})
export class catsModule {
  constructor(private readonly userService: UserService) { // 没有@Inject
    // 调用userService
  }
}
```

## 全局模块

上面定义的模块都是需要手动`imports`进来的，如果有些模块是使用率很高的，比如工具模块，此时可以声明为全局模块。

使用`@Global()`即可声明全局模块。

```ts
import { Module } from '@nestjs/common';
import { UserController } from './user.controller';
import { UserService } from './user.service';

@Global()
@Module({
  controllers: [UserController],
  providers: [UserService],
})
export class catsModule {
  
}
```

## 动态模块

上面定义的都是静态模块，如果我们需要动态声明我们的模块，比如数据库模块，连接成功我才返回模块，此时需要使用动态模块来处理。

使用`模块名.forRoot()`方法来返回模块定义，通过该方式定义的即为动态模块。

```ts
@Module({
    providers: [DatabaseProvider]
})
export class DatabaseModule {
    static async forRoot(env: string) {
         const provider =  createDatabaseProvider(env); // 根据环境变量连接不同的数据库
         return {
             module: DatabaseModule,
             providers: [provider],
             exports: [provider]
         }
    }
}
```

```ts
// user.module.ts
@Module({
    imports: [DatabaseModule.forRoot('production')]
})
export class UserModule {}
```

## 生产环境下的姿势

上面有一个商城系统的模块例子，当我们的业务模块开发完毕之后，需要将其注册到AppModule，这样才能生效，这个也有个好处，有点像插拔的例子，当需要下掉一个业务时，业务代码不动，在AppModule取消注册即可。

```ts
@Module({
    imports:[UserModule,GoodsModule,OrderModule,PayModule]
})
export class AppModule {}
```

## 结尾

模块系统是NestJs另一个重要的特性，个人认为是基于DDD思想的，每个模块就是一个单独的领域业务，可以由一个小组去独立开发。多个模块时可以同时开发，如果有依赖问题的话，可以先把模块和响应的interface公开出去，别人正常调用你的interface，当实现类开发完毕之后NestJs会自动注入该实现类，调用方的代码不用更改。

如果您觉得有所收获，分享给更多需要的朋友，谢谢！

如果您想交流关于NestJs更多的知识，欢迎加群讨论！

![image](https://more-happy.ddhigh.com/Fi58A_3OsMbbcZLL0c0Sx982T-Nx?imageView2/1/w/200)