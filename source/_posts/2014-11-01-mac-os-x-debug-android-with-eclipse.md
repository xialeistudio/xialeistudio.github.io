---
layout: post
title: mac os x 使用eclipse调试android
date: 2014-11-01 21:07:10.000000000 +08:00
type: post
published: true
status: publish
categories:
- android
tags:
- debug
- eclipse
- mac
meta:
  _edit_last: '1'
  _thumbnail_id: '221'
  views: '1734'
  _wp_old_slug: mac-os-x-10-10-adb-%e5%8f%af%e4%bb%a5%e5%8f%91%e7%8e%b0%e8%ae%be%e5%a4%87%e4%bd%86%e6%98%afeclispe%e4%b8%8d%e8%83%bd%e8%b0%83%e8%af%95%e7%9a%84%e8%a7%a3%e5%86%b3%e6%96%b9%e6%b3%95
---
这两天心血来潮装了个mac os x 10.10系统，折腾的过程就不说了。   
Mac OS X 10.10的环境下，Eclipse+ADT，进行真机调试时，会出现一个问题。   
终端下输入 adb devices可以看到小米2S，但是Device Chooser对话框里不显示真机设备，只有重新插拔数据线才可以。   
仔细看了下android run configure发现一个问题，默认显示的**compatible devices**（意思差不多是适配的设备）。   
简单说下方法   
右键项目>run as>run configurations>target>选中间那个>Active Devices
![示意图](https://og5r5kasb.qnssl.com/wp-content/uploads/2014/11/%E5%B1%8F%E5%B9%95%E5%BF%AB%E7%85%A7-2014-11-01-%E4%B8%8B%E5%8D%889.05.42.jpg)   
再次点击run就可以了。