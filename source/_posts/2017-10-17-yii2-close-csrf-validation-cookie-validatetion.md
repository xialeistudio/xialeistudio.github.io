---
title: yii2关闭csrf校验和cookie校验
date: 2017-10-17 17:19:19
categories:
- engineering
tags:
- yii
---
# 重要提示
```
关闭该选项会导致应用安全性收到影响！
```

# 问题出现
1. 开发API的时候发现POST请求老是不能通过验证，直接把报错文案放到项目中去搜索发现**yii\web\Request**中有**enableCsrfValidation**。
2. 其他应用设置的cookie，抓包的时候可以看到请求中有cookie，但是yii2读取不到。

# 源码解析
找到**yii\web\Request**文件，看到
```php
/**
 * @var bool whether to enable CSRF (Cross-Site Request Forgery) validation. Defaults to true.
 */
public $enableCsrfValidation = true;
/**
 * @var bool whether cookies should be validated to ensure they are not tampered. Defaults to true.
 */
public $enableCookieValidation = true;
```
发现是这里有问题，基于**yii2一切都是组件的思想**，去修改组件配置即可。

# 修正
编辑**config/web.php的components节**
```php
'request'      => [
    'cookieValidationKey'    => 'xxxx',
    'enableCookieValidation' => false,
    'enableCsrfValidation'   => false,
    ],
],
```