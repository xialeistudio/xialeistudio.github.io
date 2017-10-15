---
layout: post
title: 在AngularJS中使用$q进行“同步”编程
date: 2015-04-06 23:22:59.000000000 +08:00
type: post
published: true
status: publish
categories:
- angularjs
tags:
- $q
- angularjs
- promise
meta:
  _edit_last: '1'
  views: '8585'
  _thumbnail_id: '175'
  _wp_old_slug: "%e5%9c%a8angularjs%e4%b8%ad%e4%bd%bf%e7%94%a8q%e8%bf%9b%e8%a1%8c%e5%90%8c%e6%ad%a5%e7%bc%96%e7%a8%8b"
---
今天群里有位朋友问到直接返回$http说读不到数据，原因在于$http是异步请求，而且是“不可期”的，你不知道什么时候这个请求完成了。

而对于这种需要“同步”编程的方式，AngularJS提供了一个内置Service $q，它提供了一种承诺/延后（promise/deferred），可以保证我们的调用代码一定能够拿到数据。所以我们用起来可以像同步调用一样，话说回来，最终还是xhr异步请求。

##　Factory

```javascript
app.factory('itemService', ['$http', '$q', function ($http, $q) {  
  return {  
    query : function() {  
      var deferred = $q.defer();//声明承诺
      $http({method: 'GET', url: '/item/list'}).  
      success(function(data) {  
        deferred.resolve(data);//请求成功
      }).  
      error(function(data) {  
        deferred.reject(data); //请求失败
      });  
      return deferred.promise;   // 返回承诺，这里返回的不是数据，而是API
    } 
  };  
}]);  
```

## Controller

```javascript
angular.module('app')  
  .controller('MainCtrl', ['itemService','$scope', function (itemService,$scope) { // 注入itemService
    var promise = itemService.query(); //获得承诺接口  
    promise.then(function(data) {  // 成功回调
        $scope.user = data;  
    }, function(data) {  // 错误回调
        console.log('请求失败');
    });  
  }]);  
```

## 文档地址
[http://docs.angularjs.org/api/ng.$q](http://docs.angularjs.org/api/ng.$q)