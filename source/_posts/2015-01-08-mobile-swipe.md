---
layout: post
title: 移动端滑动的实现
date: 2015-01-08 17:38:08.000000000 +08:00
type: post
published: true
status: publish
categories:
- engineering
---


如果想在移动端判断用户的是否滑动以及滑动方向时，可以不使用第三方库，直接用touch事件处理即可，没必要增加不必要的代码，减轻移动端网络压力。



## 重点

移动端的touch事件有三个: touchstart、touchmove、touchend 分别代表 触摸开始，触摸移动，触摸结束

```javascript
var _begin;
var _end;
document.querySelector('#target').addEventListener('touchstart', function(e) {
	_begin = e.changedTouches[0].pageX;
}, false);
document.querySelector('#target').addEventListener('touchend', function(e) {
	_end = e.changedTouches[0].pageX;
	if (_end > _begin) {
		console.log('从左向右')
	}else{
		console.log('从右向左')
	}
}, false);
```