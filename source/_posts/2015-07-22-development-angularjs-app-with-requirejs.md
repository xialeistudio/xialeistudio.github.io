---
layout: post
title: angularjs集成requirejs
date: 2015-07-22 14:24:05.000000000 +08:00
type: post
published: true
status: publish
categories:
- Engineering
---
angularjs自带的模块话机制对于业务逻辑的组织确实起到了规范化的作用，但是对于大型web项目，弊端也出来了，一次性加载所有的资源会导致进入应用的时间变长，而实际上，首页需要加载的并不多，所以，本文将介绍如何使用requireJs与angularJs集成。
## 依赖
+ jquery(非必须)
+ angularjs
+ ui-router
+ requirejs

## 入口文件
我们知道，使用requireJs之后，在首页只需使用script标签加载requirejs即可，剩下的文件加载需要配置下入口文件。

```javascript
/**
 * @author xialei <xialeistudio@gmail.com>
 */
require.config({
    baseUrl: 'app',
    paths: {
        "angular": "/vendor/angular/angular",
        "ui-router": "/vendor/ui-router/release/angular-ui-router",
        "jquery": "/vendor/jquery/dist/jquery"
    },
    shim: {
        "angular": {
            exports: "angular",
            deps: ["jquery"]
        },
        "ui-router": {
            exports: "ui-router",
            deps: ["angular"]
        },
        "jquery": {
            exports: "jquery"
        }
    }
});

require(["jquery", "angular", "app","router","controllers"], function($, angular) {
    $(function() {
        angular.bootstrap(document, ["app"]);
    });
});
```

vendor是依赖的库，路径可以根据实际情况进行修改。   
angularjs的代码组织方式不是amd规范的，所以需要使用shim将其暴露出来供其他模块使用。   
由于采用了requireJs，所以不能直接写 angular.module('xx',[])这种代码了。因为依赖的库有可能没下载完成。
## app.js

```javascript
var app = angular.module("app", ["ui.router"]);
```

使用requireJs之后，这种就行不通了，因为amd开发方式下，一切皆模块。   
而app作为“根模块”是需要给其他模块（controller,directive,etc...）使用的，所以模块定义的最后需要return。

```javascript
var app = angular.module("app", ["ui.router"]);
define(["angular","ui-router"], function(angular) {
    var app = angular.module("app", ["ui.router"]);
    return app;
});
```

这样，其他需要依赖app模块的模块就可以使用该“根模块了”。
## controllers.js

```javascript
define(["app"], function(app) {
    app.controller("HomeCtrl", ["$scope", function($scope) {
        $scope.run = function() {
            console.log('run');
        };
    }]);
});
```

controllers是依赖app模块的，所以这里引入app依赖，其他代码与之前一样。

## router.js
之前一直使用angular-router,但是永久之后发现还是ui-router好用，这里使用ui-router作为路由管理库。

```javascript
define(["app"], function(app) {
    app.config(['$stateProvider', '$urlRouterProvider', function($stateProvider, $urlRouterProvider) {
        $stateProvider.state('index', {
            url:"/",
            views: {
                "main": {
                    templateUrl: "app/templates/home.html",
                    controller: "HomeCtrl"
                }
            }
        });
        $urlRouterProvider.otherwise('/');
    }]);
});
```

## index.html

```html
<!DOCTYPE html>
<html>
<head lang="en">
    <meta charset="UTF-8">
    <title>Angularjs+RequireJs</title>
</head>
<body>

<div ui-view="main"></div>
<script src="/vendor/requirejs/require.js" data-main="main"></script>
</body>
</html>
```

相比于之前写很多script标签，这里只需要写一个，是不是“清爽”了很多呢？

## demo
[demo](http://ngdemo.sinaapp.com/ng-requirejs/#/)，打开之后只有一个"run"的按钮，请大家打开控制台之后点击按钮即可。