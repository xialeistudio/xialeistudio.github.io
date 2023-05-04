---
layout: post
title: php实现扫描二维码登录网站
date: 2015-09-17 09:51:45.000000000 +08:00
type: post
published: true
status: publish
categories:
- engineering
---
扫描二维码登录对于现在的web应用来说，确实是个很炫酷的功能，安全性也可以保障，不少朋友可能觉得这是个很复杂的工作，其实不然，真正说来只有几个步骤而已。
## 原理
1. PC浏览器展示一张二维码图片，该图片二维码值为一段绝对地址的url，大致如下：http://www.example.com/oauth/qrcode?key=key
2. PC浏览器定期轮询 http://www.example.com/oauth/query，可能有的同学会问，怎么不用带上key？这里我们用session来保存key，所以链接中不用带上key，将这个key作为服务端的缓存key且值为空，如果该缓存值为空，证明没被扫描，继续轮询，如果已经被扫描，展示扫描结果。
3. 手机微信扫描之后会直接访问http://www.example.com/oauth/qrcode?key=key，这里我们先把这个key保存的session中（这个session和2中的不同，一个是PC，一个是手机）。然后检测用户在手机端是否登录，如果已登录，则把用户信息存到2中的key缓存中，这时候前端查询的时候就会有值了。如果用户在手机未登录，则直接跳转微信登录，登陆成功之后再将用户信息设置到2中的key缓存

## demo
[http://www.lizhiclub.com/](http://www.lizhiclub.com/)