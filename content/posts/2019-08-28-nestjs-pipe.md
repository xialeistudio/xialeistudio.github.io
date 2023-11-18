---
slug: nestjs-pipe
title: NestJs学习之旅(8)——管道
date: 2019-08-28 14:47:48
categories:
- Engineering
tags:
- nestjs
---
本文是NestJs学习之旅的第八篇，讲解管道。

## 管道

熟悉Linux命令的伙伴应该对“管道运算符”不陌生。

```bash
ls -la | grep demo
```

"|" 就是管道运算符，它把左边命令的输出作为输入传递给右边的命令，支持级联，如此一来，便可以通过管道运算符进行复杂命令的交替运算。

![img](https://static.ddhigh.com/blog/2019-08-28-054610.png)

NestJs中的管道有着类似的功能，也可以级联处理数据。NestJs管道通过**@Injectable()**装饰器装饰，需要实现**PipeTransform**接口。

NestJs中管道的主要职责如下：

- **数据转换** 将输入数据转换为所需的输出
- **数据验证** 接收客户端提交的参数，如果通过验证则继续传递，如果验证未通过则提示错误

## 执行顺序

在前面的文章中我们讨论了**中间件**、**控制器**、**路由守卫**，结合本问讨论的**管道**，可能有些读者会对这些组件的执行顺序提出疑问：这些东西执行的顺序到底是怎样的？

执行顺序也不用找资料，自己在这些组件执行时加上日志即可，我得出的结论如下：

> 客户端请求 -> 中间件 -> 路由守卫 -> 管道 -> 控制器方法

## 开发管道

数据转换类的管道就不详细解释了：

> 给你一个value和元数据，你的return值就是转换后的值。

NestJs内置了ValidationPipe、ParseIntPipe和ParseUUIDPipe。为了更好地理解它们的工作原理，我们以ValidationPipe（验证器管道）为例来演示管道的使用。

### PipeTransform

这是管道必须实现的接口，该接口定义如下：

```typescript
export interface PipeTransform<T = any, R = any> {
    transform(value: T, metadata: ArgumentMetadata): R;
}
```

- value <T> 输入参数，T为输入参数类型
- metadata <ArgumentMetadata> value的元数据，包括参数来源，参数类型等等
- <R> 输出参数，R为输出参数类型

### ArgumentMetadata

用来描述当前处理value的元数据接口，接口定义如下：

```typescript
export interface ArgumentMetadata {
  readonly type: 'body' | 'query' | 'param' | 'custom';
  readonly metatype?: Type<any>;
  readonly data?: string;
}
```

这个接口大家可能看不明白，没关系，等下会有具体示例来进行解读。

- type <string> 输入数据的来源
- metatype <Type<any>> 注入数据的类型
- data <string|undefined>传递给装饰器的数据类型

例如如下控制器方法：

```typescript
@Post()
login(@Query('type') type: number) { // type 为登录类型参数，类似手机号登录为1，账号登录为2的例子
  
}
```

上述例子的元数据如下：

- type query @Query装饰器是读取GET参数
- metatype Number type的类型符号
- data type 传递给@Query装饰器的参数为“type” 

## 验证器示例

下面以用户登录时校验账号密码来说明验证器管道的使用，规则如下：

- 账号必须是字符串，长度6-20
- 密码不能为空

### DTO定义

DTO在Java中是Data Transfer Object，简单来说就是对数据的一层包装。咱们NestJs中用这个东西一般是为了防止非法字段的提交和IDE自动提示（偷笑）。

使用规则装饰器需要安装class-validator和class-transformer：

```bash
npm i --save class-validator class-transformer
```

登录表单定义如下：

```typescript
// userLogin.dto.ts
export class UserLoginDto {
  @IsString()
  @Length(6, 20, { message: '长度不合法' })
  readonly username: string;
  @Length(1)
  readonly password: string;
}
```

### 管道定义

由于咱们的管道是通用的，也就是验证什么内容是由外部决定的，管道只负责“你给我数据和规则，我来校验”。所以咱们需要使用到装饰器元数据。

```typescript
// validate.pipe.ts
import { ArgumentMetadata, BadRequestException, Injectable, PipeTransform } from '@nestjs/common';
import { plainToClass } from 'class-transformer';
import { validate } from 'class-validator';

@Injectable()
export class ValidatePipe implements PipeTransform {

  async transform(value: any, { metatype }: ArgumentMetadata): Promise<any> {
    if (!metatype || !this.toValidate(metatype)) { // 如果不是注入的数据且不需要验证，直接跳过处理
      return value;
    }
    // 数据格式转换
    const object = plainToClass(metatype, value);
    // 调用验证
    const errors = await validate(object);
    // 如果错误长度大于0，证明出错，需要抛出400错误
    if (errors.length > 0) {
      throw new BadRequestException(errors);
    }
    return value;
  }

  /**
   * 需要验证的数据类型
   * @param metatype
   */
  private toValidate(metatype: any): boolean {
    const types = [String, Boolean, Number, Array, Object];
    return !types.includes(metatype);
  }
}
```

### 控制器定义

今天的主角是管道，所以控制器层就不写逻辑了

```typescript
// user.controller.ts
@Post('login')
@UsePipes(ValidatePipe)
login(@Body() userLoginDto: UserLoginDTO) {
  return {errcode:0, errmsg: 'ok'};
}
```

### 运行项目

项目根目录执行以下命令即可运行NestJs项目：

```bash
npm run start
```

项目运行后可以使用Postman来验证一下：

请求数据1

```json
{
	
}
```

响应数据1

```json
{
    "statusCode": 400,
    "error": "Bad Request",
    "message": [
        {
            "target": {},
            "property": "username",
            "children": [],
            "constraints": {
                "length": "长度不合法",
                "isString": "username must be a string"
            }
        },
        {
            "target": {},
            "property": "password",
            "children": [],
            "constraints": {
                "length": "password must be longer than or equal to 1 characters"
            }
        }
    ]
}
```

请求数据2

```json
{
	"username":"xialeistudio"
}
```

响应数据2

```json
{
    "statusCode": 400,
    "error": "Bad Request",
    "message": [
        {
            "target": {
                "username": "xialeistudio"
            },
            "property": "password",
            "children": [],
            "constraints": {
                "length": "password must be longer than or equal to 1 characters"
            }
        }
    ]
}
```

请求数据3

```json
{
	"username":"xialeistudio",
	"password":"111111"
}
```

响应数据3

```json
[]
```

### 注意事项

上文演示了ValidatePipe的实现，生产环境直接使用NestJs提供的ValidationPipe即可。我们可以在main.ts中使用全局管道。

```typescript
async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  app.useGlobalPipes(new ValidationPipe());
  await app.listen(3000);
}
bootstrap();
```



## 结尾

和笔者使用的SpringBoot中验证框架对比一下之后发现，NestJs验证管道所实现的功能还真不比SpringBoot差，看来官方说的“下一代Node.js全栈开发框架”确实不是盖的！

如果您想交流关于NestJs更多的知识，欢迎加群讨论！

![20190827145318](https://static.ddhigh.com/blog/2019-08-27-065355.jpg?imageView2/2/h/200)