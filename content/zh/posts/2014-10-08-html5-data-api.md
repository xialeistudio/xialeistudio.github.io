---
slug: html5-data-api
title: html5新属性data api
date: 2014-10-08 10:58:44.000000000 +08:00
categories:
- Engineering
---
以往在做列表程序的时候，需要做类似“删除”功能的时候，往往是组装一个URL，类似于这个

index.php?m=news&a=delete&id=10

这是最普通的url方式来进行删除。

但是随着用户体验要求的增加，很多时候都需要使用ajax来实现相应效果。

记得很早以前在写一个CURD项目的时候，我是用ID来做的，类似于 id="news_id_10",id="news_id_11" 这样，然后通过分割字符串来获取ID，简直就是要多麻烦有多麻烦，当时就在想有没有一个能自己定义所需数据的字段呢？

现在好了。HTML5的data-* API可以帮到我们

## html代码

```html
<a href="javascript:void(0)" data-action="delete" data-id="10">删除</a>
```

是不是看到了data-action和data-id属性呢？data-*只要更改*就可以了，需要满足标识符约束。
## js代码

```javascript
$(document).on('click', '[data-action="delete"]',
function() {
    var $id = $(this).data("id");
    var $this = $(this);
    ajax && ajax.abort();
    ajax = $.get('index.php', {
        id: $id,
        m: 'news',
        a: 'delete'
    },
    function(data) {
        if (data.status == 1) {
            //操作成功
        } else {
            alert(data.info);
        }
    },
    'json');
});
```

JQ提供的$.data方法确实挺方便的，但是请注意，本人发现$.data方法是只读的（就是不能改变data-id="10"中的10），如果需要改变，请用底层的$.attr('data-id',9)这种操作。