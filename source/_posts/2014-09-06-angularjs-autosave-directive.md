---
layout: post
title: Angularjs自动保存指令
date: 2014-09-06 19:59:23.000000000 +08:00
type: post
published: true
status: publish
categories:
- engineering
---
angularjs的指令真是好东西，也是精髓。刚才群里面有朋友在问如何在用户离开编辑区域时提醒保存，其实用指令实现很简单的。

请注意，这里使用的指令标签为**ajax-submit**

```javascript
app.directive('ajaxSubmit', [
	'$http', function($http) {
		return {
			link: function(scope, ele, attrs) {
				var old = ele.val();
				ele.bind('blur', function() {
					var url = ele.data('url');
					var val = ele.val();

					ele.prop('disabled', true);
					//发送http
					$http.post(url, {
						data: val
					}).success(function(data) {
						ele.prop('disabled', false);
						if (data.msg != undefined) {
							old = val;
							ele.after('操作成功');
							setTimeout(function() {
								ele.next().remove();
							}, 1000);
						}
						else {
							alert(data.error);
						}
					});
				});
			}
		}
	}
]);
```

关键是利用指令的link函数获取包装后的jq元素，然后给该元素进行事件绑定，其实很多的事件绑定都是这样做的。事件处理函数中的业务逻辑各位看官可以自行修改~。