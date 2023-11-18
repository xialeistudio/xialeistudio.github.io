---
slug: valueof-and-tostring
title: 聊一聊valueOf和toString
date: 2019-10-15 12:00:00
categories:
- Engineering
---
valueOf和toString是Object.prototype的方法。一般很少直接调用，但是在使用对象参与运算的时候就会调用这两个方法了。我想大部分人都存在以下疑问：

+ valueOf和toString哪个优先级较高?
+ 是不是所有场景都会调用valueOf和toString

## 概念解释

+ valueOf: 返回对象的原始值表示
+ toString: 返回对象的字符串表示

在介绍下面的内容之前先了解一下转换规则，下面的内容解释都是基于这个规则表来的：

### valueOf转换规则

valueOf是Object.prototype的方法，由Object来的对象都会有该方法，但是很多内置对象会重写这个方法，以适合实际需要。

说到原始值就必须说到原始类型，JS规范中 **原始类型** 如下：

+ Boolean
+ Null
+ Undefined
+ Number
+ String

非原始值(也就是对象)重写规则如下：

| 对象     | valueOf返回值        |
| -------- | -------------------- |
| Array    | 数组本身             |
| Boolean  | 布尔值               |
| Date     | 返回毫秒形式的时间戳 |
| Function | 函数本身             |
| Number   | 数字值               |
| Object   | 对象本身             |
| String   | 字符串值             |

> 以下规则是经过验证的，如果对验证过程不关心，可以只看转换规则。
>
> 建议看一下验证过程，这样可以加深理解

#### 对象转换为布尔值

1. 直接转换为true（包装类型也一样），不调用valueOf和toString

#### 对象转换为数字

在预期会将对象用作数字使用时，比如参与算术运算等等操作，对象转换为数字会依次调用valueOf和toString方法，具体规则如下：

1. 如果对象具有`valueOf`方法且返回原始值(string、number、boolean、undefined、null)，则将该原始值转换为数字(转换失败会返回NaN)，并返回这个数字
2. 如果对象具有`toString`方法且返回原始值(string、number、boolean、undefined、null)，则将该原始值转换为数字(转换失败会返回NaN)，并返回这个数字
3. 转换失败，抛出TypeError

#### 对象转换为字符串

1. 如果对象具有`toString`方法且返回原始值(string、number、boolean、undefined、null)，则将该原始值转换为字符串，并返回该字符串
2. 如果对象具有`valueOf`方法且返回原始值(string、number、boolean、undefined、null)，则将该原始值转换为字符串，并返回该字符串
3. 转换失败，抛出TypeError

### toString转换规则

| 对象     | toString返回值                                               |
| -------- | ------------------------------------------------------------ |
| Array    | 以逗号分割的字符串，如[1,2]的toString返回值为"1,2"           |
| Boolean  | "True"                                                       |
| Date     | 可读的时间字符串，如"Tue Oct 15 2019 12:20:56 GMT+0800 (中国标准时间)" |
| Function | 声明函数的JS源代码字符串                                     |
| Number   | "数字值"                                                     |
| Object   | "[object Object]"                                            |
| String   | "字符串"                                                     |

## 验证对象到原始值的转换

光看valueOf和toString没啥东西可说，日常开发中也很少直接调用，但是当我们将对象当做原始值来使用时会发生转换，而且转换过程还略微有点迷糊。

### 对象转换为Boolean

为了能够直观的看到JS内部的转换过程，我把valueOf和toString都简单重写了，加了日志。

```javascript
// 保存原始的valueOf
var valueOf = Object.prototype.valueOf;
var toString = Object.prototype.toString;

// 添加valueOf日志
Object.prototype.valueOf = function () {
    console.log('valueOf');
    return valueOf.call(this);
};
// 添加toString日志
Object.prototype.toString = function () {
    console.log('toString');
    return toString.call(this);
};
var a = {};
var b = new Boolean(false);

if (a) {
    console.log(1);
}
if(b) {
    console.log(2);
}
```

以上例子的输出如下：

```
1
2
```

> 未调用valueOf和toString，符合[对象到布尔值]的转换规则

### 对象转换为Number

#### 例子1

```javascript
// 保存原始的valueOf
var valueOf = Object.prototype.valueOf;
var toString = Object.prototype.toString;

// 添加valueOf日志
Object.prototype.valueOf = function() {
    console.log('valueOf');
    return valueOf.call(this);
};
// 添加toString日志
Object.prototype.toString = function() {
    console.log('toString');
    return toString.call(this);
};
var a = {};
console.log(++a);
```

