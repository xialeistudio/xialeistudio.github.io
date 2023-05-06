---
title: nodejs unhandledRejection问题解决
layout: post
categories: 
- Engineering
---
今天在使用promise的时候没有catch掉错误，导致报错，类似于
```
unhandledRejection promise ....
```
而且不会显示trace信息，导致无从查错，经过google发现，需要监听进程的`unhandledRejection`事件，才能显示trace信息
```javascript
process.on('unhandledRejection', (...params) => {
  console.log(params);
});
```