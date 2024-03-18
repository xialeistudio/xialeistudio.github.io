---
slug: css3-loading
title: css3打造炫酷loading
date: 2015-01-20 22:38:35.000000000 +08:00
categories:
- Engineering
---
css3的优点就不多说了，一个很重要的，节约了带宽，以往需要使用图片的地方很多时候都可以使用CSS3来实现。 本文将带来一个利用CSS3制作loading的教程，这里直接上代码了。

## CSS代码

```css
@keyframes spin {
	0% {
		transform: rotate(0deg);
		-webkit-transform: rotate(0deg);
	}

	100% {
		transform: rotate(360deg);
		-webkit-transform: rotate(360deg);
	}
}

@-webkit-keyframes spin {
	0% {
		transform: rotate(0deg);
		-webkit-transform: rotate(0deg);
	}

	100% {
		transform: rotate(360deg);
		-webkit-transform: rotate(360deg);
	}
}

@keyframes spinoff {
	0% {
		transform: rotate(0deg);
		-webkit-transform: rotate(0deg);
	}

	100% {
		transform: rotate(-360deg);
		-webkit-transform: rotate(-360deg);
	}
}

@-webkit-keyframes spinoff {
	0% {
		transform: rotate(0deg);
		-webkit-transform: rotate(0deg);
	}

	100% {
		transform: rotate(-360deg);
		-webkit-transform: rotate(-360deg);
	}
}

body {
	margin: 0;
}

.content {
	width: 100px;
	height: 100px;
	position: relative;
	margin: 10% auto 0 auto;
}

.content .ball {
	top: 25px;
	left: 25px;
	width: 50px;
	height: 50px;
	position: absolute;
	border-radius: 50px;
	-webkit-border-radius: 50px;
	border: 5px solid rgba(40,40,200,0.5);
	border-left: 5px solid rgba(255,255,255,0.7);
	border-top: 5px solid rgba(255,255,255,0.7);
	box-shadow: 2px 2px 4px 0 rgba(40,40,200,0.4);
	animation: spin .5s linear infinite;
	-webkit-animation: spin .5s linear infinite;
}

.content .ball1 {
	top: 35px;
	left: 35px;
	width: 30px;
	height: 30px;
	position: absolute;
	border-radius: 30px;
	-webkit-border-radius: 30px;
	border: 5px solid rgba(40,40,200,0.8);
	border-left: 5px solid rgba(255,255,255,1.0);
	border-top: 5px solid rgba(255,255,255,1.0);
	box-shadow: 2px 2px 4px 0 rgba(40,40,200,0.4);
	animation: spinoff .5s linear infinite;
	-webkit-animation: spinoff .5s linear infinite;
}
```

## HTML代码

```html
<div class="content">
    <div class="ball"></div>
    <div class="ball1"></div>
</div>
```

## 总结

实现动画有几个关键点：
+ css3 keyframes
+ css position
+ css border

基本就以上问题，代码可以直接新建一个页面，复制打开即可运行