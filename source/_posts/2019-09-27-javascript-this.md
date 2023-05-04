---
title: Javavscript基础——this指向
date: 2019-09-27 12:00:00
categories:
- engineering
---

本文研究一下Javascript的this指向。

Javascript的this指向问题，有些人可能觉得很简单，有些人却觉得扑朔迷离，看完本文之后相应会对this的掌握有一个直观的判断，而不是"开局全靠猜"。



## 敲黑板

1. function函数this指向由`调用方式`确定，跟定义环境无关。

2. 箭头函数this指向由`定义环境`决定，与`调用方式无关`，也不可以`bind(this)`。

   

## 严格模式

1. 非严格模式下，全局作用域下的this指向`window`

2. 严格模式下，全局作用域下的this指向`undefined`

   

以下讨论均为`非严格模式`，这个不影响今天的讨论。



## 实践

说结论往往是让人难以理解的，下面通过不同的调用场景对this做一个说明。

### 1. 直接调用

```javascript
function test() {
  console.log(this);
}
test(); // 输出undefined
```

直接调用是最简单的， 大部分人在这里都能回答的很好。



#### 总结

> 直接调用时this指向`全局作用域`。
>
> + 非严格模式this指向window
> + 严格模式this指向undefined

### 2. 对象调用

```javascript
'use strict'
var n = 1;
var a = {
  n: 2,
  b: function() {
  	console.log(this.n);
  }
};

a.b(); // 输出2
var b = a.b;
b(); // 输出1
```

#### 面试题：请问上述例子输出什么?

> 非严格模式下，输出2和1，严格模式下输出2和一个报错(this指向undefined，访问undefined的n属性肯定报错)

那如果你这么回答，`满分`!

#### 分析

知其然还要知其所以然，我们分析一下：

为什么输出2?

>  因为`a.b()`是对象调用方式，所以b()中的this指向a

为什么输出1?

这个非常有意思，而且也很有迷惑性，面试的时候经常问到，也经常有人被问倒。

```javascript
var b = a.b
```

把`a.b`赋值给`变量b`，b就是一个函数，`请注意: 这里只是赋值，没有调用，所以b中的this指向还不确定`。

```java
b();
```

调用函数`b`，这是什么调用方式? **`普通调用`**，所以this指向全局作用域。

#### 总结

对象调用方式下this指向调用对象。



是否GET? 如果没有GET，请关注公众号`NodeJs之路`，我在线给你答疑。

开胃菜已经吃了，下面来点"有难度的(实际上也没啥难度)"。



### 3. 嵌套对象调用

```javascript
var n = 1;
var a = {
  n: 2,
  b: {
    n: 3,
    c: function() {
      console.log(this.n)
    }
  }
};
```

#### 面试题：请问上述例子中function中的this指向哪里?

> 正确答案：`未确定调用环境`的情况下，this的指向`不确定`。
>
> 错误答案：指向a.b对象，Too young too simple!

```javascript
var n = 1;
var a = {
  n: 2,
  b: {
    n: 3,
    c: function() {
      console.log(this.n)
    }
  }
};

a.b.c(); // 输出3

a.c = a.b.c;
a.c(); // 输出2

var c = a.b.c; 
c(); // 输出1
```

这道题跟之前那道`对象调用`很像。

为什么输出3?

> 对象调用方式下指向调用对象，a.b.c()中c()是通过`a.b`对象调用，指向对象`a.b`

为什么输出?

> a.c = a.b.c 给a对象定义一个函数c，注意，此时没有调用！this指向不确定
>
> a.c() 通过a对象来调用c()，所以this指向对象`a`

为什么输出1？

> var c = a.b.c 函数赋值给普通变量，注意，此时没有调用!
>
> c(); 普通方式调用，指向window

#### 总结

嵌套对象调用方式下，this指向`最终调用`函数的对象。

`a.b.c.d.e.f.g.h()` h函数中的this指向`a.b.c.d.e.f.g`



