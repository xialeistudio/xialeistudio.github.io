---
layout: post
title: php OOP中的__get和__set方法
date: 2014-09-07 11:46:40.000000000 +08:00
type: post
published: true
status: publish
categories:
- Engineering
---
__get,__set光看前面两个下划线就知道是魔术方法了，而且还是PHP OOP中比较重要的方法。

先看一段代码

```php
<?php
class Account{
    private $user = 1;
    private $pwd = 2;
}
$a = new Account();
echo $a->user;
$a->name = 5;
echo $a->name;
echo $a->big;
```
运行这段代码结果是肯定会报错的！

原因在于，不能访问私有属性user。利用__get和__set改进下这个类

```php
<?php
class Account{
    private $user = 1;
    private $pwd = 2;
    
    public function __set($name,$value){
        $this->name = $value;
    }
    
    public function __get($name){
        if(!isset($this->name)){
            $this->name = '这是默认值';
        }
        return $this->name;
    }
}
$a = new Account();
echo $a->user;
$a->name = 5;
echo $a->name;
echo $a->big;
```

运行之后就不会报错了。

现在有了这两个魔术方法就可以随时扩展类里面的属性了，是不是很方便呢？