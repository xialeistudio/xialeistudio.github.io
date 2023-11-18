---
slug: javascript-event
title: Javascript事件系统
date: 2019-12-30 12:00:00
categories:
- Engineering
---

本文内容

+ 事件基础
+ 事件监听方式
+ 事件默认行为
+ 事件冒泡与事件捕获
+ 事件绑定与事件委托

## 事件基础

> 注意：本文不会深入探究Javascript的事件循环。

提到事件，相信每位Javascript开发者都不会陌生，由于Javascript是先有实现，后有规范，因此，对于大部分人来说，事件模块可以说是比较模糊的，本文将从不同角度帮助你理清楚事件模块。

事件的本质可以说是一个回调函数，当事件触发时会调用你的监听函数。

> 事件是一定会触发的，如果没有对应的监听函数，就不会执行回调。

比如下面就是用户点击指定元素打印日志的例子：

```javascript
document.querySelector('#button').onclick = function() {
	console.log('clicked');
};
```

事件基础相信大家都没什么问题，重点在后面的内容。

## 事件监听方式

由于历史原因，Javascript目前存在三种事件监听方式：

1. HTML代码中监听
2. DOM0级监听
3. DOM2级监听

Q: 为啥从DOM0级开始？

> 1998年，W3C综合各浏览器厂商的现有API，指定了DOM1标准。在DOM1标准出现之前浏览器已有的事件监听方式叫做DOM0级。

Q：DOM1级监听到哪里去了？

> 由于DOM1标准只是对DOM0标准的整理+规范化，并没有增加新的内容，因此DOM0级可以看做DOM1级。

### HTML代码监听

```html
<button onclick="alert('Hello World!')">点我</button>
```

直接将事件处理函数或事件处理代码写到HTML元素对应的属性上的方式就是**HTML代码监听方式**。

该方式有一个明显的缺点，如果事件逻辑比较复杂时，将大段代码直接写在HTML元素上不利于维护。因此一般会提取到一个专一的函数进行处理。

```html
<button onclick="callback()">点我</button>
```

该方式也有一个问题，那就是如果`callback()`函数还未加载好时点击按钮将报错。而且直接将事件耦合到HTML元素上也不符合单一职责，HTML元素应该只负责展示，不负责事件。

> 不建议在开发中使用该方式处理事件。

### DOM0级事件监听

在DOM1级规范出来之前，各浏览器厂商已经提供了一套事件API，也就是DOM0级API，它的写法如下：

```html
<button id="click">点我</button>
<script>
  document.querySelector('#click').onclick = function() {
    console.log('clicked');
  };
</script>
```

这个相信大家在刚开始入行时写的比较多，比如我们的ajax相关API就是DOM0级的。

```javascript
var xhr = new XMLHttpRequest();
xhr.onload = function() {};
xhr.onerror = function() {};
```

> DOM0级事件基本上都是以"on"开头的

DOM0级事件也存在一个问题，那就是不支持添加多个事件处理函数，因此只有在不支持DOM2级事件的情况下才会使用DOM0级来绑定事件。

### DOM2级事件监听

DOM2级事件是最新的事件处理程序规范（有许多年未更新了）。DOM2级事件通过`addEventListener`方式给元素添加事件处理程序。

```html
<button id="click">点我</button>
<script>
  document.addEventListener('click', function(){
    console.log('clicked');
  });
</script>
```

多次调用addEventListener可以绑定多个事件处理程序，但是需要注意：

> 同样的事件名、同样的事件处理函数和同样的事件流机制(冒泡和捕获，下面会讲到)，**只会触发一次**。

```html
// 下面的代码只会触发一次
<button id="request">登录</button>
<script>
function onClick() {
	console.log('clicked');
}
document.querySelector('#request').addEventListener('click', onClick, false);
document.querySelector('#request').addEventListener('click', onClick, false);
</script>
```

onClick是同一个事件处理程序，所以只触发一次

