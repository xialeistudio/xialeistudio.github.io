---
title: TS简明教程(3)
date: 2019-07-30 10:12:29
categories:
- frontend
- typescript
---

本文是TS简明教程的第三篇，讲解泛型。

## 泛型

> 泛型程序设计（generic programming）是程序设计语言的一种风格或范式。泛型允许程序员在强类型程序设计语言中编写代码时使用一些以后才指定的类型，在实例化时作为参数指明这些类型。

泛型的出现有效的降低了代码重复率，同时也能很好的保留类型信息，降低运行期崩溃的概率。

## HelloWorld

假设有个函数，你给他啥类型，他就返回啥类型，代码如下：

```typescript
function getValue(arg: number):number {
    return arg;
}
```

如果需要支持字符串的话，有以下做法：
1. 复制一份代码，然后更改`number`为`string`
2. 把`number`改为`any`

但是以上做法有弊端，方法1会导致代码重复比较多，而且难以扩展（只能通过复制代码来扩展）；方法2的话会丢失变量类型信息，运行期可能会抛出异常。

因此，我们需要一种方法使返回值的类型与传入参数的类型是相同的。这里，我们使用了 类型变量，它是一种特殊的变量，只用于表示类型而不是值。

```typescript
function getValue<T>(arg: T): T {
    return arg;
}
```

调用

```typescript
const n = getValue<number>(2);
const s = getValue<string>('s');
```

说明，如果`arg:T`中`arg`是`可自动推导类型（一般不是any就能推导）`，那么`<>`之间的类型可以省略，如果`<>`指定了类型，但是`arg`类型不匹配的话，编译失败。

`T`是随便取的，你叫ABCD都没人管你

## 泛型函数

原型如下：

```typescript
function 函数名<泛型类型，有几个写几个，逗号分隔>(参数名: 参数类型，参数名:参数类型):返回值类型
```

传统风格

```typescript
function makeMap<K,V>(key: K, value: V):map<K,V> {
    return map<K,V>(key,value);
}
```

箭头函数风格

```typescript
const makeMap: <K,V>(key:K,value:V) => map<K,V> = { // <K,V>(key:K,value:V) => map<K,V> 类型声明
    return map<K,V>(key,value);
}
```

## 泛型接口

原型如下:

```typescript
interface 接口名称<泛型类型，有几个写几个，逗号分隔> {
    // 使用泛型约束
}
```

例子

```typescript
interface GenericFunction<T> {
    getValue(arg:T):T;
}
// 字符串类型
class Test implements GenericFunction<string> {
    getValue(arg:string):string {
        returna arg;
    }
}
// 数字类型
class Test2 implements GenericFunction<number> {
    getValue(arg:number):number {
        returna arg;
    }
}
const test = new Test();
console.log(test.getValue('111'));

const test2 = new Test2();
console.log(test.getValue(111));

```

## 泛型类

泛型类的使用和泛型接口差不多

```typescript
class GenericClass<T> {
    add(a: T, b: T):T;
}

const n = new GenericClass<number>();
console.log(n.add(1,1));

const s = new GenericClass<string>();
console.log(s.add('1','2'));
```

## 使用继承约束

Java中经常看到如下代码

```java
public class Generic<T extends Number>{
    private T key;

    public Generic(T key) {
        this.key = key;
    }

    public T getKey(){
        return key;
    }
}
```

上例中，T只能为`Number`子类。避免过大范围的泛型导致问题

TS也可以使用以上方法：

```typescript
class BeeKeeper {
    hasMask: boolean;
}

class ZooKeeper {
    nametag: string;
}

class Animal {
    numLegs: number;
}

class Bee extends Animal {
    keeper: BeeKeeper;
}

class Lion extends Animal {
    keeper: ZooKeeper;
}

function createInstance<A extends Animal>(c: new () => A): A {
    return new c();
}

createInstance(Lion).keeper.nametag;  // 编译OK
createInstance(Bee).keeper.hasMask;   // 编辑OK
```

以下代码可能难以理解

```typescript
function createInstance<A extends Animal>(c: new () => A): A
```

拆开来看:

1. <A extends Animal> 泛型约束，A必须是Animal子类
2. `new () => A` 箭头函数，约束了传入的值必须是构造方法
3. `:A` `createInstance`必须返回传入的构造函数的实例

## 结语

泛型有效减少了重复代码，同时也解决了类型强制转换的问题，在开发中要尽量使用泛型而不是`any`。
TS的泛型用法大部分都比这复杂，但是原理是一样的，不足之处，敬请包涵。
对TS有兴趣的小伙伴可以扫码加我进行交流
![微信](https://more-happy.ddhigh.com/Fg5UE615NzZ0dXo6_gUe6qpCJILG?imageView2/1/w/200)