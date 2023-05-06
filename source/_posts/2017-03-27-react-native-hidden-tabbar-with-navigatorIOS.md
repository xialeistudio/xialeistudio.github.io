---
title: ReactNative在NavigatorIOS中隐藏TabBar
layout: post
categories:
- Engineering
tag:
- react-native
---
ReactNative常用的一种布局是TabBar+Navigator布局，底部几个固定的标签，顶部有个导航栏，如果进入子页面的话，底部TabBar是需要隐藏起来的。

不过官方没有提供这个属性，github和StackOverflow上的答案有个bug，平时没什么问题，如果手指左滑一点然后松开，这时候路由没切换，但是TarBar会显示，然后不消失。

目前能够完美解决这个问题的方案如下：
1. 找到React/RCTWrapperViewController.m
2. 查找 ***willShowViewController***
3. 在该方法最开始的地方加入`self.navigationController.tabBarController.tabBar.hidden=self.navigationController.childViewControllers.count>1;`
