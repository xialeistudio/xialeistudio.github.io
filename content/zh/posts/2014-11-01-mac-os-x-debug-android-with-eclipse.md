---
slug: mac-os-x-debug-android-with-eclipse
title: mac os x 使用eclipse调试android
date: 2014-11-01 21:07:10.000000000 +08:00
categories:
- Engineering
---
这两天心血来潮装了个mac os x 10.10系统，折腾的过程就不说了。   
Mac OS X 10.10的环境下，Eclipse+ADT，进行真机调试时，会出现一个问题。   
终端下输入 adb devices可以看到小米2S，但是Device Chooser对话框里不显示真机设备，只有重新插拔数据线才可以。   
仔细看了下android run configure发现一个问题，默认显示的**compatible devices**（意思差不多是适配的设备）。   
简单说下方法   
右键项目>run as>run configurations>target>选中间那个>Active Devices
![示意图](https://og5r5kasb.qnssl.com/wp-content/uploads/2014/11/%E5%B1%8F%E5%B9%95%E5%BF%AB%E7%85%A7-2014-11-01-%E4%B8%8B%E5%8D%889.05.42.jpg)   
再次点击run就可以了。