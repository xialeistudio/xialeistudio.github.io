---
layout: post
title: highchats曲线不显示
date: 2014-09-25 00:24:00.000000000 +08:00
type: post
published: true
status: publish
categories:
- Engineering
---
highchats是什么就不介绍了。一个JS绘图工具库，基于JQ，使用简单方便，但是不注意的话会坑人。

今天兴致满满的去绘图，后端数据也返回了。可是一个纠结的问题困扰了我一下午！

后端数据返回的JSON是

```json
["0","0","0"]
```

这种形式，JSON.parse解析之后返回的是一个字符数组，而不是数字数组，解决方案是利用JS做一次类型转换

```javascript
for(var i in data){
    data[i]=parseInt(data[i]);
}
```
for(var i in data){
    data[i]=parseInt(data[i]);
}
图形就可以正常显示了。