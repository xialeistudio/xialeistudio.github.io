---
layout: post
title: angularjs ng-options第一个选项为空的解决方案
date: 2015-09-02 17:07:54.000000000 +08:00
type: post
published: true
status: publish
categories:
- angularjs
tags:
- angularjs
- ng-options
meta:
  _edit_last: '1'
  views: '4153'
  _thumbnail_id: '495'
  _wp_old_slug: angularjs-ng-options%e7%ac%ac%e4%b8%80%e4%b8%aa%e9%80%89%e9%a1%b9%e4%b8%ba%e7%a9%ba%e7%9a%84%e8%a7%a3%e5%86%b3%e6%96%b9%e6%a1%88
---
angularjs的ng-options渲染到页面上的时候结构大致是这样的。

```html
<select>
  <option value=""></option>
    <option value="1">北京</option>
</select>
```

这样会导致select第一行为空，用户体验很差。所以改造后的代码如下

```html
<select>
  <option value="" selected hidden></option>
  <option value="1">北京</option>
</select>
```

这样就可以避免第一行的空行了。配合绝对定位以及加个div，可以做个很好看的下拉列表样式。