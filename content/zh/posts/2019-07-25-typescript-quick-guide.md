---
slug: typescript-quick-guide
title: TS简明教程(1)
date: 2019-07-25 22:01:54
categories:
- Engineering
---

本文是TS简明教程的第一篇，对TS做简要介绍、基础知识以及后续内容规划。

> TypeScript是JavaScript的一个超集，支持 ECMAScript 6 标准。
> TypeScript可以在任何浏览器、任何计算机和任何操作系统上运行，并且是开源的。
> Typescript由微软开发，与C#出自同一人之手!

## TS与JS的区别

> TS是JS的超集，扩展了TS的语法，因此现有的JS代码可`直接与TS一起工作无需任何修改`，TS通过类型注解提供编译时的静态类型检查。

由于TS与JS语法大部分一致，本文只对有差异的部分进行讲解。

## 目录

有些知识点可能是交叉的建议通读完本文再开始真正的开发，这样疑惑会比较少一点

1. 数据类型与类型断言
2. 函数
3. 接口和类
4. 泛型
5. 枚举
6. 命名空间和模块
7. 装饰器(注解)
8. 高级类型
9. 声明文件
10. tsconfig.json
11. 示例
    1. React示例(前端)
    2. Koa示例(后端)

## 数据类型与类型声明

TS使用`:`语法对类型进行声明。基础类型如下：

### 布尔类型

TS使用`boolean`来声明布尔类型。

```typescript
let succeed: boolean = false; // 声明succeed为boolean类型
```

### 数字

TS对数字的支持与JS一致，所有数字都是浮点数，所以TS并不存在`int`,`float`之类的数字类型声明，只有`number`。
除了支持十进制和十六进制，TS还支持ES6的二进制和八进制数字。

```typescript
const age: number = 16; // 声明年龄为数字类型
const price: number = 99.99; // 声明价格为数字类型
```

### 字符串

TS使用`string`声明字符串，和JS一样，支持`单引号`和`双引号`。

```typescript
let name: string = "demo";

name = "demo1";

const description = `我是${name}`; // ES6语法
```

### 数组

TS使用`类型[]`声明数组的元素类型，与JS不一样的地方在于，`TS`中一旦指明一个类型，所有元素必须是该类型。`JS`则可以往数组放任意类型的元素。

```typescript
const numbers: number[] = [];
numbers.push(1);
numbers.push(2);
numbers.push('3'); // 错误，'3'不是数字类型
```

### 对象

与JS一样，TS的对象也是由`键值对`构成，类型声明可以分别作用与`键类型`以及`值类型`。

声明语法：`{[key名称: key类型]: 值类型}`
key名称可以`自定义`，如`key`,`index`都是合法的。

```typescript
const config: {[key: string]: string} = {}; // 声明键和值都只能是字符串类型
config.version = '1.0.0';

const ages: {[key: number]: number} = {}; // 声明键值对都是数字类型
ages[10] = '1.0.0'; // 赋值
```

上例中赋值语法虽然和数组一致，但是ages对象的长度为1，如果ages是数组的话，长度为11。(0-9个元素为undefined)

### 任意类型

TS用`any`用来声明`任意类型`，被`any`修饰的变量(或常量以及返回值等等)在编译阶段会`直接通过`，但是运行阶段可能会`抛出undefined或null相关错误`。

`any`的出现使得现有的JS代码能够很快速的切换到TS。

```typescript
let age:any = 10;
age = 'name'; // 编译通过
```

### 空类型

TS使用`void`声明空类型。与`any`相反，表示没有任何类型，常用在函数返回值中。
`void`类型只能被赋值为`null`和`undefined`。

```typescript
function test(name: string): void { // 声明函数无返回值，编译成JS之后取返回值会取到undefined，与JS一致
    console.log(name);
}

let v: void = null;
```

### null和undefined

TS中`默认情况`下，`null`和`undefined`是所有类型的子类型，换句话说，你可以把`null`和`undefined`直接赋值给`number`/`string`/`boolean`等类型。
但是不能反过来干，你不能把`number`/`string`/`boolean`类型赋值给`null`或者`undefined`

```
let u: undefined = undefined;
let n: null = null;
```

### never

`never`是`100%不存在的值`的类型。比如函数中直接抛出异常或者有死循环。

```typescript
function error(message: string): never {
    throw new Error(message);
}

function fail() { // TS自动类型推断返回值类型为never，类型推断在下文中会提到
    return error('failed');
}

function loop(): never { // 死循环，肯定不会返回
    while(true) {} 
}
```

`never`和`void`区别

1. 被`void`修饰的函数`能正常终止，只不过没有返回值`
2. 被`never`修饰的函数`不能正常终止，如抛出异常或死循环`

### 枚举

枚举是对JS的一个扩展。TS使用`enum`关键字定义枚举类型。

```typescript
enum Color {
    Red,
    Green,
    Yellow
}
let c: Color = Color.Red;
```

### Object

TS使用`object`类修饰对象类型，TS中表示`非原始类型`。原始类型如下：

1. number
2. string
3. boolean
4. null
5. undefined
6. symbol(ES6新出类型)

```typescript
let a: object = {}; // ok
let a: object = 1; // error
let a: object = Symbol(); / error
```

虽然`Symbol`长得像`对象类型`，不过在`ES6`规范中，人家就是`原始类型`。

### 函数声明

TS中可以对函数的`形参`以及`返回值`进行类型声明。

```typescript
function a(name: string, age: number): string {
    return `name:${name},age:${age}`;
}
```

### 类型断言

类型断言说白了就是`告诉编译器，你按照我指定的类型进行处理`。

```typescript
let value: any = 'a string';
const length: number = (<string>value).length;
```

编译结果(正常编译且正常运行)

```javascript
let value = 'a string';
const length = value.length;
```

### 类型推断

当没有手动指定类型时，TS编译器利用类型推断来推断类型。
如果由于缺乏声明而不能推断出类型，那么它的类型被视作默认的动态 any 类型。

```typescript
let num = 2; // 推断为number类型
```

## 函数

TS函数与JS函数没有大的区别，多了一个类型系统。

```typescript
function test(name: string) { // 自动推断返回类型为string
    return name;
}
```

### 可选参数

TS中函数每个形参都是`必须`的，当然你可以传递`null`和`undefined`，因为`他们是值`。但是在JS中，每个形参都是可选的，没传的情况下取值会得到`undefined`。
TS中`在参数名后面使用?号指明该参数为可选参数`

```typescript
function test(name: string, age?: number) {
    console.log(`${name}:${age}`);
}
test('a'); // 输出 a:undefined
```

### 默认参数

与ES6一致，TS也的函数也支持默认参数。需要注意的是`可选参数`和`默认参数`是`互斥`的。因为如果使用了默认参数，不管外部传不传值，取值的时候都是有值的，和可选参数矛盾。

```typescript
function test(name: string, age: number = 10) {
    console.log(`${name}:${age}`)
}
test('a'); // 输出 a:10
```

### 剩余参数

剩余参数和ES6表现一致，但是多了类型声明：

```typescript
function test(name1: string, ...names: string[]) {
    console.log(name1, names);
}
test('1','2','3');// 输出 1 ['2', '3']
```

### this执行

TS中this指向和JS一致，这里不做赘述。

## 结语

未完待续~
