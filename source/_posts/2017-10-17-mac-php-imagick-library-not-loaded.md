---
title: mac下php-imagick扩展library not loaded问题
date: 2017-10-17 17:26:30
tags:
---
最近在使用imagick开发图像合成功能，和往常一样，终端执行

```
brew install php71-imagick
```

虽然homebrew提示我安装成功了，然而`php -m`的时候确提示**php-imagick模块无法加载**。

google发现很多使用homebrew的人都遇到了问题，解决方法是**使用源码编译imagick**扩展，当然有个Homebrew倒是不用自己输入很长串的编译命令。

终端执行

```
brew reinstall -s php71-imagick
```

**-s**代表源码编译。