---
slug: typescript-quick-guide4
title: TS简明教程(4)
date: 2019-08-06 15:37:39
categories:
- Engineering
---
本文是TS简明教程的第四篇，讲解装饰器。

## 装饰器

装饰器是一种特殊类型的声明，它能够被附加到类声明，方法，访问符，属性或参数上。 装饰器使用`@expression`这种形式，expression必须是一个函数，它会在运行时被调用，被装饰的声明信息做为参数传入。

> Typescript中的装饰器是一项实验性功能，需要在tsconfig.json中开启该特性

```json
{
    "compilerOptions": {
        "experimentalDecorators": true
    }
}
```

例如，有一个`@sealed`装饰器，我们这样定义`sealed`:

```typescript
function sealed(target: any) {
    // 操作被装饰对象
}
```

## 装饰器工厂

如果需要给装饰器添加一些动态行为，比如开发一个监控统计的装饰器，需要传入当前统计的事件名称，有多个事件名称时只需要变更传入的事件名而不用重复定义装饰器。

这时候需要使用到装饰器工厂。装饰器工厂也是一个函数，只不过它的返回值是一个装饰器。例如如下的事件监控装饰器：

```typescript
function event(eventName: string) {
    return function(target: any) {
        // 获取到当前eventName和被装饰对象进行操作
    }
}
```

## 装饰器组合

多个装饰器可以同时应用到被装饰对象上，例如下面的例子：

```typescript
@sealed
@test('test')
class Demo {

}
```

装饰器执行顺序：

1. 装饰器工厂需要先求值，再装饰，求值顺序是由上到下
2. 装饰器可以直接求值，装饰顺序是由下到上

上面的说明可以难以理解，下面举一个实际的例子：

```typescript
function f() {
    console.log('f求值');
    return function(target: any) {
        console.log('f装饰');
    }
}

function g() {
    console.log('g求值');
    return function(target: any) {
        console.log('g装饰');
    }
}

@f()
@g()
class Demo {

}
```

上例的执行顺序为

```text
f求值
g求值
g装饰
f装饰
```

因为先求值，所以在上面的f会比g先求值。因为装饰器是由下到上装饰，所以求值后的g比f先执行。

## 装饰器类型

根据被装饰的对象不同，装饰器分为以下几类：

1. 类装饰器
2. 方法装饰器
3. 属性装饰器
4. 函数参数装饰器

## 类装饰器

类装饰器在定义类的地方。类装饰器可以监视、修改或替换类定义。类的构造函数将作为唯一参数传递给装饰器。如果类装饰器返回一个值，它会使用返回的构造函数替换原来的类声明。

```typescript
function sealed(target: Function) {
    Object.seal(target);
    Object.seal(target.prototype);
}

@sealed
class Demo {}

```

下面来一个替换构造函数的示例：

```typescript
function replace<T extends {new(...args: any[]):{}}>(target: T) {
    return class extends target {
        newname = "newName";
        age = 18
    }
}

@replace
class Demo {
    oldname = "oldname";
    constructor(oldname: string) {
        this.oldname = oldname;
    }
}

console.log(new Demo("oldname"));
```

以上例程会输出

```text
class_1 { oldname: 'oldname', newname: 'newName', age: 18 }
```

可以看到通过装饰器新增的newname和age属性已经成功注入了。

## 方法装饰器

方法装饰器用来装饰类的方法（静态方法和实例方法都可以）。方法装饰器可以监视、修改或替换方法定义。
方法装饰器接收3个参数：

1. 类的原型对象，如果是静态方法则为类的构造函数
2. 方法名称
3. 方法的属性描述符

下面是一个`修改`方法行为的装饰器：

```typescript
function hack(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    const oldFunction = target[propertyKey]; // 获取方法引用
    const newFunction = function(...args: any[]) {
        console.log('call function ', propertyKey);
        oldFunction.call(target, ...args);
    }
    descriptor.value = newFunction; // 替换原声明
}

class Demo {
    @hack
    demo() {
        console.log('call demo');
    }
}

const demo = new Demo();
demo.demo();
```

以上例程输出如下：

```text
call function  demo
call demo
```

## 属性装饰器

属性装饰器用来装饰类的成员属性。属性装饰器接收两个参数：

1. 类的原型对象，如果是静态方法则为类的构造函数
2. 属性名

```typescript
function demo(value: string) {
	return function(target: any, propertyKey: string) {
		target[propertyKey] = value;
	}
}
class Demo {
    @demo('haha') name?: string;
}

const d = new Demo();
console.log(d.name);
```

属性装饰器多用在属性依赖注入上面

## 函数参数装饰器

参数装饰器表达式会在运行时当作函数被调用，传入下列3个参数：

1. 对于静态成员来说是类的构造函数，对于实例成员是类的原型对象。
2. 参数的名字。
3. 参数在函数参数列表中的索引。

```typescript
function PathParam(paramDesc: string) {
    return function (target: any, paramName: string, paramIndex: number) {
        !target.$meta && (target.$meta = {});
        target.$meta[paramIndex] = paramDesc;
    }
}

class Demo {
    constructor() { }
    getUser( @PathParam("userId") userId: string) { }
}

console.log((<any>Demo).prototype.$meta);
```

以上例程输出

```text
{ '0': 'userId' }
```

函数参数装饰器可以用在开发Web框架时自动注入请求参数。

## 结语

装饰器的介绍到这里就暂时结束了，装饰器的存在让Typescript有了与Java和C#等语言的注解相同的功能。当然，基于装饰器能做的工作是相当多的，注明的Angular2就大量使用了装饰器来分离业务逻辑。
对装饰器有想法的小伙伴可以扫码加我进行交流
![微信](https://more-happy.ddhigh.com/Fg5UE615NzZ0dXo6_gUe6qpCJILG?imageView2/1/w/200)