### 4. 构造函数方式调用

```javascript
var name = 1;
function Person() {
  this.name = 2;
}

var p1= Person(); // p1为undefined
console.log(p1.name); // 报错

var p2 = new Person();
console.log(p2.name); // 输出2

```

p1为什么是undefined?

> 这道题比较坑，跟调用方式和this指向无关，因为Person函数没有返回值，js中，默认会返回undefined.

p2.name为什么是2?

> 使用new操作符时，构造函数的返回值`默认`指向对象实例，所以p2.name就是Person()中的this.name



如果在`Person()`函数中加上`return this`的话，`Person()`返回值还是`this`，因为这是普通调用。

### 5. 构造函数中指明返回值

原则上构造函数不应该有返回值，但是如果真的写了会怎么样？我们来探讨一下。

#### 返回复杂对象

```javascript
function Person() {
  this.name = 2;
  return {};
}
var p1 = new Person();
console.log(p1.name)// 输出undefined
```

#### 返回简单对象

虽然Js只有对象，但是有一些如string,number这种一般叫做简单对象,date,regex,array,object等等叫复杂对象。

```javascript
function Person() {
  this.name = 2;
  return 1;
}
var p1 = new Person();
console.log(p1.name)// 输出2
```

#### 返回null

使用`typeof null`返回的是`[object]`，证明null是个对象，不过咱们来看看构造函数返回null的表现。

```javascript
function Person() {
  this.name = 2;
  return null;
}
var p1 = new Person();
console.log(p1.name)// 输出2
```

#### 总结

构造函数中this指向对象实例本身，如果构造函数指明了返回值，那么表现如下：

+ 返回普通值，this指向不变，还是对象实例本身
+ 返回复杂对象，this指向新对象，也就是你new Person()返回的是那个新对象



### 6. bind

```javascript
  var a = {
    n: 1
  };
  var b = {
    n: 2
  }
  function f() {
    console.log(this.n);
  }
  var fa = f.bind(a);
  var fb = fa.bind(b);

  fa(); // 输出1
  fb(); // 输出1
```
  第1个输出1应该不难理解，bind可以更改function内部的this指向。多次bind已经bind过的函数，this指向不变。

bind的实现原理有点复杂，将在下一篇文章进行详细解读。

#### 总结

bind可以手动绑定function的this，`this`指向`第1次`bind时的this。

### 7. apply/call

这两个函数在this指向上表现一致，放到一起讲

```javascript
  var a = {
    n: 1
  };
  var b = {
    n: 2
  }
  function f() {
    console.log(this.n);
  }
  f.call(a); // 输出1
  f.apply(b); // 输出2
```

> call和apply的第1个参数为function执行时的this，这个this是确定的，对未使用过bind的函数进行多次apply/call，this指向都会改变。

### 8. 箭头函数

```javascript
var n = 1;
var b = {
  n: 2,
  a: () => {
    console.log(this.n);
  }
}
b.a(); // 输出1
b.a.call({n:3}); // 输出1
```

b.a定义时的this和`n`,`b`所在的`this一致`，默认情况下为全局作用域

> 箭头函数的this指向定义时所在的this，这个是明确的，但是如果定义时所在的是1个function，那么this指向同上面7点。

*说下我之前学JS遇到过的问题: ES5下function才会有作用域隔离, {}这种玩意不会隔离作用域。*



## 结尾

1. 直接调用this指向全局作用域window，严格模式指向undefined
2. 对象调用方式指向调用对象
3. 嵌套对象调用方式指向最终调用对象(离function最近的那个)
4. 构造函数方式调用指向对象实例
   1. 构造函数返回String/Number等简单类型时this指向不变，返回null指向也不变
   2. 构造函数返回Object/Array等复杂对象时，new Person()的返回值为return的对象
5. bind可以更改function的this,一经绑定，永不改变。`但是并不执行函数`
6. apply/call可以更改没有被bind过的this

7. 箭头函数的`this`指向为`定义`箭头函数的`this`