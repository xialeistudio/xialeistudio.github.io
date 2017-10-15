---
layout: post
title: 移动端实时检测输入框
date: 2014-10-14 14:15:21.000000000 +08:00
type: post
published: true
status: publish
categories:
- javascript
tags:
- mobile
meta:
  _edit_last: '1'
  views: '1684'
  _thumbnail_id: '178'
  _wp_old_slug: "%e7%a7%bb%e5%8a%a8%e7%ab%af%e5%ae%9e%e6%97%b6%e6%a3%80%e6%b5%8b%e8%be%93%e5%85%a5%e6%a1%86"
---
PC浏览器的话由于有blur和focus事件，可以在失去焦点时进行一次验证，但是移动端有点麻烦，点击其他地方才可以，这种的话体验不是很好。
利用input事件可以解决这个问题。

```javascript
$(document).on('input','#username',function(){
    //验证逻辑
});
```

测试之后问题确实来了，每输入一个字符就会触发，浪费很多网络请求，接下来使用一个定时器的技术来进行处理。

```javascript
var timer;
$(document).on('input','#username',function(){
    timer && clearTimeout(timer);
    timer = setTimeout(function(){
   
    //验证逻辑
    },500);//延时0.5s触发
});
```

采用这种定时器技术可以在请求次数和用户体验之间取得平衡，很多地方都可以使用这种技术来实现。