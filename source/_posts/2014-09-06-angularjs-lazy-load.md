---
layout: post
title: 摆脱jquery!angularjs利用指令简单实现滚动翻页
date: 2014-09-06 20:14:13.000000000 +08:00
type: post
published: true
status: publish
categories:
- angularjs
tags:
- angularjs
meta:
  _edit_last: '1'
  views: '21729'
  _wp_old_slug: "%e6%91%86%e8%84%b1jqueryangularjs%e5%88%a9%e7%94%a8%e6%8c%87%e4%bb%a4%e7%ae%80%e5%8d%95%e5%ae%9e%e7%8e%b0%e6%bb%9a%e5%8a%a8%e7%bf%bb%e9%a1%b5"
---
移动开发一个很重要的问题是翻页操作，而现在的主流都是滚动翻页，以往都是用jquery的插件进行实现。用了angularjs之后，要逐步减轻对jquery的依赖。   

*滚动翻页基本原理就是判断scrollTop和offsetHeight之和 大于等于 scrollHeight*   
## 代码
### 指令
```javascript
app.directive('whenScrolled', function() { 
  return function(scope, elm, attr) { 
    var raw = elm[0]; 
    elm.bind('scroll', function() { 
      if (raw.scrollTop+raw.offsetHeight &gt;= raw.scrollHeight) { 
        scope.$apply(attr.whenScrolled); 
      } 
    }); 
  }; 
});
```
### 控制器

```javascript
$scope.loadMore = function() { 
    if ($scope.currentPage &lt; $scope.pages) { 
      $scope.currentPage++; 
      if ($scope.busy) { 
        return false; 
      } 
      $scope.busy = true; 
      $http.get('/api.php?r=site/list/page/'+$scope.currentPage+'/limit/'+$scope.limit).success(function(data) { 
        $scope.busy = false; 
        for (var i in data.data) { 
          $scope.newses.push(data.data[i]); 
        } 
        $scope.pages = Math.ceil(data.total/$scope.limit); 
        $rootScope.title = '首页 - 微文章'; 
      }); 
    } 
  };
```

### 视图

```html
<div when-scrolled="loadMore()">
//内容处理逻辑
</div>
```