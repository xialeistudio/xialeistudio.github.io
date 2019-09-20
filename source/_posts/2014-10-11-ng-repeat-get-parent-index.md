---
layout: post
title: ng-repeat获取父级INDEX
date: 2014-10-11 11:37:48.000000000 +08:00
type: post
published: true
status: publish
categories:
- frontend
- angularjs
---
angularjs的循环嵌套我就不多说了，无非是ng-repeat的嵌套而已，如果需要获取索引请使用$index。

那么问题来了，$index只能获取当前循环的索引，如果需要获取父级的索引怎么办？

原理其实也不难，在父级ng-repeat时利用ng-init写入一个变量即可，子循环是可以访问到的。

```html
<div ng-controller="MainCtrl">
    <dl ng-repeat="user in users">
       <dt ng-init="p_index=$index">Name:</dt>
        <dd ng-repeat="p in user.posts">父级INDEX: - 
        自己的INDEX:
        </dd>
    </dl>
</div>
```

```javascript
var site = angular.module('application.site', []);
site.controller('MainCtrl', ['$scope', '$http', function ($scope, $http) {
    $scope.users = [
        {name:"xialei",posts:["文章一","文章二","文章三"]},
        {name:"zhangsan",posts:["文章四","文章五"]}
    ];
}]);
```

这里只是关键代码，用过angularjs的小伙伴们相信一眼就可以看懂了。