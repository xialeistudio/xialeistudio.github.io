---
layout: post
title: 移动端滑动的实现
date: 2015-01-08 17:38:08.000000000 +08:00
type: post
published: true
status: publish
categories:
- javascript
tags:
- mobile
- swipe
- touch
meta:
  _edit_last: '1'
  _thumbnail_id: '179'
  views: '3469'
  _wp_old_slug: "%e7%a7%bb%e5%8a%a8%e7%ab%af%e5%88%a9%e7%94%a8touch%e4%ba%8b%e4%bb%b6%e5%ae%9e%e7%8e%b0%e5%b7%a6%e6%bb%91%e5%8f%b3%e6%bb%91"
---
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