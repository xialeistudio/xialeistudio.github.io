---
layout: post
title: 移动端input和textarea宽度不一致的问题
date: 2015-07-05 20:15:07.000000000 +08:00
type: post
published: true
status: publish
categories:
- frontend
- css
---
今天在做写一个IOS端的表单时，尽管input,textarea设置了宽度，结果发现真机浏览的时候发现宽度不一致，有图为证   
![图片](https://og5r5kasb.qnssl.com/wp-content/uploads/2015/07/IMG_0839.png)

## css

```css
input,
textarea {
  border-radius: 4px;
  border: 1px solid #4f4f4f;
  font-size: 24px;
  background: none;
  outline: 0;
  width: 283px;
  -webkit-box-shadow: 0 0 4px rgba(0, 0, 0, .4);
}
```

在PC版的chrome发现textarea有默认的padding属性，估计是这个问题，加上padding:0;之后，宽度一致了。   
![图片](https://og5r5kasb.qnssl.com/wp-content/uploads/2015/07/IMG_0840.png)
