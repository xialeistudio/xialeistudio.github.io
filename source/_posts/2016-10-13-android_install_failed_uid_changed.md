---
layout: post
title: 解决shareUserId导致的app无法升级的问题
date: 2016-10-13 18:40:30.000000000 +08:00
type: post
published: true
status: publish
categories:
- android
tags:
- android
- INSTALL_FAILED_UID_CHANGED
meta:
  _edit_last: '1'
  _wp_old_slug: "%e4%b8%80%e6%ac%a1android%e5%ba%94%e7%94%a8%e5%8d%87%e7%ba%a7%e5%ae%89%e8%a3%85%e5%a4%b1%e8%b4%a5%e7%9a%84%e8%a7%a3%e5%86%b3%e8%bf%87%e7%a8%8b"
  views: '174'
---
老版本app版本号是2.0.13，Build是20160719。新版本app版本号是2.0.14，Build是2016101301。   
初略看来应该是可以覆盖升级的，但是安装新版本的时候提示“应用未安装”。   
网上找了一下，大致原因有以下几种：
+ 签名冲突
+ 手机空间不足
+ 当前版本号小于已安装版本号

解决方案都是让用户卸载老版本，然后安装新版本，但是这肯定是可以安装的（测试通过）。      
为了找出不能覆盖安装的问题，笔者还是将USB调试模式打开，直接使用IDE安装新版本app。   
安装的时候提示**INSTALL_FAILED_UID_CHANGED**，从字面意思来看感觉是用户问题，定义app用户相关的代码只有AndroidManifest.xml文件中有。   
打开AndroidManifest.xml发现定义了**shareUserId**，而老版本app是没有定义该属性的，删除之后，问题解决。