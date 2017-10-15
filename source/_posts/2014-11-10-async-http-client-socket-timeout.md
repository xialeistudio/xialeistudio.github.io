---
layout: post
title: async http client socket超时问题
date: 2014-11-10 13:47:50.000000000 +08:00
type: post
published: true
status: publish
categories:
- android
tags:
- android
meta:
  _edit_last: '1'
  _thumbnail_id: '241'
  views: '1700'
  _wp_old_slug: async-http-client-socket%e8%b6%85%e6%97%b6%e9%97%ae%e9%a2%98
---
最近做的一个项目的HTTP模块使用了loopj的asynchttpclient ([https://github.com/loopj/android-async-http](https://github.com/loopj/android-async-http)）。

自动更新模块总是出现sockettimeout的exception,查来查去也不知道什么问题，为此还换了asynchttpclient的库版本。但是问题也没解决。

仔细看了一下，提示的是timeout，应该从这方面去看看，后面看到自己的HTTP工具类设置了全局超时时间为5000ms,普通请求当然没这么久，但是自动更新是下载，肯定不止5秒的，删掉超时设置就可以了。