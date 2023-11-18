---
slug: angularjs-load-remote-data-on-directive
title: Angularjs指令数据远程请求的处理
date: 2014-09-06 20:01:03.000000000 +08:00
categories:
- Engineering
---
假设有一个指令用来根据IP地址进行地位，获取实际地址。

首先，我们的IP地址是由后台PHP程序返回的，这里需要一个Http请求，使用了Http请求就会有类似回调的问题，之前想了各种办法，死活拿不到数据，后来去ng官网看了下，需要使用ngModel，这个是双向绑定。

## 指令代码

```javascript
app.directive('location', ['ApiService', function (ApiService) {
    return {
        restrict: 'A',
        require:'ngModel',
        link: function (scope, ele, attrs,ngModel) {
            ele.addClass('opt');
            ele.bind('click', function () {
                ele.text('定位中...');
                ApiService.location(ngModel.$viewValue).success(function (data) {
                    ele.text(data.country + ' ' + data.region + ' ' + data.city + ' ' + data.isp);
                });
            });
        }
    };
}]);
```

## HTML部分

```html
<span location ng-model="user.login_ip">定位</span>
```

JS中的ngModel 会去搜索该指令的元素上的ng-model指令，这里会搜索到一个user.login_ip 的model,然后JS中使用ngModel.$viewValue 就可以拿到值了。

