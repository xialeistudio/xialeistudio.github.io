---
slug: css-center
title: css水平居中和垂直居中
date: 2014-12-16 18:04:32.000000000 +08:00
categories:
- Engineering
---
水平居中还是比较好弄的

```css
{
    margin-left: auto;
    margin-right: auto;
}
```

但是垂直居中就比较麻烦，网上一大推文章都是什么display:table-cell,根本不管用。这里利用position属性可以达到这个目的。
## 效果图
![效果图](https://og5r5kasb.qnssl.com/wp-content/uploads/2014/12/16541418724107.png)
## HTML代码

```html
<html>
 <head></head>
 <body> 
  <div class="container"> 
   <div class="inner"></div> 
  </div> 
 </body>
</html>
```

## CSS代码

```css
body{
 background: #f1f1f1;
}
.container{
 width: 400px;
 height: 400px;
 position: relative;
 margin: 100px auto;
 background: white;
}
.container .inner{
 width: 100px;
 height: 100px;
 background: black;
 position: absolute;
 left: 50%;
 margin-left: -50px;
 top: 50%;
 margin-top: -50px;
}
```

## 关键点
top属性和margin-top的组合，一般来说 top: 50%之后，加一个 margin-top: 容器的高度/2 就可以垂直居中了。