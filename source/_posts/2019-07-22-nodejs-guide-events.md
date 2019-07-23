---
title: NodeJs简明教程(7)
date: 2019-07-22 10:53:10
categories:
- nodejs
tags:
- javascript
- nodejs guide
---

> NodeJs简明教程将从零开始学习NodeJs相关知识，助力JS开发者构建全栈开发技术栈！

关注获取更多`NodeJs精品文章`
![二维码](https://more-happy.ddhigh.com/FuFpZh9QTZVatcBtupR4MtOGPGTJ?imageView2/1/w/200)

本文是NodeJs简明教程的第七篇，将介绍NodeJs events模块相关的基本操作。

> 大多数 Node.js 核心 API 构建于惯用的异步事件驱动架构，其中某些类型的对象（又称触发器，Emitter）会触发命名事件来调用函数（又称监听器，Listener）。

## 快速开始

使用事件监听器一般包含以下操作：

1. 新建事件监听器实例
2. 设置监听函数
3. 触发事件

```js
const EventEmitter = require('events'); // 引用模块

class MyEmitter extends EventEmitter {} // 初始化监听器

const myEmitter = new MyEmitter();

myEmitter.on('event', () => { // 设置监听函数
  console.log('an event occurred!');
});

myEmitter.emit('event'); // 触发事件
```

以上例程会输出`an event occurred!`

## 一次性事件监听

上文中的监听方式`事件触发几次`就会`输出几次an event occurred!`，有些事件可能是一次性的。这时候可以使用`once`监听。

```js
const EventEmitter = require('events'); // 引用模块

class MyEmitter extends EventEmitter {} // 初始化监听器

const myEmitter = new MyEmitter();

myEmitter.once('event', () => { // 设置监听函数
  console.log('an event occurred!');
});

myEmitter.emit('event'); // 触发事件
myEmitter.emit('event'); // 触发事件
```

以上例程会输出`1次` `an event occurred!`;

## 同一事件多次监听

上文中的监听方式都是只有`1个`监听函数，通过`多次调用on`可以设置多个监听函数。

```js
const EventEmitter = require('events');

class MyEmitter extends EventEmitter {}

const myEmitter = new MyEmitter();

myEmitter.once('event', () => { // 监听器1
  console.log('监听器1收到事件');
});

myEmitter.on('event', () => { // 监听器2
  console.log('监听器2收到事件');
})

myEmitter.emit('event'); // 触发事件
```

以上例程会输出

```text
监听器1收到事件
监听器2收到事件
```

## 接收事件参数

1. `emit`函数的第一个值为`事件名`,`后续参数为事件值`
2. `on`和`once`等监听器设置函数的回调函数收到的值`为emit传入的事件参数`

```js
const EventEmitter = require('events');

class MyEmitter extends EventEmitter {}

const myEmitter = new MyEmitter();

myEmitter.once('event', (param1,param2,param3) => { // 接收事件参数
  console.log('收到事件',param1,param2,param3);
});

myEmitter.emit('event','参数1','参数2',{name:'参数3'}); // 发送事件参数
```

以上例程会输出

```text
收到事件 参数1 参数2 { name: '参数3' }
```

## 获取事件监听器上所有事件

使用`eventNames()实例方法`获取监听器上所有事件

```js
const EventEmitter = require('events');

class MyEmitter extends EventEmitter {}

const myEmitter = new MyEmitter();

myEmitter.once('event', (param1,param2,param3) => {
  console.log('收到事件',param1,param2,param3);
});

myEmitter.once('event2',() => {
  console.log('收到事件2');
});

console.log(myEmitter.eventNames());
```

以上例程输出`[ 'event', 'event2' ]`

## 移除事件监听器

使用`off实例方法`移除单个监听器

```js
const EventEmitter = require('events');

class MyEmitter extends EventEmitter {}

const myEmitter = new MyEmitter();

const callback = (param1) => {
  console.log(param1);
};

myEmitter.on('event', callback); // 添加监听器

myEmitter.off('event', callback); // 移除监听器

myEmitter.emit('event'); // 触发事件
```

以上例程`没有输出`，因为`先添加监听器，随后移除，触发事件时已经没有可用的监听器了`

## 移除所有监听器

使用`removeAllListeners([eventName])实例方法移除所有监听器`。

1. removeAllListener`不传参数`时移除该`emitter实例`上`所有`事件监听器
2. removeAllListener传入`字符串`参数时移除该`emitter实例`上`所有该事件`的监听器

## 结语

事件系统是NodeJs的灵魂，在几乎所有的I/O模块都有使用，希望各位读者好好掌握。事件模块读后有疑问请加微信群讨论。

![微信群](https://more-happy.ddhigh.com/FpffwgkBeSWPyHRUJJmi9J9SFX_l?imageView2/1/w/200)
