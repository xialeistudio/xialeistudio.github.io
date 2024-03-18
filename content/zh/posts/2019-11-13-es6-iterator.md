---
slug: es6-iterator
title: 深入浅出ES6的迭代器
date: 2019-11-14 11:00:00
categories:
- Engineering
tags:
- es6
---

迭代器是ES2015中新增的规范，与之相关的for...of也是ES2015新增的。

本文来深入研究一下迭代器是什么，以及迭代器能够干什么？

或许你对for ... of的执行还不了解，比如什么情况下可以使用for ... of去遍历对象，什么情况下会报错等等，这篇文章应该能帮到你。

## 迭代器协议

>  for ... of只能迭代满足【迭代器协议】的对象

可迭代对象的必须存在[Symbol.iterator]方法，该方法一个无参函数，返回迭代器协议的对象。

迭代器对象包含一个`next()`函数，该函数返回值有两种:

+ 如果迭代未结束，返回如下

  ```javascript
  return {
    value: 'item', // item是本次迭代值，可以为任意对象
    done: false
  }
  ```

+ 如果迭代已结束，返回如下

  ```javascript
  return {
    done: true
  }
  ```

下面是未提供迭代器的示例。

```javascript
const obj = {
  name: 'xialei',
  id: 1
};
for(let item of obj) { // TypeError: obj is not iterable
  
}
```

下面是提供迭代器的示例。

```javascript
const obj = {
    name: 'xialei',
    id: 1,
    [Symbol.iterator]: function () { // 迭代器属性
        const keys = Object.keys(this); // 读取对象键列表
        let keyIndex = 0; // 遍历未知
        const self = this; // 保存this，next中的function会有自己的this
        return { // 返回带有next()的对象
            next: function () {
                if (keyIndex < keys.length) { // 防止越界
                    const key = keys[keyIndex];
                    keyIndex++; // 移动到下一个位置
                    return {
                        value: [key, self[key]], // 键值对数组
                        done: false
                    }
                }
                return { // 遍历结束
                    done: true
                }
            }
        }
    }
};
```

通过给obj提供迭代器方法让obj也可以使用for...of遍历。

直接去理解迭代器概念比较困难，用一个简单的例子去简化理解是一件很容易的事情。

## 其他可迭代对象

`String`,`Array`,`Map`,`Set`,`TypedArray`是所有内置的可迭代对象，他们的原型对象都有一个[Symbol.iterator]方法。

下面是两种方法迭代String对象的示例。

```javascript
// for ... of
const str = 'xialei';
for(const char of str) {
  console.log(char);
}
// iterator
const str = 'xialei';
const iterator = str[Symbol.iterator](); // 返回一个{next:方法}对象
let obj = null;
do {
    obj = iterator.next(); // 返回的是对象，{value:任意对象,done:布尔型}
    console.log(obj.value);
}while(!obj.done);
```

## 结尾

迭代器协议虽然一般用的比较少，但是了解其原理是非常有必要的，这样才可以才需要的实现定义自己的迭代器来遍历对象。

![0.jpeg](https://static.ddhigh.com/blog/2019-10-22-102654.jpg)