---
title: 实现一个JS深拷贝函数
date: 2019-07-16 11:17:59
tags:
- javascript
categories:
- frontend
---

JS深拷贝概念并不新鲜，但是真正要真正理解原理还是有点难度的。这也是JS语言精粹之一吧。

## 例子

```js
let a = {
    name: 'demo',
    age: 18
};

let b = a;
b.name = 'demo1';

console.log(a); // 输出 {name: "demo1", age: 18}
console.log(b); // 输出 {name: "demo1", age: 18}
```

因为JS对于对象的赋值使用的是浅拷贝，其中`一个实例变量`的赋值会影响到`所有指向该对象`的`变量`

## 解决方案

1. 粗暴好使的 `JSON.parse(JSON.stringify)`，缺点: `丢失成员函数`
2. `Object.assign`，缺点：`只有第一级深拷贝，子级对象依旧是浅拷贝`，例子如下：

    ```js
    let a = {name:{demo:'1'}};
    let b = Object.assign({}, a);
    console.log(a); // 输出 {name:{demo:'1'}}
    console.log(b); // 输出 {name:{demo:'1'}}
    b.name.demo = '2';
    console.log(a); // 输出 {name:{demo:'2'}}
    console.log(b); // 输出 {name:{demo:'2'}}
    ```

## 手动实现原理

1. 遍历待拷贝对象
2. 判断当前值类型，如果是object类型且不是null(null也是object)，则递归调用拷贝函数
3. 如果当前值类型时null或者非object类型，直接return，退出本次递归

## 编码实现

```js
function deepCopy(obj) {
    let result = obj;
    if(typeof obj === 'object' && obj !== null) {
        result = Object.prototype.toString.call(obj) === '[object Array]' ? []: {};
        for(let prop in obj) {
            result[prop] = deepCopy(obj[prop]);
        }
    }
    return result;
}
```

验证一下：

```js
let a = {name:{demo:'1'}};
let b = deepCopy(a);
console.log(a); // 输出 {name:{demo:'1'}}
console.log(b); // 输出 {name:{demo:'1'}}
b.name.demo = '2';
console.log(a); // 输出 {name:{demo:'1'}}
console.log(b); // 输出 {name:{demo:'2'}}
```
