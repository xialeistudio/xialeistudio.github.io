---
slug: php-chinese-reverse
title: php中文字符串反转
date: 2014-09-06 19:57:42.000000000 +08:00
categories:
- Engineering
---

php **strrev()** 函数能实现字符串反转，但是不支持中文，利用mb_系列函数可以进行中文字符串反转。

```php
/**
 * 中文字符串反转
 * @param $str
 * @param string $charset
 * @return string
 */
function reverse($str, $charset = 'UTF-8')
{
    $ret = '';
    $len = mb_strlen($str, $charset);
    for ($i = 0; $i < $len; $i++) {
        $ret[] = mb_substr($str, $i, 1, $charset);
    }

    return implode('', array_reverse($ret));
}
```