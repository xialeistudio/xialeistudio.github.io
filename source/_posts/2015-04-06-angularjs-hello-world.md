---
layout: post
title: angularjs Hello World
date: 2015-04-06 18:04:48.000000000 +08:00
type: post
published: true
status: publish
categories:
- frontend
- angularjs
---
几乎所有的编程入门都是以"Hello World"开始的，这里也不例外。
## HTML代码

```html
<!DOCTYPE html>
<!--使用ng-app指令“告诉”ng从哪里开始编译-->
<html ng-app="app">
<head lang="en">
    <meta charset="UTF-8">
    <title>Hello World - Angularjs</title>
    <script src="../vendor/angularjs/angular.js"></script>
    <script src="main.js"></script>
</head>
<body>
<p></p>
<input type="text" ng-model="message" placeholder="说点什么"/>
</body>
</html>
```

## JS代码

```javascript
/**
 * @author xialei <xialeistudio@gmail.com>
 */
var app = angular.module('app',[
]);
```

双向绑定为ng内置，所以这里的js，实际上只有一个app定义罢了。   
在输入框中输入任何字符都会及时在其之前的p元素显示出来。