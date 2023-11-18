---
slug: angularjs-concept to explain
title: Angularjs概念解释
date: 2015-04-06 17:48:32.000000000 +08:00
categories:
- Engineering
---
+ 本文所有内容仅代表个人观点

## ng
*Angularjs的简称。*
## 指令(Directive)
*特殊的html标签或html属性，扩展了html的功能*。有以下几类：
+ E    Element 元素 如 <dropdown /> 就是一个自定义指令（如何自定义指令，将在后面的文章中介绍），名称为"dropdown"。
+ A    Attribute 属性 如 <html ng-app="app"></html> 这是最常用的指令了，ng-app为指令名称，也是html元素的属性，app为该属性的值

## 作用域(scope)
*ng中变量、方法都是基于作用域的，作用类似于js作用域。*
## ng-bind
*html输出js变量，跟作用域绑定，message为作用域中的一个变量。*示例代码：

```html
<button ng-bind="message"></button>
```

最终会显示同一scope下的message变量值。

## ng-model
*双向绑定指令*，示例代码：

```html
<input type="text" ng-model="message"/>
```

表明将input的值与作用域中的message变量进行绑定，当input值改变的时候，变量message跟着改变，html中输出的内容也会同步改变。
