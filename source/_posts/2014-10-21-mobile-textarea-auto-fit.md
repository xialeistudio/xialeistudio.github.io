---
layout: post
title: 移动端textarea自适应高度
date: 2014-10-21 14:21:08.000000000 +08:00
type: post
published: true
status: publish
categories:
- engineering
---
PC端网页的textarea内容多了会出现滚动条，这个没什么，鼠标么，滚动方便。但是移动端是没鼠标的，出现滚动条是很不友好的行为。

利用js的事件绑定及动态改变CSS就可以做到这个了。

```javascript
onpropertychange="this.style.height=this.scrollHeight + 'px'" oninput="this.style.height=this.scrollHeight + 'px'"
```