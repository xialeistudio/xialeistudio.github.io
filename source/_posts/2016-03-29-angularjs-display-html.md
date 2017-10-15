---
layout: post
title: angularjs显示html文本
date: 2016-03-29 16:48:26.000000000 +08:00
type: post
published: true
status: publish
categories:
- angularjs
tags:
- $sce
- sanitize
- angularjs
meta:
  _edit_last: '1'
  _thumbnail_id: '175'
  views: '3215'
---
Angularjs中输出变量使用**花括号**或者**ng-bind**，但是如果变量中有html代码的话，angularjs为了xss安全，默认是不解析html，直接原样显示html代码。   
如果需要显示解析后的html代码，需要使用**angular-sanitize**模块。

angular-sanitize一般会附带在angularjs中，如果没有附带，请前往官网下载对应版本的angular-sanitize模块。
## 模块代码

```javascript
var demo = angular.module('demo',['ng-sanitize']);
```

## 控制器代码

```javascript
demo.controller('Demo13Controller', [
  '$scope', function($scope) {
    $scope.html = '<span style="color: red">这是格式化的HTML文本</span>';
  }
]);
```

## 视图代码

```html
<article class="demo13" ng-controller="Demo13Controller">
<h2><a name="demo13">13.显示HTML文本</a></h2>
<div class="demo13-content">
<p>需要显示的文本：</p>
<p>Html格式化文本： <span ng-bind-html="html|htmlContent"></span></p>
</div>
</article>
```

## 过滤器代码

```javascript
demo.filter('htmlContent',['$sce', function($sce) {
  return function(input) {
    return $sce.trustAsHtml(input);
  }
}]);
```

## 总结
$sce过滤器+ng-bind-html就可以显示html文本了。