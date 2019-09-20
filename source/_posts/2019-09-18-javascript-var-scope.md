---
title: 搞懂JS变量提升
date: 2019-09-17 12:30:00
categories:
- frontend
- javascript
---

本文讲解Javascript变量提升引起的问题以及如何规避。

## 问题

今天看到一道有意思的面试题，考察的还真是JS的基本功，题目如下：

```javascript
var name = "world";

(function(){
  if(type name === "undefined") {
    var name = "Jack";
  	console.log("Hello " + name);
  } else {
    console.log("Hello " + name);
  }
}());
```

根据if条件可以得出可能的答案：

+ Hello world
+ Hello Jack

## 正确答案

答案是`Hello Jack`，但是答案怎么来的，回答不好可能还是只能打50分，有以下两种理解：

理解1：

> 立即执行函数有独立的作用域，访问不到外部name，所以if判断成立，输出 `Hello Jack`

这个理解是不正确的。虽然函数隔离了作用域，但是由于作用域链的关系，JS会从当前作用域一直往上级查找，直到顶级作用域（浏览器环境为window）。

如下代码输出`Hello world`

```javascript
var name = "world";

(function(){
  console.log("Hello " + name);
}());
```

理解2：

> var存在变量提升，所以if在判断的时候name确实为undefined，走了if分支，输出 `Hello Jack`

## 变量提升

MDN对变量提升的解释：

> “变量提升”意味着变量和函数的声明会在物理层面移动到代码的最前面，但这么说并不准确。实际上变量和函数声明在代码里的位置是不会动的，而是在编译阶段被放入内存中。
>
> + **JavaScript 仅提升声明，而不提升初始化**
> + **函数和变量相比，会被优先提升**

根据变量提升理论我们可以“模拟”JS实际执行代码的过程：

```javascript
var name = "world";

(function(){
  var name; // 变量提升，仅提升声明，不提升初始化
  if(type name === "undefined") {
    name = "Jack";
    console.log("Hello " + name);
  } else {
    console.log("Hello " + name);
  }
}());
```

函数内部作用域顶级的name初始化时为undefined，所以会走if分支，输出`Hello Jack`。这才是100分答案！

## 规避变量提升问题

> 1. 在作用域的顶部定义变量
> 2. 使用ES6新语法let或const定义变量

## 技术参考

+ [变量提升 - 术语表 | MDN](https://developer.mozilla.org/zh-CN/docs/Glossary/Hoisting)