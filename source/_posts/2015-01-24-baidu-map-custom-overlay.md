---
layout: post
title: 百度地图添加自定义标注
date: 2015-01-24 14:09:36.000000000 +08:00
type: post
published: true
status: publish
categories:
- frontend
tags:
- baidu map
- overlay
meta:
  _edit_last: '1'
  _thumbnail_id: '355'
  views: '1433'
  _wp_old_slug: "%e7%99%be%e5%ba%a6%e5%9c%b0%e5%9b%be%e6%b7%bb%e5%8a%a0%e8%87%aa%e5%ae%9a%e4%b9%89%e6%a0%87%e6%b3%a8"
---
百度地图的默认标注是一个 红色 的地标，如果要做互动性强的地图应用，几乎没提供什么额外信息，本文教大家怎么添加自定义标注，如添加头像。
## JS代码

```javascript
var icon = new BMap.Icon('头像URL地址', new BMap.Size(33, 33), {
    offset: new BMap.Size(10, 25),
    imageOffset: new BMap.Size(0, 0)
});
markers[i] = new BMap.Marker(new BMap.Point([经度], [纬度]), {
    icon: icon
});
map.addOverlay(markers[i]);
```

由于百度地图的限制，我们不能获取标注的HTML，只能采取“特别”的方式对头像增加样式，比如圆角，边框等等。

```javascript
var avatarRadiusCompleted = false;
var avatarRadius = setInterval(function() {
    avatarRadius && clearInterval(avatarRadius);
    $('#map').find('img').each(function() {
        var src = $(this).attr('src');
        if (src.indexOf('map') == -1) {
            $(this).addClass('xl-map-avatar'); //.xl-map-avatar 为自定义的CSS
        }
    });
    avatarRadiusCompleted = true;
},
100);
```

## CSS代码

```css
.xl-map-avatar {
	width: 32px;
	height: 32px;
	border: 1px solid white !important;
	border-top-left-radius: 999px; /* 左上角 */
	border-top-right-radius: 999px; /* 右上角 */
	border-bottom-right-radius: 999px; /* 右下角 */
	border-bottom-left-radius: 999px; /* 左下角 */
	border-radius: 50%;
	background-color: #ccc;
	background-clip: padding-box;
}
```

## 效果图
![效果图](https://og5r5kasb.qnssl.com/wp-content/uploads/2015/01/QQ%E6%88%AA%E5%9B%BE20150124140833.png)