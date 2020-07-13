---
layout: post
title: JS函数不同执行环境下的this指向
date: 2015-08-20 11:49:39.000000000 +08:00
type: post
published: true
status: publish
categories:
- frontend
- javascript
---
> JavaScript中this指向一直是一个难点，也是一个重点，本文研究Node.js与浏览器环境下this指向的不同之处。

先来看一段代码

```javascript
var length = 10;
function fn() {
  console.log(this.length);
}

var obj = {
  length: 5,
  method: function(fn) {
    fn();
    arguments[0]();
  }
};

obj.method(fn,1);
```

猜猜输出结果？

## 浏览器环境

```bash
10
2
```

### 为什么输出10?
执行过程大致如下：   

obj.method这是个obj对象的方法，而传入的fn是个函数，fn()属于调用模式的"函数调用"。`非严格模式下，this为global对象（浏览器中就是window）`。   
而在这段代码的最上方使用var定义了length，由于var是直接写在global作用域中的，所以此处的 var length 与 window.length是同一个东西。输出10也就不奇怪了。

### 为什么输出2？
arguments这个是在函数内部才有的参数，很像array，而且typeof得到的也是object值，我们知道，js访问对象有 . 操作符 和 中括号操作符，此处使用的是第二种方法获取到obj.method的第一个参数，也就是fn
由于`arguments[0]()`是属于调用方式中的“方法调用模式”,this指向对象本身，也就是arguments，所以会输出2。

## NodeJs环境

```bash
undefined
2
```
### 为什么输出undefined？

**Node.js的global处理机制不同。**

global贯穿与Node.js整合生命周期，而每个js文件是单独的模块，就算使用var定义在顶层，也只是这个module的全局变量。所以会输出undefined。

### 为什么输出2？
同浏览器。