---
title: 无需编程导出微信表情包
date: 2019-01-11 10:53:02
categories:
- Engineering
---

微信前两天推送了年度报告，其中的表情统计很有意思，的确，表情包这两年是越来越火了。但是有个问题是微信不支持导出表情包，有的小伙伴又需要导出来保存到其他地方。

本文分享一个比较简单的方式导出表情包，条件只有一个：谷歌浏览器。

1. 打开 https://wx.qq.com 并登陆，这是网页版微信登录入口
2. 手机选择表情发送给文件传输助手
3. 打开网页版微信，可以查看到图片
![1](http://download.ddhigh.com/blog-img/WX20190111-105910.png)
4. 接下来打开谷歌浏览器的开发者工具（不同电脑不太一样，但是都是右上角打开）
![2](http://download.ddhigh.com/blog-img/WX20190111-110041.png)
5. 然后按照图片顺序点击如下图所示的图标
![3](http://download.ddhigh.com/blog-img/WX20190111-110109.png)
6. 这时候鼠标处于选择元素的状态，直接悬浮在表情图片上即可
![4](http://download.ddhigh.com/blog-img/WX20190111-110127.png)
7. 下方的窗口会出现图片链接，而且会有背景色（本图片的背景色是淡蓝色）
![5](http://download.ddhigh.com/blog-img/WX20190111-110127.png)
8. 鼠标悬浮到刚才的淡蓝色窗口的链接上面，会出现表情的原图
![6](http://download.ddhigh.com/blog-img/WX20190111-110137.png)
8. 在链接上面点击右键，选择如图名字的菜单（菜单顺序不同系统不同）
![7](http://download.ddhigh.com/blog-img/WX20190111-110148.png)
9. 在新窗口打开的图片就是表情原始图片了，可以保存
![8](http://download.ddhigh.com/blog-img/WX20190111-110159.png)