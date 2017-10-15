---
layout: post
title: angularjs ueditor指令
date: 2015-02-05 19:20:43.000000000 +08:00
type: post
published: true
status: publish
categories:
- angularjs
tags:
- angularjs
- directive
- ueditor
- rich text editor
meta:
  _edit_last: '1'
  _thumbnail_id: '374'
  views: '7336'
  _wp_old_slug: angularjs%e5%88%a9%e7%94%a8%e6%8c%87%e4%bb%a4%e8%b0%83%e7%94%a8ueditor-2
---
一直以来，angularjs的富文本编辑器都比较难做，主要是第三方的编辑器很难集成进来，今天花时间研究了一下，发现ueditor主要加载两个js文件
+ ueditor.config.js
+ ueditor.all.js

能不能把这两个文件异步加载呢？答案是肯定的。我们新建一个服务用来异步加载资源，并设置必要的回调方法。

## Factory

```javascript
services.factory('Common', ['$http', '$q',
function($http, $q) {
    return {
        loadScript: function(url, callback) {
            var head = document.getElementsByTagName("head")[0];
            var script = document.createElement("script");
            script.setAttribute("type", "text/javascript");
            script.setAttribute("src", url);
            script.setAttribute("async", true);
            script.setAttribute("defer", true);
            head.appendChild(script);
            //fuck ie! duck type
            if (document.all) {
                script.onreadystatechange = function() {
                    var state = this.readyState;
                    if (state === 'loaded' || state === 'complete') {
                        callback && callback();
                    }
                }
            } else {
                //firefox, chrome
                script.onload = function() {
                    callback && callback();
                }
            }
        },
        loadCss: function(url) {
            var ele = document.createElement('link');
            ele.href = url;
            ele.rel = 'stylesheet';
            if (ele.onload == null) {
                ele.onload = function() {};
            } else {
                ele.onreadystatechange = function() {};
            }
            angular.element(document.querySelector('body')).prepend(ele);
        }
    }
}]);
```

通过绑定callback到 onload 事件来实现回调。
## 指令

```javascript
directives.directive('ueditor', ['Common', '$rootScope',
function(Common, $rootScope) {
    return {
        restrict: 'EA',
        require: 'ngModel',
        link: function(scope, ele, attrs, ctrl) {
            $rootScope.$emit('loading', '初始化编辑器...'); //广播loading事件，可以删除
            var _self = this,
            _initContent, editor, editorReady = false,
            base = '/public/vendor/utf8_qiniu_ueditor-master',
            //ueditor目录
            _id = attrs.ueditor;
            var editorHandler = {
                init: function() {
                    window.UEDITOR_HOME_URL = base + '/';
                    var _self = this;
                    if (typeof UE != 'undefined') {
                        editor = UE.getEditor(_id, {
                            toolbars: [['fontsize', '|', 'blockquote', 'horizontal', '|', 'removeformat', '|', 'insertimage', '|', 'bold', 'italic', 'underline', 'forecolor', 'backcolor', '|', 'justifyleft', 'justifycenter', 'justifyright', 'justifyjustify', 'rowspacingtop', 'rowspacingbottom', 'lineheight', '|', 'insertorderedlist', 'insertunorderedlist', '|', 'link', 'unlink', '|', 'emotion']]
                        });
                        editor.ready(function() {
                            editor.setHeight(500);
                            editorReady = true;
                            $rootScope.$emit('loading', ''); //编辑器初始化完成
                            editor.addListener('contentChange',
                            function() { //双向绑定
                                if (!scope.$$phase) {
                                    scope.$apply(function() {
                                        ctrl.$setViewValue(editor.getContent());
                                    });
                                }
                            });
                        });
                    } else {
                        Common.loadScript(base + '/ueditor.config.js', null);
                        Common.loadScript(base + '/ueditor.all.min.js',
                        function() {
                            _self.init();
                        });
                    }
                },
                setContent: function(content) {
                    if (editor && editorReady) {
                        editor.setContent(content);
                    }
                }
            };
            ctrl.$render = function() {
                _initContent = ctrl.$isEmpty(ctrl.$viewValue) ? '': ctrl.$viewValue;
                editorHandler.setContent(_initContent); //双向绑定
            };
            editorHandler.init();
            //事件
            $rootScope.$on('$routeChangeStart',
            function() {
                editor && editor.destroy();
            });
        }
    }
}]);
```

由于angularjs无法自动获得编辑器内容，只能手动监听 contentChange事件来实现双向绑定。

## 模板代码

```html
<div ueditor="editor" ng-required="true" ng-model="material.content.content" id="editor"></div> 
```

## 效果图
![效果图](https://og5r5kasb.qnssl.com/wp-content/uploads/2015/02/QQ%E6%88%AA%E5%9B%BE20150205191752.png)