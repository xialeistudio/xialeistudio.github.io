---
title: 书籍答疑
date: 2018-01-21
---

+ QQ群 346660435
+ 微信群 ![微信群二维码](http://static.ddhigh.com/1516637757389.jpg)

# ThinkPHP实战

+ ISBN:9787302466529
+ 出版时间:2017-03-01
+ 出版社:清华大学出版社

## 问题1（28页）

不知道 page 28是不是少了 几行

1. 确认httpd.conf配置文件中加载了mod_rewrite.so模块，加载的方法是去掉mod_rewrite.so，前面的注释#号
1. httpd.conf中的Allowoverride  None 将None改为All

## 问题1回复

1. **httpd.conf**的**123行**已经默认开启**mod_rewrite.so**模块，故书本中未提出
1. **httpd-vhosts.conf**初始内容如下(未开启upupw的**s1**选项)

```text
<VirtualHost *:80>
    DocumentRoot "X:/upupw/htdocs"
    ServerName 127.0.0.1:80
    ServerAlias localhost
    ServerAdmin webmaster@localhost
    DirectoryIndex index.html index.htm index.php default.php app.php u.php
    ErrorLog logs/localhost_error.log
    CustomLog logs/localhost_access_%Y%m%d.log comonvhost
    php_admin_value open_basedir "X:\upupw\htdocs\;X:\upupw\memcached\;X:\upupw\phpmyadmin\;X:\upupw\temp\;C:\Windows\Temp\"
<Directory "X:/upupw/htdocs">
    Options FollowSymLinks
    AllowOverride All
    Require all granted
</Directory>
<LocationMatch "/(inc)/(.*)$">
    Require all denied
</LocationMatch>
<LocationMatch "/(attachment|attachments|uploadfiles|avatar)/(.*).(php|php5|phps|asp|aspx|jsp)$">
    Require all denied
</LocationMatch>
</VirtualHost>
```

可以看到默认已经**AllowOverride All**

## 问题2（29页-30页）

+ http://localhost/home/posts/2015/01/01 测试失败
+ http://localhost/index.php/home/posts/2015/01/01 测试成功

## 问题2回复

1. 检查index.php所在目录是否有**.htaccess**文件
1. 检查httpd.conf是否开启了mod_rewrite模块

## 问题3（31页）

+ http://localhost/index.php/home/posts/2017/12/9
显示 year:2017,month:12,day:9
+ http://localhost/index.php/home/posts/2017/12/19
显示 year:2017,month:12,day:1

由于我的测试程序 是直接安装是网页根目录内
/htdocs/myweb/
thinkphp 相关目录结构就在 /myweb内
再手输入 范例 并没有 chapterxx 等目录结构

## 问题3回复

请将chapter-3/Application/Home/Conf/config.php中

```php
/^posts\/(\d{4})\/(\d{2})\/(\d{2})$/' => 'Index/index?year=:1&month=:2&day=1
```

最后的**=1**改为**=:1**，以下是修改结果

```php
/^posts\/(\d{4})\/(\d{2})\/(\d{2})$/' => 'Index/index?year=:1&month=:2&day=:1
```

## 问题4（53页）

```php
<?php
return array (
'DB_TYPE'  =>'pdo',
'DB_HOST'  =>'localhost',
```

设定成`'DB_TYPE'  =>'mysql'`才能连接

## 问题4回复

需要开启php的pdo_mysql扩展才能使用，否则只能使用mysql的DB_TYPE

## 问题5（84页行第7行）

编辑 Application/Home/IndexController.class.php
是不是
编辑 Application/Home/Controller/IndexController

## 问题5回复

是，但是ThinkPHP框架对项目文件名称做了严格限定，所以书本中尽量写详细，担心有些读者可能出现问题不知道如何解决。

## 问题6(132页)

+ 文件名 /Application/Home/Controller/IndexController.class.php

```php
    public function log()
    {
        Log::record('ERR - record', Log::ERR);
        Log::write('INFO - write', Log::INFO);
        Log::record('INFO - record', Log::INFO);
    }
```

+ 访问地址 http://loalhost/index.php/home/index/log

+ 错误信息

```text
 
 :(
Class 'Home\Controller\Log' not found
错误位置
 
FILE: /usr/local/apache2/htdocs/dfweb/Application/Home/Controller/IndexController.class.php 　LINE: 13
 
ThinkPHP3.2.3 { Fast & Simple OOP PHP Framework } -- [ WE CAN DO IT JUST THINK ]
 
 
错误行 Log::record('ERR - record',Log::ERR);
```

## 问题6回复

请确认**/Application/Home/Controller/IndexController.class.php** 顶部有如下代码：

```php
<?php
namespace Home\Controller;

use Think\Controller;
use Think\Exception;
use Think\Log;
use Think\Model;
```

这位读者出错的问题在于**use Think\Log;**该类没有引入。建议使用智能IDE（如PHPStorm）进行PHP开发。

## 问题7（139页）

```php
$model->cache(true,3600,'xcache')->select();
```

```text
 
:(
系统不支持:Xcache
错误位置
 
FILE: /usr/local/apache2/htdocs/dfweb/ThinkPHP/Library/Think/Cache/Driver/Xcache.class.php 　LINE: 26
 
 
是不是 少了 Xcache 的 模块
http://www.thinkphp.cn/topic/12023.html
```

## 问题7回复

如果使用xcache作为缓存，需要手动安装xcache扩展，[下载地址](http://xcache.lighttpd.net/pub/Releases/3.2.0/)

## 问题8（142页-143页）

范例有用到 Page，在 IndexController.class.php，里面是不是要加上 use Think\Page

## 问题8回复

是的，只要是提示有类似**Class XXX\XXX not found**之类的错误，都需要引入相应的类。

## 问题9

何时出ThinkPHP5的新书

## 问题9回复

预计2018年

## 问题10（154页-155页）

这里用到的表名 最好 说明 库名 及 表名

messageId  应该是 message_id
userId     应该是 user_id

## 问题10回复

待处理

## 问题11（158页）

这里的 function delete 范例 和 书本 不一致
 
IndexController.class.php
 书本里用的是

```php
$result = $model->where(array('message_id' => $id, 'user_id' => session('user.userId')))->delete();
```
 
范例里面是

```php
$result = $model->where(array('message_id' => $id, 'user_id' => session('user.userId')))->find();
```

## 问题11回复

待处理

## 问题12（171页-182页）

BaseController.class

```php
<?php
/**
* Project: thinkphp-inaction
* User: xialei
* Date: 2016/8/13 0013
* Time: 17:25
*/
namespace Admin\Controller;
 
use Think\Controller;

class BaseController extends Controller
{
    protected function _initialize()
    {
        if (!in_array(ACTION_NAME, $this->publicActions) && session('admin.adminId') === null)
        {
            $this->error('请登录', U('admin/index/login'));
        }
        C('LAYOUT_NAME', 'admin');
    }
```

=== null  ???
 
php 我没用过这种判断

## 问题12回复

以下是摘自PHP官方文档的说明：

| 例子 | 名称           | 	结果  |
| ----- |:-------------:| --------|
| $a == $b| 等于 | TRUE，如果类型转换后 $a 等于 $b。 |
| $a === $b| 全等      |   TRUE，如果$a等于$b，并且它们类型也相同。 |
| $a != $b	|不等	|TRUE，如果类型转换后 $a 不等于 $b。 |
|$a <> $b	|不等	|TRUE，如果类型转换后 $a 不等于 $b。
|$a !== $b|	不全等|	TRUE，如果$a不等于$b，或他们类型不同。
|$a < $b|	小与|	TRUE，如果 $a 严格小于 $b。
|$a > $b|	大于|	TRUE，如果 $a 严格大于 $b。
|$a <= $b|	小于等于|	TRUE，如果 $a 小于或者等于 $b。
|$a >= $b|	大于等于|	TRUE，如果 $a 大于或者等于 $b。

## 问题13（172页）

在 172 的 function index()
是不是该说明是哪一个 class

## 问题13回复

待处理

## 问题14

在最后是不是 写上 测试网址好一点我目前 卡在这里了

## 问题14回复

请把卡住的地方详细说明一下，谢谢！