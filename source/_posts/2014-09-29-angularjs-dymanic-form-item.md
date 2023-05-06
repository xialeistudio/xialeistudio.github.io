---
layout: post
title: Angularjs动态表单项
date: 2014-09-29 16:56:03.000000000 +08:00
type: post
published: true
status: publish
categories:
- Engineering
---
后台业务系统中有很多CURD操作，一个很简单的例子是OA系统中为员工添加帐号信息，传统的做法是添加完一个就跳转并提示“成功”,后来高级一点的做法是利用jquery来做。

但是一个比较麻烦的问题是需要手动拼接HTML并且插入文档树。

然而，现在有了跨时代神器--angularjs,就是这么炫，强大的双向绑定功能可以帮到我们。

整体思想是利用 ng-repeat 指令来遍历一个临时数组（元素个数为表单个数）生成表单

## HTML代码

```html
<!DOCTYPE html>
<html ng-app="application.site">
<head>
    <meta charset="UTF-8"/>
    <title>Login</title>
</head>
<body>

<div ng-controller="ListCtrl">
    <button type="button" ng-click="add()">添加表单</button>
    <form action="" method="post" class="form" ng-repeat="form in forms" novalidate="novalidate">
        <p> 号表单</p>
        <label for="username">帐号</label>
        <input type="text" ng-model="username" id="username" ng-required="true"/>
        <button type="submit" ng-click="post($index,username)">提交</button>
        <button type="button" ng-click="remove($index)">移除</button>
    </form>
</div>
<script src="js/angularjs-1.2.19.js"></script>
```

## JS代码

```javascript
var site = angular.module('application.site', []);
site.controller('ListCtrl', ['$scope', '$http',
function($scope, $http) {
    $scope.forms = ["1"];

    $scope.index = 1;
    $scope.post = function(index, username) {
        console.log(index + ' 号表单提交 [' + username + '] 成功');
    }
    $scope.remove = function(index) {
        console.log('删除 [' + index + '] 号表单成功');
        $scope.forms.splice(index, 1);
    }
    $scope.add = function() {
        console.log('添加表单');
        $scope.forms.push((++$scope.index).toString());
    }
}]);
```

由于小编只是为了实现功能而写的这么一个demo，样式至上难免有些欠缺--。但是，麻雀虽小，五脏俱全，大家可以根据这个思路去开发更为强大的应用系统。