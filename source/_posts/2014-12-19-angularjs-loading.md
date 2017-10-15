---
layout: post
title: angularjs注入拦截器实现Loading效果
date: 2014-12-19 19:35:34.000000000 +08:00
type: post
published: true
status: publish
categories:
- angularjs
tags:
- loading
- interceptor
meta:
  _thumbnail_id: '216'
  _edit_last: '1'
  views: '16643'
  _wp_old_slug: angularjs%e6%b3%a8%e5%85%a5%e6%8b%a6%e6%88%aa%e5%99%a8%e5%ae%9e%e7%8e%b0loading%e6%95%88%e6%9e%9c
---
angularjs作为一个全ajax的框架，对于请求，如果页面上不做任何操作的话，在结果烦回来之前，页面是没有任何响应的，不像普通的HTTP请求，会有进度条之类。

本文通过对httpProvider注入拦截器实现loading。
## HTML代码

```html
<div class="loading-modal modal" ng-if="loading">
    <div class="loading">
        <img src="<?=$this->module->getAssetsUrl()?>/img/loading.gif" alt=""/><span ng-bind="loading_text"></span>
    </div>
</div>
```

## LESS代码

```css
.modal {
  position: fixed;
  width: 100%;
  height: 100%;
  left: 0;
  top: 0;
  z-index: 99;
  background: rgba(0, 0, 0, 0.3);
  overflow: hidden;
}

.loading {
  position: absolute;
  top: 50%;
  background: white;
  #solution> .border-radius(8px);
  width: 160px;
  height: 72px;
  left: 50%;
  margin-top: -36px;
  margin-left: -80px;
  text-align: center;
  img {
    margin-top: 12px;
    text-align: center;
  }
  span {
    display: block;
  }
}
```

## JS代码

```javascript
app.config(["$routeProvider", "$httpProvider", function ($routeProvider, $httpProvider) {
    $routeProvider.when('/', {
        templateUrl: "/views/reminder/index.html",
        controller: "IndexController"
    });
    $routeProvider.when('/create', {
        templateUrl: "/views/reminder/item/create.html",
        controller: "ItemCreateController"
    });
    $routeProvider.otherwise({redirectTo: '/'});
    $httpProvider.interceptors.push('timestampMarker');
}]);

//loading
app.factory('timestampMarker', ["$rootScope", function ($rootScope) {
    var timestampMarker = {
        request: function (config) {
            $rootScope.loading = true;
            config.requestTimestamp = new Date().getTime();
            return config;
        },
        response: function (response) {
           // $rootScope.loading = false;
            response.config.responseTimestamp = new Date().getTime();
            return response;
        }
    };
    return timestampMarker;
}]);
```

## 效果图
![效果图](https://og5r5kasb.qnssl.com/wp-content/uploads/2014/12/C34B52AD-CEA0-4762-85A6-45B6869D757A.jpg)