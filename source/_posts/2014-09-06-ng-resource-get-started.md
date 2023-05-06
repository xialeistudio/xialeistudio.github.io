---
layout: post
title: ngResource快速上手
date: 2014-09-06 20:11:06.000000000 +08:00
type: post
published: true
status: publish
categories:
- Engineering
---
废话不多说，本文的目的就是看过之后就会使用ngResource了。
1. 引入angular-resource.min.js
2. 定义模块时加载ngResource
3. 定义service

完整代码如下

```javascript
var app = angular.module('app', ["ngResource"]);
app.factory('Phone', ['$resource',
function($resource) {
    return $resource('user/:uid', {
        uid: '@uid'
    },
    {
        update: {
            method: 'PUT'
        }
    });
}]);
app.controller('MainCtrl', ['$scope', 'Phone',
function($scope, Phone) {
    $scope.phones = Phone.query();
    Phone.update({
        uid: 1
    },
    {
        name: "zhangsan",
        age: "10"
    });
}]);
```