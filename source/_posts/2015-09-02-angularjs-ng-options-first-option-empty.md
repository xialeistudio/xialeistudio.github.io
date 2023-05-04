---
layout: post
title: angularjs ng-options第一个选项为空的解决方案
date: 2015-09-02 17:07:54.000000000 +08:00
type: post
published: true
status: publish
categories:
- engineering
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