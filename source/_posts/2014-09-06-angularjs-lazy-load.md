---
layout: post
title: 摆脱jquery!angularjs利用指令简单实现滚动翻页
date: 2014-09-06 20:14:13.000000000 +08:00
type: post
published: true
status: publish
categories:
- engineering
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