```javascript
// 下面的代码只会触发两次
<button id="request">登录</button>
<script>
document.querySelector('#request').addEventListener('click', function() {
	console.log('clicked');
}, false);
document.querySelector('#request').addEventListener('click', function() {
	console.log('clicked');
}, false);
</script>
```

两个匿名函数，所以会触发两次

## 事件默认行为

很多网页元素会有默认行为，比如下面这些：
+ 点击a标签的时候，会有跳转行为
+ 点击右键时会弹出菜单
+ 在表单中点击提交按钮会提交表单

如果我们需要阻止默认行为，比如我们在阻止表单的默认提交事件，进行数据校验，通过校验后再调用表单submit方法提交。

> 不同的监听方式阻止默认行为的方式也不同。

### HTML代码方式

> HTML代码方式支持return false和event.preventDefault()

#### return false方式

```html
<form action="" onsubmit="return handleSubmit()">
	<button type="submit">Submit</button>
</form>
<script>
function handleSubmit() {
	return false;
}
</script>
```

上例中我们监听了表单的`onsubmit`事件，当点击按钮或者按下回车时，将会触发`handleSubmit`方法，同时会阻止表单的提交。

> 表单内如果有type="submit"的按钮存在，按下回车时就会自动提交。

HTML监听方式阻止默认事件需要满足以下两点：

1. HTML事件监听代码`return handler()`，`return不能少`，少了就无法阻止默认行为
2. `handler()`函数需要返回`false`

#### event.preventDefault()

```html
<a href="https://www.ddhigh.com" onclick="handleClick(event)" id="click">Href</a>
<script>
function handleClick(e) {
	e.preventDefault();
}
</script>
```

### DOM0级事件方式

> DOM0级事件支持return false和event.preventDefault()两种方式。

#### event.preventDefault()

```html
// event.preventDefault()
<a href="https://www.ddhigh.com" id="click">Href</a>
<script>
	document.querySelector('#click').onclick= function (event) {
  	event.preventDefault();
  };
</script>
```

#### return false

```html
// return false
<a href="https://www.ddhigh.com" id="click">Href</a>
<script>
	document.querySelector('#click').onclick= function (event) {
  	return false;
  };
</script>
```

两种方式都能工作，不过建议使用`event.preventDefault()`，原因在下面DOM2级会讲到

### DOM2级事件

> DOM2级事件事件**只支持event.preventDefault()**方式，这也是事件的标准处理方法。

```html
<a href="https://www.ddhigh.com" id="click">Href</a>
<script>
document.querySelector('#click').addEventListener('click', function (e) {
	e.preventDefault();
});
</script>
```

## 事件冒泡与事件捕获

先来看一个HTML结构

```html
<div id="father">
  <div id="child">
    <div id="son">Click</div>
  </div>
</div>
```

我们知道，一旦绑定了事件处理程序，在事件触发时，事件处理函数都会触发。

如果我们给father/child/son都绑定了事件处理函数，点击了son时，谁被触发呢？

事实上，三个函数都会被触发，因为son时child的子元素，child又是father的子元素，点击son，同时也点击了father和child。

由此带来一个问题，三个函数谁先触发，谁后触发呢？这就是我们常说的事件流，father->child->son这种路径是可以的，但是son->child->father这种路径也是可以的。

针对这两种方式，W3C给了我们一个答案，两种方式都支持，即可以从父元素到子元素，又可以从子元素到父元素，前者叫**事件捕获**，后者叫**事件冒泡**。

### 事件捕获

事件发生时采取`自上而下`的方式进行触发，最先触发的是`window`，其次是`document`，然后根据DOM层级依次触发，最终进入到真正的事件元素。

> addEventListener第三个参数传入true就是捕获方式的标志。

```html
<div id="father">
	<div id="child">
  	<div id="son">Click</div>
    </div>
	</div>

  <script>
  document.querySelector('#father').addEventListener('click', function () {
  	console.log('father');
  }, true);
  document.querySelector('#child').addEventListener('click', function () {
  	console.log('child');
  }, true);
  document.querySelector('#son').addEventListener('click', function () {
  	console.log('son');
  }, true);
	</script>
```