输出如下：

```
valueOf
toString
NaN
```

#### 分析

1. valueOf方法返回的是对象本身，不是原始值，继续执行
2. toString方法返回的是"[object Object]"，是原始值(字符串)，将字符串转换为数字NaN

#### 例子2

```javascript
// 保存原始的valueOf
var valueOf = Object.prototype.valueOf;
var toString = Object.prototype.toString;

// 添加valueOf日志
Object.prototype.valueOf = function () {
    console.log('valueOf');
    return "1"; // 强制返回原始值
};
// 添加toString日志
Object.prototype.toString = function () {
    console.log('toString');
    return toString.call(this);
};
var a = {};
console.log(++a);
```

输出如下：

```
valueOf
2
```

#### 分析

1. valueOf返回原始值(字符串)，直接将该字符串转换为数字，得到1

### 对象转换为字符串

在预期会将对象用作字符串时，比如一个字符串拼接了字符串，传入了一个对象，此时会发生转换。

```javascript
// 保存原始的valueOf
var valueOf = Object.prototype.valueOf;
var toString = Object.prototype.toString;

// 添加valueOf日志
Object.prototype.valueOf = function () {
    console.log('valueOf');
    return valueOf.call(this);
};
// 添加toString日志
Object.prototype.toString = function () {
    console.log('toString');
    return toString.call(this);
};
var a = {};
alert(a);
```

输出如下：

```
toString
// 弹出[object Object]
```

#### 分析

1. 调用toString方法，返回了字符串"[object Object]"，对象最终转换为该字符串

#### 例子2

```javascript
// 保存原始的valueOf
var valueOf = Object.prototype.valueOf;
var toString = Object.prototype.toString;

// 添加valueOf日志
Object.prototype.valueOf = function () {
    console.log('valueOf');
    return valueOf.call(this);
};
// 添加toString日志
Object.prototype.toString = function () {
    console.log('toString');
    return this;
};
var a = {};
alert(a);
```

输出如下：

```
toString
valueOf
Uncaught TypeError: Cannot convert object to primitive value
    at 1.js:16
```

#### 分析

1. 调用toString方法，返回的不是原始值，继续执行
2. 调用valueOf方法，返回的不是原始值，继续执行
3. 抛出TypeError

##【番外】使用加号运算符连接字符串和对象时的处理

在测试对象到字符串转换时发现如下代码的表现和预期并不一致：

```javascript
// 保存原始的valueOf
var valueOf = Object.prototype.valueOf;
var toString = Object.prototype.toString;

// 添加valueOf日志
Object.prototype.valueOf = function () {
    console.log('valueOf');
    return valueOf.call(this);
};
// 添加toString日志
Object.prototype.toString = function () {
    console.log('toString');
    return toString.call(this);
};

console.log("a" + {});
```

输出如下：

```
valueOf
toString
a[object Object]
```

### 疑问

`"a"+ {}` 应该是预期把`{}`当做字符串使用，应该先调用toString方法的，实际情况却不是这样。

### 结论

通过查找资料得到的结论如下：

1. 如果有一个是对象，则遵循对象对原始值的转换过程(Date对象直接调用toString完成转换，其他对象通过valueOf转化，如果转换不成功则调用toString)
2. 如果两个都是对象，两个对象都遵循步骤1转换到字符串
3. 两个数字，进行算数运算
4. 两个字符串，直接拼接
5. 一个字符串一个数字，直接拼接为字符串

## 面试题

```javascript
var a = {};
var b = {};
var c = {};
c[a] = 1;
c[b] = 2;

console.log(c[a]);
console.log(c[b]);
```

### 题解

由于对象的key是字符串，所以`c[a]`和`c[b]`中的`a`和`b`会执行[对象到字符串]的转换。

根据转换规则, `a`和`b`都转换为了`[object Object]`，所以`c[a]`和`c[b]`操作的是同一个键。

答案是`输出两个2`，c对象的最终结构如下：

```javascript
{
  '[object Object]':2
}
```

![0.jpeg](https://static.ddhigh.com/blog/2019-10-15-093620.jpg)

![image-20210225113209566](https://static.ddhigh.com/blog/2021-02-25-113209-2.png)