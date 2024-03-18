---
slug: ios9-navigation-bar-transparent
title: ios9 导航栏全透明
date: 2015-12-12 16:59:32.000000000 +08:00
categories:
- Engineering
---

## 效果图
![效果图](https://og5r5kasb.qnssl.com/wp-content/uploads/2015/12/1.pic_.jpg)   
导航栏是全透明的，但是导航栏的 item 还是正常的。

```
[self.navigationBar setBackgroundImage:[UIImage new] forBarMetrics:UIBarMetricsDefault];
self.navigationBar.shadowImage = [UIImage new];
self.navigationBar.translucent = YES;
```
如果你的当前**viewController**不是**navigationController**navigationController，请把**self.navigationBar**改为**self.navigationController.navigationBar**。