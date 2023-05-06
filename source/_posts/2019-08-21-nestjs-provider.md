---
title: NestJs学习之旅(3)——服务提供者
date: 2019-08-21 10:27:42
categories:
- Engineering
tags:
- nestjs
---

本文是NestJs学习之旅的第三篇，讲解服务提供者。

## 简介

服务提供者是NestJs一个非常重要的概念，一般来说，被装饰器`@Injectable()`修饰的类都可以视为服务提供者。服务提供者一般包含以下几种：

+ Services(业务逻辑)
+ Factory(用来创建提供者)
+ Repository(数据库访问使用)
+ Utils(工具函数)

## 使用

下文中将以Services来说明服务提供者的具体使用。

典型的MVC架构中其实有一个问题，业务逻辑到底放哪里？

+ 放在控制器，代码复用成了问题，不可能去New一个控制器然后调用方法，控制器方法都是根据路由地址绑定的
+ 放在Model，导致Model层臃肿，Model应该是直接和数据库打交道的，业务逻辑跟数据库的关系并不是强制绑定的，只有业务逻辑涉及到数据查询/存储才会使用到Model层

现阶段比较流行的架构是多添加一个Services层来写业务逻辑，分离Model层不应该做的事情。

```typescript
// 业务类 user.service.ts
@Injectable()
export class UserServices {
  private readonly users: User[] = [];

  create(user: User) {
    this.users.push(user);
  }

  findAll(): User[] {
    return this.users;
  }
}
```

```ts
// 用户控制器
@Controller('users')
export class UserController {
    constructor(private readonly userService: UserService) {} // 注入UserService

    @Post()
    async create(@Body() createUserDTO:CreateUserDTO) {
        this.userService.create(createUserDTO);
    }

    @Get()
    async findAll() {
        return this.userService.findAll();
    }
}
```

## 服务提供者的Scope

SpringBoot中提供了Scope注解来指明Bean的作用域，NestJs也提供了类似的`@Scope()`装饰器：

| scope名称 | 说明                               |
| :-------- | :--------------------------------- |
| SINGLETON | 单例模式，整个应用内只存在一份实例 |
| REQUEST   | 每个请求初始化一次                 |
| TRANSIENT | 每次注入都会实例化                 |

```ts
@Injectable({scope: Scope.REQUEST})
export class UserService {

}
```

## 可选的依赖项

默认情况下，如果依赖注入的对象不存在会提示错误，中断应用运行，此时可以使用`@Optional()`来指明选择性注入，但依赖注入的对象不存在时不会发生错误。

```ts
@Controller('users')
export class UserController {
    constructor(@Optional() private readonly userService:UserService){}
}
```

## 基于属性的注入

上文中的注入都是基于构造函数的，这样做有一个缺陷，如果涉及到继承的话，子类必须显示调用`super`来实例化父类。如果父类的构造函数参数过多的话反而成了子类的负担。

针对这个问题，NestJs建议的方式是`基于属性`进行注入。

```ts
@Controller('users')
export class UserController {
    @Inject()
    private readonly userService:UserService;
}
```

## 服务提供者注册

只有被注册过的服务提供者才能被NestJs进行自动注入。

```ts
@Module({
    controllers:[UserController], // 注册控制器
    providers: [UserServices], // 注册服务提供者，可以是services,factory等等
})
export class UserModule {

}
```

## 自定义服务提供者

### 使用值

上文中提供的Services一般用在编写业务逻辑，结构基本是固定的，如果需要集成其他库作为注入对象的话，需要使用的自定义的服务提供者。

比如我们使用sequelize创建了数据库连接，想把他注入到我们的Services中进行数据库操作。可以使用以下方式进行处理：

```ts
// sequelize.ts 数据库访问
export const sequelize = new Sequelize({
    ///
});
```

```ts
// sequelize.provider.ts
import {sequelize} from './sequelize';

export const sequelizeProvider = {
    provide: 'SEQUELIZE', // 服务提供者标识
    useValue: sequelize, // 直接使用值
}
```

```ts
// user.module.ts
@Module({
    providers:[UserService, sequelizeProvider]
})
export class UserModule {}
```

```ts
// user.service.ts
@Injectable()
export class UserService {
    constructor(@Inject('SEQUELIZE') private readonly sequelize: Sequelize) {}
}
```

### 使用类

OOP的一个重要思想就是`面向接口化`设计，比如我们开发了一个日志接口，有写入本地文件的实现，也有写入syslog的实现。依赖注入到时候我们希望使用接口进行注入，而不是具体的实现。

```ts
// logger.ts
export interface Logger {
    log(log:string);
}
```

```ts
// file.logger.ts
export class FileLogger implements Logger {
    log(log:string) {
        // 写入本地文件
    }
}
```

```ts
// syslog.logger.ts
export class SyslogLogger implements Logger {
    log(log:string) {
        // 写入Syslog
    }
}
```

```ts
// logger.provider.ts
export const loggerProvider = {
    provide: Logger, // 使用接口标识
    useClass: process.env.NODE_ENV==='development'?FileLogger:SyslogLogger, // 开发日志写入本地，生产日志写入syslog
}
```

```ts
// user.module.ts
@Module({
    providers:[UserService,loggerProvider]
})
export class UserModule {

}
```

```ts
// user.service.ts
@Injectable()
export class UserService {
    constructor(@Inject(Logger) private readonly logger: Logger) {}
}
```

### 使用工厂

工厂模式相信大家都不陌生，工厂模式本质上是一个函数或者方法，返回我们需要的产品。

传统的第三方库都是提供callback形式或者事件形式的进行连接，比如redis，如果需要使用该类型的注入对象，工厂模式是最佳方式。

以下是使用工厂模式创建数据库连接的例子：

```ts
// database.provider.ts
export const databaseProvider = {
    provide:'DATABASE',
    useFactory: async(optionsProvider: OptionsProvider) { // 使用依赖，注入顺序和下面定义的顺序一致
        return new Promise((resolve, reject) => {
            const connection = createConnection(optionsProvider.getDatabaseConfig())
            connection.on('ready',()=>resolve(connection));
            connection.on('error',(e)=>reject(e));
        });
    },
    inject:[OptionsProvider], // 注入依赖
}
```

```ts
// user.module.ts
@Module({
    providers:[OptionsProvider, databaseProvider]
})
export class UserModule {

}
```

```ts
// user.service.ts
@Injectable()
export class UserService {
    constructor(@Inject('DATABASE') private readonly connection: Connection) {}
}
```

### 别名方式

别名方式可以基于现有的提供者进行创建。

```ts
const loggerAliasProvider = {
  provide: 'AliasedLoggerService',
  useExisting: Logger,
};
```

## 导出服务提供者到其他模块

模块的详细知识将在后文提到，但是有一点需要提前知道，`只有被模块导出的服务提供者才能被其他模块导入`

### 基于类型的导出

上文中的`UserService`是基于类型而不是进入名称进行注入的。

```ts
@Module({
    providers: [UserService],
    exports: [UserService], // 重要
})
export class UserModule {}
```

### 基于名称的导出

上文中`DATABASE`和`SEQUELIZE`这种服务提供者都是自定义的，而且指定的标识符。

```ts
@Module({
    providers: [sequelizeProvider],
    exports: ['SEQUELIZE'], // 其他模块的组件直接使用@Inject('SEQUELIZE')即可
})
```

## 结尾

服务提供者是NestJs的精华之一，提供了几种方式方便我们在各种环境下的服务提供者创建。
