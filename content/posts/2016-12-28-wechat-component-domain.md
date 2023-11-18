---
slug: wechat-component-domain
date: 2016-12-28
title: 微信开放平台公众号第三方平台网页开发域名问题
categories:
- Engineering
---
先来看一下微信官方定义:

*第三方平台在代公众号做网页授权、调用JS SDK等网页开发工作时所用的域名，可填写3个，以;隔开。为了满足开发者管理需要，符合以下要求的下级域名也将生效：$APPID$.wx.abc.com（$APPID$为公众号的AppID的替换符）*

只能说微信文档这个 **wx.abc.com**误导了我好久，试过的域名是**APPID.wx.abc.com**，死活不行，后来发现公司域名整个就是用**wx.abc.com**替换，不是**abc.com**，所以最终进行授权的域名域名是(假设appid为**testappid**，填写的网页开发域名为**example.com**):**testappid.example.com**，可以根据这个做泛域名解析。