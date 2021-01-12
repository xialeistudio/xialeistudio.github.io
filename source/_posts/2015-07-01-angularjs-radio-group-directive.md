---
layout: post
title: angularjs指令实现radioGroup
date: 2015-07-01 00:26:31.000000000 +08:00
type: post
published: true
status: publish
categories:
- frontend
- angularjs
---
angularjs的指令系统其实也是很强大的东西，扩展了HTML的表现力。本文讲的是如何用angularjs指令实现radioGroup，自带的radio只能控制ngModel的两种状态: true/false。
## 指令代码

```javascript
module.directive('radio', [function() {
    return {
        transclude: true,
        replace: true,
        template: '<div class="ui ui-radio"><span class="radio-item"></span><span ng-transclude="" class="common-color"></span></div>',
        require: 'ngModel',
        link: function(scope, ele, attrs, ctrl) {
            ctrl.$render = function() {
                if(ctrl.$viewValue == attrs.value) {
                    //jqLite不支持siblings方法，如果此段代码无效，请使用zepto实现
                    ele.parent().children().removeClass("active");
                    ele.addClass("active");
                }
            };
            ele.bind("click", function() {
                ctrl.$setViewValue(attrs.value);
                ele.addClass("active");
                var childrens = ele[0].parentNode.children;
                for(var i = 0; i < childrens.length; i++) {
                    if(childrens[i] != ele[0]) {
                        angular.element(childrens[i]).removeClass("active");
                    }
                }
            });
        }
    };
}]);
```

```less
.ui {
  &-radio {
    &.active {
      .radio-item:after {
        display: block;
        width: 19px;
        height: 19px;
        content: ' ';
        position: absolute;
        border-radius: 50%;
        left: (35px-19)/2;
        top: (35px-19)/2;
        background: #d14db7;
      }
    }
    .radio-item {
      width: 35px;
      height: 35px;
      border-radius: 50%;
      position: relative;
      background: white;
      display: inline-block;
      vertical-align: middle;
      margin: 0;
    }
    span {
      margin-left: 12px;
    }
  }
}
```

## HTML

```html
<div ng-init="answer='A'" class="options container-fluid wrapper">
  <div radio="" ng-model="answer" value="A">A. </div>
  <div radio="" ng-model="answer" value="B">B. </div>
  <div radio="" ng-model="answer" value="C">C. </div>
    <div ng-if="questions[index].option_d" radio="" ng-model="answer" value="D">D. </div>
</div>
```

## 效果
![效果](https://og5r5kasb.qnssl.com/wp-content/uploads/2015/07/B0723015-0ECD-403A-9207-78EFB316E358.jpg)