---
title: Javavscript基础——原型和原型链
date: 2019-09-23 12:00:00
categories:
- frontend
- javascript
---

本文研究一下Javascript的核心基础——原型链和继承。

对于使用过基于类的语言(如Java或C#)的人来说，Javascript的继承有点难以搞懂，因为它本身没有`class`这种东西。(ES6中引入了`class`关键字，看上去也像传统的OOP语言，但是那只是语法糖，底层还是基于原型)。

## 原型链

MDN上对于原型链的解释：

> 当谈到继承时，JavaScript 只有一种结构：对象。每个实例对象（ object ）都有一个私有属性（称之为 `__proto__` ）指向它的构造函数的原型对象（`prototype` ）。该原型对象也有一个自己的原型对象( `__proto__` ) ，层层向上直到一个对象的原型对象为 `null`。根据定义，`null` 没有原型，并作为这个**原型链**中的最后一个环节。
>
> 几乎所有 JavaScript 中的对象都是位于原型链顶端的 `Object` 的实例。

这段话可能难以理解，我们来举个例子：

```javascript
const list = []; // 定义数组
list.__proto__ === Array.prototype; // true
list.__proto__.__proto__ === Object.prototype; // true
list.__proto__.__proto__.__proto__===null; // true
// 继承关系为
// list -> Array.prototype -> Object.prototype -> null
```

结合MDN的解释，我们来解释一下上述例子：

list是`Array`的实例对象，使用了`字面量`的方式创建了`对象实例`。

> 每个实例对象（ object ）都有一个私有属性（称之为 `__proto__` ）指向它的构造函数的原型对象（`prototype` ）。

```javascript
// list的构造函数是Array，所以list.__proto__指向构造函数Array的原型对象。
list.__proto__ === Array.prototype; // true
```

> 该原型对象也有一个自己的原型对象( `__proto__` )

```javascript
// Array.prototype也是对象，也有自己的原型对象，原型是Object.prototype
// 下面是数学运算(等量代换)
// list.__proto__ = Array.prototype
// Array.prototype.__proto__ = Object.prototype
list.__proto__.__proto__ === Object.prototype; // true
```

> 层层向上直到一个对象的原型对象为 `null`。根据定义，`null` 没有原型，并作为这个**原型链**中的最后一个环节。

```javascript
// 目前我们来到了Object.prototype，根据规范，Object.prototype的原型对象为null
// list.__proto__ = Array.prototype
// Array.prototype.__proto__ = Object.prototype
// Object.prototype.__proto__ = null;
list.__proto__.__proto__.__proto__ === null; // true
```

### 原型链查找

> 当我们访问对象的属性或者方法时，会先从对象本身开始查找，如果查找不到，则查找对象的`__proto__`，层层向上查找，直到查找到属性，否则抛出错误。

```javascript
const list = [];
list.toString();
```

属性查找过程如下：

1. 查找list.toString()方法，没找到
2. 继续查找list.`__proto__`，也就是`Array.prototype`，找到了
3. 调用`Array.prototype.toString`

### 原型链结论

1. 对象实例.`__proto__` = 对象构造函数.`prototype`
2. 几乎所有对象的原型都是`Object.prototype`
3. null是对象，但是null没有原型
4. 属性/方法查找采用`优先返回`机制。

## 函数

经过原型链的简单介绍，相信大家对原型和原型链有了一个比较直观的了解了，现在要说到的是函数。

> 我们知道，Javascript中函数也是对象，所以`Function.__proto__`指向`Object.prototype`。

上面的结论在Javascript中是`有问题`的。我们来聊一聊函数。

先看看简单一点的例子，大家知道,`Object`是对象的`构造函数`，`构造函数`也是`函数`，所有的`函数`的原型都是`Function.prototype`，所以`Object.__proto__`是等于`Function.prototype`的。

事实证明，也是如此。

![image-20190923170248951](https://static.ddhigh.com/blog/2019-09-23-090412.jpg)

那么`Function.__proto__`为什么不等于`Object.prototype`呢?`Function`不是对象吗?

> Function确实是对象，同时还是构造函数，可以通过new Function()来得到函数实例。

上面我们说到所有`函数`的原型是`Function.prototype`，所以`Function这个构造函数`的原型`__proto__`等于`Function.prototype`。

基于以上原理，还有以下相等关系：

+ `Object.__proto__ === Function.prototype`
+ `Array.__proto__ === Function.prototype`

### 引申的问题

我们知道`Function.__proto__`是指向`Function.prototype`，那个`Function.prototype`这个`Function`哪里来的?`Function`自己创造自己?那不是会死循环吗?

> 这个问题不是纯JS层面能解决的，牵涉到底层实现，下面是网络上别人整理的结论，有需要的可以研究一下V8的源码，这样可以彻底解决这个问题。
>
> 1. 用C/C++ 构造内部数据结构创建一个 OP 即(Object.prototype)以及初始化其内部属性但不包括行为。
> 2. 用 C/C++ 构造内部数据结构创建一个 FP 即(Function.prototype)以及初始化其内部属性但不包括行为。
> 3. 将 FP 的[[Prototype]]指向 OP。
> 4. 用 C/C++ 构造内部数据结构创建各种内置引用类型。
> 5. 将各内置引用类型的[[Prototype]]指向 FP。
> 6. 将 Function 的 prototype 指向 FP。
> 7. 将 Object 的 prototype 指向 OP。
> 8. 用 Function 实例化出 OP，FP，以及 Object 的行为并挂载。
> 9. 用 Object 实例化出除 Object 以及 Function 的其他内置引用类型的 prototype 属性对象。
> 10. 用 Function 实例化出除Object 以及 Function 的其他内置引用类型的 prototype 属性对象的行为并挂载。
> 11. 实例化内置对象 Math 以及 Grobal
> 12. 至此，所有 内置类型构建完成。

### 函数结论

1. 函数的原型都是`Function.protype`,构造函数也是函数，所以构造函数的原型也是`Function.prototype`

## 来自灵魂的拷问1

下面是一道有点难度的JS基础题，可以感受一下：

```javascript
function A() {
  
}

function B(a) {
  this.a = a;
}

function C(a) {
  if(a) {
    this.a = a;
  }
}

A.prototype.a = 1;
B.prototype.a = 1;
C.prototype.a = 1;
console.log(new A().a);
console.log(new B().a);
console.log(new C().a);
```

输出是

```javascript
1
undefined
1
```

### 解释

1. 为什么输出`1`?

   > 因为new A()这个对象上没有属性a，所以去查找原型链，查到了F.prototype.a

2. 为什么输出`undefined`?

   > 因为new B时没有传递a，所以a是undefined，new B()这个对象是有a属性的，只不过值是undefined,所以不查原型链

3. 为什么输出`1`?

   > 因为new C()未传递a，所以a是undefined，由于if(a)的判断，new C()这个对象内部没有a属性，所以去查原型链

## 来自灵魂的拷问2

```javascript
function F() {
  this.a = 1;
}
F.prototype.b = 2;

var f = new F();
console.log(f.hasOwnProperty('a'));
console.log(f.hasOwnProperty('b'));
```

输出是

```text
true
false
```

## 解释

1. 为什么输出true`?

> 输出true比较好理解，因为构造函数`F`声明了属性`a`，所以`F`的实例有`a`属性

2. 为什么输出`false`?

> b是`f`的原型对象`F.prototype`的属性，不是`b`自己的，不能拿别人的说成自己的。

## 结尾

本文研究了原型和原型链之间的关系以及常见对象的原型和原型链，对于特殊对象Function也研究了一下，如果能搞懂后面两个问题，那本文对你来说没什么问题了。