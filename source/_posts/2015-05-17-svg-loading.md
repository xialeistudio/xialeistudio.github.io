---
title: svg制作loading
date: 2015-05-17 05:58:35
categories:
- engineering
---
还在使用gif做loading效果吗？你确实out了，再不济也得用css3动画是不是--。无奈，css3旋转动画需要一张png图片来做，也没什么问题，现在，有更炫酷的方案了。   
没错!就是SVG。svg其实不是什么新东西。SVG 于 2003 年 1 月 14 日成为 W3C 推荐标准。现在浏览器越来越强大，所以，尽情使用吧！   

## 代码

```xml
<div style="width: 200px;height: 200px;background: #000000">
  <svg width="100%" height="100%" version="1.1" xmlns="http://www.w3.org/2000/svg">
    <g>
      <circle cx="100" cy="100" r="50" fill="none" stroke-width="2" stroke="rgba(255,255,255,0.2)"/>
      <path d="M100 50 A50 50 0 0 1 150 100 " style="stroke: rgba(255,255,255,.7);stroke-width: 2"/>
      <animateTransform 
        attributeName="transform" 
        fill="freeze" 
        attributeType="XML" 
        type="rotate" 
        from="0,100,100" 
        to="360,100,100" 
        dur="1s" 
        repeatCount="indefinite"
      />
    </g>
  </svg>
</div>
```

## 效果

<div style="width: 200px;height: 200px;background: #000000">
  <svg width="100%" height="100%" version="1.1" xmlns="http://www.w3.org/2000/svg">
    <g>
      <circle cx="100" cy="100" r="50" fill="none" stroke-width="2" stroke="rgba(255,255,255,0.2)"/>
      <path d="M100 50 A50 50 0 0 1 150 100 " style="stroke: rgba(255,255,255,.7);stroke-width: 2"/>
      <animateTransform attributeName="transform" fill="freeze" attributeType="XML" type="rotate" from="0,100,100" to="360,100,100" dur="1s" repeatCount="indefinite"/>
    </g>
  </svg>
</div>