---
slug: angularjs-ios-like-toggle
title: angularjs开发ios风格的toggle
date: 2014-12-20 09:12:28.000000000 +08:00
categories:
- Engineering
---
## 效果图
![效果图](https://og5r5kasb.qnssl.com/wp-content/uploads/2014/12/53441419037830.png)

## HTML代码

```html
<div class="toggle-box" ng-click="item.hide_remind = !item.hide_remind"
     ng-class="{'active':item.hide_remind,'':!item.hide_remind}" ng-init="item.hide_remind=0">
    <div class="toggle-container">
        <div class="toggle-item"></div>
    </div>
</div>
```

```css
.site-create .page-bd .container form .form-group .toggle-box {
  position: absolute;
  right: 48px;
  top: 15px;
}
.site-create .page-bd .container form .form-group .toggle-box .toggle-container {
  position: relative;
  width: 72px;
  height: 40px;
  background: #a8aeb3;
  -webkit-border-radius: 24px;
  -moz-border-radius: 24px;
  border-radius: 24px;
  padding: 2px;
}
.site-create .page-bd .container form .form-group .toggle-box .toggle-container .toggle-item {
  width: 39px;
  height: 39px;
  background: white;
  -webkit-border-radius: 39px;
  -moz-border-radius: 39px;
  border-radius: 39px;
  cursor: pointer;
  -webkit-transition: all linear 0.3s;
  -moz-transition: all linear 0.3s;
  -o-transition: all linear 0.3s;
  transition: all linear 0.3s;
}
.site-create .page-bd .container form .form-group .toggle-box.active .toggle-container {
  background: #79e575;
}
.site-create .page-bd .container form .form-group .toggle-box.active .toggle-container .toggle-item {
  margin-left: 32px;
}
```

记得自己去掉不存在的容器（我是在项目中用的，有CSS层级限制）
## JS代码
无

所有的操作都在html中实现的。   
如果需要获取值，请获取**item.hide_remind**即可