点击son之后的输出顺序为

```
father
child
son
```

### 事件冒泡

事件发生时采取`自下而上`的方式进行触发，最先触发的是发生事件的元素，其次是父元素，依次向上，最终触发到`document`和`window`。

> addEventListener第三个参数传入false就是捕获冒泡的标志。

```html
<div id="father">
	<div id="child">
  	<div id="son">Click</div>
    </div>
	</div>

  <script>
  document.querySelector('#father').addEventListener('click', function () {
  	console.log('father');
  }, false);
  document.querySelector('#child').addEventListener('click', function () {
  	console.log('child');
  }, false);
  document.querySelector('#son').addEventListener('click', function () {
  	console.log('son');
  }, false);
	</script>
```

点击son之后的输出顺序为

```
son
child
father
```

> 由于事件捕获和事件冒泡机制，我们需要一个标记来标识真正触发事件的元素，这个元素就是event.target，而另外一个相似的属性叫event.currentTarget，这是当前元素。

### 事件捕获和时间冒泡的顺序

> 根据浏览器规范，事件捕获会先于事件冒泡发生。因此，总的事件顺序如下

1. window 捕获阶段
2. document 捕获阶段
3. ... 依次到真正触发事件的元素 捕获阶段
4. 真正触发事件的元素 冒泡阶段
5. 依次向上的父元素 冒泡阶段
6. document  冒泡阶段
7. window 冒泡阶段

```html
<div id="father">
        <div id="child">
            <div id="son">Click</div>
        </div>
    </div>

    <script>
        document.querySelector('#father').addEventListener('click', function () {
            console.log('father捕获');
        }, true);
        document.querySelector('#child').addEventListener('click', function () {
            console.log('child捕获');
        }, true);
        document.querySelector('#son').addEventListener('click', function () {
            console.log('son捕获');
        }, true);
        document.querySelector('#father').addEventListener('click', function () {
            console.log('father冒泡');
        }, false);
        document.querySelector('#child').addEventListener('click', function () {
            console.log('child冒泡');
        }, false);
        document.querySelector('#son').addEventListener('click', function () {
            console.log('son冒泡');
        }, false);
    </script>
```

点击son之后的输出为

```
father捕获
child捕获
son捕获
son冒泡
child冒泡
father冒泡
```

## 事件绑定和事件委托

弄明白浏览器的事件流机制之后，来讨论事件绑定和事件委托其实是很简单的事情。

### 事件绑定

就是在事件监听方式中直接对具体元素进行事件监听的方式。有个明显的缺点，对于新增加的DOM节点是无法监听到事件的。

```html
    <div class="a">click1</div>
    <div class="a">click2</div>
    <script>
        document.querySelectorAll('.a').forEach(ele => ele.onclick = function () {
            console.log('clicked ' + this.innerHTML);
        });
        setTimeout(function () {
            const div3 = document.createElement('div')
            div3.className = "a";
            div3.innerHTML = "click3"
            document.body.appendChild(div3)
        }, 500);
    </script>
```

上面的click3点击是没有任何反应的，因为在创建该元素时没有绑定事件处理函数。

### 事件委托

我们利用事件流机制来实现上面的需求。

> 事件委托就是利用事件流机制，在父元素进行监听，由于事件冒泡机制，父元素可以接受新添加元素的事件。

```html
    <div class="a">click1</div>
    <div class="a">click2</div>
    <script>
        document.body.addEventListener('click', function (e) {
            console.log(e.target.innerHTML)
        }, false);
        setTimeout(function () {
            const div3 = document.createElement('div')
            div3.className = "a";
            div3.innerHTML = "click3"
            document.body.appendChild(div3)
        }, 500);
    </script>
```

由于事件冒泡机制，click3元素点击之后会将事件冒泡给父元素，也就是我们的document.body，通过event.target可以拿到真正触发事件的元素。

（完）

![0.jpeg](https://static.ddhigh.com/blog/2019-10-22-102654.jpg)