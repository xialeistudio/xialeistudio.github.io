---
layout: post
title: 移动端textarea自适应高度
date: 2014-10-21 14:21:08.000000000 +08:00
type: post
published: true
status: publish
categories:
- javascript
tags:
- mobile
meta:
  _edit_last: '1'
  views: '2143'
  _thumbnail_id: '177'
  _wp_old_slug: "%e7%a7%bb%e5%8a%a8%e7%ab%aftextarea%e6%a0%b9%e6%8d%ae%e5%86%85%e5%ae%b9%e8%87%aa%e5%8a%a8%e5%a2%9e%e5%8a%a0%e9%ab%98%e5%ba%a6"
---
PC端网页的textarea内容多了会出现滚动条，这个没什么，鼠标么，滚动方便。但是移动端是没鼠标的，出现滚动条是很不友好的行为。

利用js的事件绑定及动态改变CSS就可以做到这个了。

```javascript
onpropertychange="this.style.height=this.scrollHeight + 'px'" oninput="this.style.height=this.scrollHeight + 'px'"
```