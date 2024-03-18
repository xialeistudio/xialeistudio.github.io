---
slug: permissionscope-with-swift-4
title: PermissionScope Swift4 兼容问题
date: 2018-06-14 21:41:15
categories:
- Engineering
tags:
- swift
---

[PermissionScope](https://github.com/nickoneill/PermissionScope)是iOS非常好用的权限处理库，界面效果也非常精美。不幸的是作者已经停止维护。

> PermissionScope is no longer supported. Please use an alternative if you need updates for newer iOS 10 and 11 APIs!

## 问题的来源

因为作者是基于Swift3开发的，而4.0的`@selector`语法有一点调整，所以是不能通过编译的，处理办法是根据Xcode的提示一个个修正。

可是事情真的这么简单吗？Xcode处理过后虽然编译通过了，但是会触发运行时错误。错误内容大致是`调用了不存在的方法`。

## 解决方案

由于我们根据Xcode的提示给相关代码加了`@objc`，但是有些方法是没有加的，而这些方法类似下面的代码：

```swift
func requestCamera() {

}
```

由于没有`@objc`修饰，`@selector`指令找不到方法，所以就报错了。解决方案如下：

```swift
@objc
func requestCamera() {

}
```