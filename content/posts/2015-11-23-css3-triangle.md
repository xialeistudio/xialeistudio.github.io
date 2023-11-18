---
slug: css3-triangle
title: css3实现三角形
date: 2015-11-23 15:37:09.000000000 +08:00
categories:
- Engineering
---

```css
div{
    border: 1px solid #dddddd;
    padding: 4px 40px 4px 8px;
    position: relative;
}
div:after{
    content: ' ';
    margin-top: -5px;
    display: block;
    position: absolute;
    right: 8px;
    top: 50%;
    width: 0;
    height: 0;
    border-left: 12px transparent solid;
    border-right: 12px transparent solid;
    border-top: 12px #000000 solid;
}
```

[demo](http://ngdemo.sinaapp.com/#demo12)
