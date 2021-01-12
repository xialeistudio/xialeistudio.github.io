---
layout: post
title: js在线调试工具
date: 2016-06-12 09:34:14.000000000 +08:00
type: post
published: true
status: publish
categories:
- frontend
- javascript
---
在进行微信开发的时候，由于JS SDK提供的api需要在真机调试，而手机端的console方法虽然存在，但是调用结果却看不到。所以笔者使用socket.io重写了一个在线版本的调试工具。

[工具地址](http://jsconsole.org/)

## 使用方法
+ 打开 http://jsconsole.duapp.com?token=【您的标识符】 请确保标识符全局唯一，否则其他人可能会看到你的调试信息哟！   
+ 在需要调试的页面引入以下js:   

```html
<script src="http://jsconsole.duapp.com/dist/chat.bundle.js"></script>
<script src="http://jsconsole.duapp.com/dist/client.js?token=【您的标识符】"></script>
```

+ 开始调试！