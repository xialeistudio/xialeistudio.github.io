---
title: 不只是块级作用域，你不知道的let和const
date: 2019-10-22 12:00:00
categories:
- engineering
tags:
- es6
---

ES6新增了两个重要的关键字`let`和`const`，相信大家都不陌生，但是包括我在内，在系统学习ES6之前也只使用到了【不存在变量提升】这个特性。

+ **let**声明一个块级作用域的本地变量
+ **const**语句声明一个块级作用域的本地常量，不可以重新赋值

## 支持块级作用域

`var`定义的变量会提升到整个函数作用域内，`let/const`则支持块级作用域。

> 块级作用域: 由`{}`包裹的作用域（函数那种{}不算）

来看一个`var`的例子:

```javascript
{
  var a = 1;
}
console.log(a);
```

此时输出1，因为`var`没有块级作用域。

来看一个`let`的例子(`const`效果一样):

```javascript
{
  let a = 1;
}
console.log(a);
```

此时会报错`ReferenceError`，因为`let/const`支持块级作用域，所以`let`定义的`a`只在`{}`可以访问

## 不存在变量提升

与`var`不同的是，`let/const`声明的变量不存在变量提升，也就是说`{}`对于`let/const`是有效的。

来看一个`var`的例子:

```javascript
console.log(a);
var a = 1;
```

此时会输出undefined，因为var声明的变量会提升到作用域顶部（只提升声明，不提升赋值）

来看一个`let`的例子(`const`效果也一样):

```javascript
console.log(a);
let a = 1;

```

此时会报错`ReferenceError`，因为`let`不存在变量提升

## 同一作用域内不可以重复声明

同一作用域内`let/const`不可以重复声明,`var`可以。

来看一个`var`的例子:

```javascript
var a = 1;
var a = 2;
console.log(a);
```

此时会输出2，var是支持重复声明的，后面声明的值会覆盖前面声明的值。

来看一个`let`的例子(`const`效果也一样):

```javascript
let a = 1;
let a = 2;
console.log(a);
```

此时会报错`SyntaxError`，因为同一作用域内`let/const`不可以重复声明。

再来看一个不同作用域的例子：

```javascript
let a = 1;
{
  let a = 2;
}
console.log(a);
```

此时输出1，因为两者作用域不同

## 暂存死区

**暂存死区TDZ(Temporal Dead Zone)**是ES6中对作用域新的语义。

通过`let/const`定义的变量直到执行他们的初始化代码时才被初始化。在初始化之前访问`该变量`会导致`ReferenceError`。该变量处于`一个自作用域顶部到初始化代码`之间的“暂存死区”中。

来看以下例子：

```javascript
function do_something() {
  console.log(bar); // undefined
  console.log(foo); // ReferenceError
  var bar = 1;
  let foo = 2;
}
do_something();
```

`var`定义的变量声明会提升到作用域顶部，所以`bar`是undefined，而`let`定义的变量`从作用域开始到let foo=2`这中间都无法访问，访问会报错`ReferenceError`

## 暂存死区与typeof

typeof检测var定义的变量或者检测不存在的变量时会返回undefined，如果检测暂存死区内的变量，会报错`ReferenceError`.

```javascript
console.log(typeof foo); // undefined
console.log(typeof bar); // ReferenceError
console.log(typeof bar2); // undefined
let bar = 1;
var bar2 = 2;
```

也就是说typeof去检测未初始化的`let`变量时会报错，`var`或者未声明的变量不会报错

## 面试题

```javascript
function test(){
   var foo = 33;
   {
      let foo = (foo + 55);
   }
}
test();
```

以上函数执行结果是什么?为什么?

> 报错
>
> `{}`内有`let`定义的`foo`，所以存在暂存死区，`(foo + 55)`这个表达式是在`let foo`之前执行的(赋值时先执行等号右边的，执行完毕把结果赋给等号左边)，表达式执行的时候还没有初始化foo，所以报错`ReferenceError`

## 总结

1. let/const支持函数作用域和块级作用域,var只有函数作用域
2. let/const不存在变量提升，var存在变量提升
3. let/const同一作用域内不可以重复声明，var可以重复声明
4. let/const存在暂存死区，var不存在

## 面试题

```javascript
let b = 1;

function test4() {
    console.log(b);
    let b = 2;
}
test4()
```

![0.jpeg](https://static.ddhigh.com/blog/2019-10-22-102654.jpg)

