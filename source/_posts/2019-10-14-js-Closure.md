---
title: 搞懂JS闭包
date: 2019-10-14 12:00:00
categories:
- frontend
- javascript
---

闭包(Closure)是JS比较难懂的一个东西，或者说别人说的难以理解， 本文将以简洁的语言+面试题来深入浅出地介绍一下。

## 作用域和作用域链

在将闭包之前，需要先讲一下作用域。

JS中有全局作用域和局部作用域两种。

全局作用域任何地方都能访问，而局部作用于只有内部能访问。

```javascript
function a() {
  var num = 1;
}
console.log(num);
```

在上面的例子中会报错，num不存在。

> 总结：函数外部无法访问函数内部的值

当代码在一个作用域中执行时，JS引擎会默认创建一个作用域链(从当前作用域一直链接到全局作用域)。

在访问变量或者函数时，如果当前作用域查找不到，则向上级作用域查找，找到就返回，如果查找到全局作用域还没找到的话就报错。

```javascript
function a() {
  var num = 1;
  function b() {
    console.log(num);
  }
}
```

在上面的例子中，num是在`a`函数作用域下的局部变量，我们在`b`函数访问num时会有以下过程：

1. 在`b`的作用域查找num，发现找不到
2. 往上一级作用域查找，发现num在`a`作用域，查找成功

> 总结：函数可以访问同级或上级作用域的值

## 闭包

当我们需要在函数外部访问函数内部的值时，闭包就产生了。

```javascript
function a() {
  var num = 1;
  function b () {
    console.log(num);
  }
  return b;
}
var bb = a();
bb(); // 1
```

> 在函数`a`的内部声明一个函数`b`，然后把`return b`，这个时候的`b()`函数就可以在外部访问，最终能够访问到num。

简单来说：

> 闭包就是函数内部的函数，上面的那个b就是闭包，可以在外面访问到内部的num

## 面试题

```javascript
// 每隔1秒输出0-10的数字
for(var i = 0;i<10;i++) {
  setTimeout(function() {
    console.log(i);
  },1000);
}
// 上面这段代码输出什么?如果需要修改为正确的情况，怎么修改？
```

> 1秒后输出10，因为setTimeout是到下一轮tick中执行，而for循环在当前这轮循环完毕后i的值已经是最后一个值了。需要使用闭包来保留现场

```javascript
for (var i = 0; i < 10; i++) {
    (function (i) {
        setTimeout(function () {
            console.log(i);
        }, 1000);
    }(i))
}
```

这样就是正常的输出了。

```javascript
var name = "Window";

var object = {
    name: "Object",

    f: function () {
        return function () {
            return this.name;
        };

    }

};

alert(object.f()());
```

答案是Window。

> `object.getNameFunc()()`可以分开两部分来看。
>
> 1. object.f()得到了一个这样的函数
>
> ```javascript
> function() {
>   return this.name
> }
> ```
> 2. `object.f()()`相当于执行上面那个函数，也就是`普通函数调用方式`，this指向`全局环境`，this指向搞不清楚的同学可以看看我之前发的[Javavscript基础——this指向](https://www.ddhigh.com/2019/09/27/javascript-this.html)
> 3. 所以this.name也就是`var name = "Window"`

还是那道题，不过我们把this保存一下，变成下面这种形式

```javascript
var name = "Window";

var object = {
    name: "Object",

    f: function () {
        var that = this;
        return function () {
            return that.name;
        };

    }

};

alert(object.f()());
```

答案是Object。

> 1. object.f()中调用时这个this指向object，当用变量保存时，这个that相当于object
> 2. object.f()()调用时，由于that相当于object，所以that.name就是object中的Object

## 总结

1. 闭包可以在外部访问函数内部的变量
2. 闭包可以保留现场

## 结尾

来道面试题给大家看看吧

```javascript
const buttons = document.querySelectorAll('.btn');
for(var i = 0; i < buttons.length; i++) {
  buttons[i].onclick = function() {
    console.log(i);
  }
}
```

以上例子显示什么?如果需要正常显示需要怎么修改?

![0.jpeg](https://static.ddhigh.com/blog/2019-10-14-103646.jpg)