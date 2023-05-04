---
layout: post
title: PHP将日期转换为星座
date: 2014-09-06 20:11:56.000000000 +08:00
type: post
published: true
status: publish
categories:
- engineering
---
这几日在做的一个项目发现一个很有意思的东西，就是PHP将指定日期输出为星座

```php
<?php
function constellation($month, $day) 
{ 
    if ($month < 1 || $month > 12 || $day < 1 || $day > 31) return false; 
    $constellations = array( 
      array("20" => '水瓶座'), 
      array("19" => '双鱼座'), 
      array("21" => '白羊座'), 
      array("20" => '金牛座'), 
      array("21" => '双子座'), 
      array("22" => '巨蟹座'), 
      array("23" => '狮子座'), 
      array("23" => '处女座'), 
      array("23" => '天秤座'), 
      array("24" => '天蝎座'), 
      array("22" => '射手座'), 
      array("22" => '摩羯座') 
    ); 
    list($constellation_start, $constellation_name) = each($constellations[(int)$month - 1]); 
    if ($day < $constellation_start) list($constellation_start, $constellation_name) = each($constellations[($month - 2 < 0) ? $month = 11 : $month -= 2]); 
    return $constellation_name;
}
```