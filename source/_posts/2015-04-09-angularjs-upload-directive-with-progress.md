---
layout: post
title: 带进度条的angularjs上传指令
date: 2015-04-09 19:02:42.000000000 +08:00
type: post
published: true
status: publish
categories:
- engineering
---
## 项目地址
[https://git.coding.net/xialei/xl-angular-upload.git](https://git.coding.net/xialei/xl-angular-upload.git)
## 效果图
![图1](https://og5r5kasb.qnssl.com/wp-content/uploads/2015/04/QQ%E6%88%AA%E5%9B%BE20150409190032-300x144.png)
![图2](https://og5r5kasb.qnssl.com/wp-content/uploads/2015/04/QQ%E6%88%AA%E5%9B%BE20150409190040-300x153.png)
## 指令代码

```javascript
angular.module('xl-angular-upload', [])
    .directive('angularUpload', [function () {
        return {
            restrict: 'E',
            require: 'ngModel',
            template: '<div class="xl-angular-upload">\n    <!--upload button-->\n    <button class="xl-btn btn-primary">上传\n        <input type="file"/>\n    </button>\n    <!--upload queue-->\n    <div class="queue">\n        <div class="item" ng-repeat="item in queue">\n            <div class="info">\n                <div class="no">{{$index+1}}</div>\n                <div class="name">{{item.name}}</div>\n                <div class="size">{{(item.size/1024).toFixed(2)}}KB</div>\n            </div>\n            <div class="process-bar">\n                <div class="process" style="width:{{item.process}}%"></div>\n            </div>\n        </div>\n    </div>\n</div>',
            replace: true,
            link: function (scope, ele, attrs, ctrl) {
                //必要属性检测
                if (!attrs.action) {
                    throw new Error('请设置上传action');
                }
                //初始化
                scope.queue = [];
                var file = angular.element(document.querySelector('.xl-angular-upload>.xl-btn>input[type="file"]'));
                var files = [];
                attrs.accept && file.attr('accept', attrs.accept);
                attrs.multiple && file.attr('multiple', attrs.multiple);
                file.bind("change", function (e) {
                    scope.$apply(function () {
                        scope.queue = [];
                        for (var i in e.target.files) {
                            if (/^\d+$/.test(i)) {
                                e.target.files[i].process = 0;
                                scope.queue.push(e.target.files[i]);
                            }
                        }
                    });
                    //准备上传
                    scope.queue.forEach(function (item) {
                        var data = new FormData;
                        data.append(attrs.name || 'file', item);
                        var xhr = new XMLHttpRequest();
                        xhr.open('POST', attrs.action, true);
                        //事件监听
                        xhr.onreadystatechange = function () {
                            if (xhr.readyState == 4 && xhr.status == 200) {
                                //上传完成了
                                var resp = JSON.parse(xhr.responseText);
                                if (resp.error) {
                                    throw new Error(resp.error);
                                } else {
                                    files.push(resp);
                                    ctrl.$setViewValue(files);
                                }
                            }
                        };
                        xhr.onerror = function (error) {
                            throw new Error(error);
                        };
                        xhr.upload && (xhr.upload.onprogress = function (e) {
                            if (e.lengthComputable) {
                                scope.$apply(function () {
                                    item.process = parseInt((e.loaded / e.total) * 100);
                                });
                            }
                        });
                        xhr.send(data);
                    });
                });
            }
        }
    }]);
```

## HTML代码

```html
<!DOCTYPE html>
<html ng-app="app">
<head lang="en">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>AngularToggle</title>
    <link rel="stylesheet" href="angular-upload.css"/>
    <style>
        * {
            font-family: Consolas, "Microsoft Yahei", arial, sans-serif;
        }
    </style>
</head>
<body ng-controller="MainCtrl">
<div style="width: 400px">
    <angular-upload action="upload.php" name="file" accept="image/*" multiple="true" ng-model="files"/>
</div>
<script src="http://cdn.bootcss.com/angular.js/1.3.15/angular.min.js"></script>
<script src="angular-upload.js"></script>
<script>
    (function () {
        "use strict";
        angular.module('app', [
            'xl-angular-upload'
        ]).controller('MainCtrl', ['$scope', function ($scope) {
            $scope.$watch('files', function (n, o) {
                console.log(n);
            });
        }]);
    })();
</script>
</body>
</html>
```

## CSS代码

```css
.xl-angular-upload .xl-btn {
  color: #666;
  background-color: #EEE;
  border-color: #EEE;
  font-weight: 300;
  font-size: 16px;
  font-family: "Consolas", "Microsoft YaHei", Arial, arial, sans-serif;
  text-decoration: none;
  text-align: center;
  line-height: 40px;
  height: 40px;
  padding: 0 40px;
  margin: 0;
  display: inline-block;
  appearance: none;
  cursor: pointer;
  border: none;
  -webkit-box-sizing: border-box;
  -moz-box-sizing: border-box;
  box-sizing: border-box;
  -webkit-transition-property: all;
  transition-property: all;
  -webkit-transition-duration: .3s;
  transition-duration: .3s;
  border-radius: 4px;
  -webkit-border-radius: 4px;
  -moz-border-radius: 4px;
  position: relative;
}
.xl-angular-upload .xl-btn.btn-primary {
  background-color: #7B72E9;
  border-color: #7B72E9;
  color: #FFF;
}
.xl-angular-upload .xl-btn.btn-primary:hover {
  background-color: #a49ef0;
  border-color: #a49ef0;
  color: #FFF;
}
.xl-angular-upload .xl-btn input[type="file"] {
  position: absolute;
  width: 100%;
  height: 100%;
  left: 0;
  top: 0;
  opacity: 0;
}
.xl-angular-upload .queue {
  width: 100%;
}
.xl-angular-upload .queue .item {
  margin-top: 4px;
}
.xl-angular-upload .queue .item > .info .no {
  float: left;
  width: 10%;
  text-align: center;
}
.xl-angular-upload .queue .item > .info .name {
  float: left;
  width: 70%;
}
.xl-angular-upload .queue .item > .info .size {
  float: right;
  width: 20%;
}
.xl-angular-upload .queue .item > .info:after {
  content: ' ';
  display: block;
  clear: both;
}
.xl-angular-upload .queue .item > .process-bar {
  width: 100%;
  height: 4px;
  margin-top: 4px;
}
.xl-angular-upload .queue .item > .process-bar .process {
  transition: all .2s;
  -webkit-transition: all .2s;
  -moz-transition: all .2s;
  height: 100%;
  width: 0;
  background: #7B72E9;
}
```

本指令的难点在于进度条的更新及ngModel数据的双向绑定，其实，只要在指令中require”ngModel”之后，利用$setViewValue方法和$render方法就可以了。而进度条的处理是由于双向绑定中列表的每个元素都是一个单独的对象，更新该对象的值不会影响其他上传，即每个上传都是单独的进度条。