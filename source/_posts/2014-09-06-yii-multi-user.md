---
layout: post
title: Yii同一站点配置多个用户角色
date: 2014-09-06 20:01:42.000000000 +08:00
type: post
published: true
status: publish
categories:
- Engineering
tags:
- yii
---
Yii是基于组件的PHP MVC框架，yii的用户组件调用很方便，但是如果有遇到一个站点有多种用户的时候，如前台用户，后台用户，就需要增加User组件了。

简单来说，就是新建一个用户类去继承 CWebUser类，比如

WebUser继承CWebUser，配置文件在components中增加

```php
'user'=>array(
    'class'=>'WebUser'
)
```

以上就创建了一个前台用户,调用方式 Yii::app()->user

后台用户可以这么写

AdminUser继承CWebUser,配置文件在components中增加

```php
'admin'=>array(
    'class'=>'AdminUser'
)
```

这样就创建了一个后台用户，调用方式 Yii::app()->admin

这种方法是本人所知最科学的，比用session来区分好多了。毕竟很多时候，能用框架现有的方法就用框架的方法。