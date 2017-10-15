---
title: 移动端rem和PSD单位换算问题
layout: post
categories:
- css3
tags:
- css3
- rem
---

设计图尺寸一般750宽度，而需要兼容640宽度手机的话，需要调整缩放比率，之前使用`写死viewport`的做法来实现，不过这个方法有点取巧，而且有些场景并不适用。
本文用`标准的@media`来实现

## rem定义
```css
@media screen and (max-width: 750px) {
  html {
    font-size: 30px;
  }
}

@media screen and (min-width: 640px) and (max-width: 749px) {
  html {
    font-size: 25px;
  }
}

@media screen and (min-width: 480px) and (max-width: 639px) {
  html {
    font-size: 20px;
  }
}

@media screen and (min-width: 320px) and (max-width: 479px) {
  html {
    font-size: 15px;
  }
}
```

## 如何使用
假设PSD中有个button的大小为`100px*40px`，那使用rem时CSS如下
```css
button {
    width: 3.333rem;
    height: 1.333rem;
}
```