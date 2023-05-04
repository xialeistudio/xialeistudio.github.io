---
layout: post
title: PHPExcel导出时列过大的解决方案
date: 2015-03-07 11:41:30.000000000 +08:00
type: post
published: true
status: publish
categories:
- engineering
---
今天导出Excel的时候，列不是固定的，而且有差不多几十个，横轴由'A'变为了'AA'，给导出时增加了难度，因为要去算列名称，不过换个方式想一下，发现是很有规律的26进制数。 发现秘诀后就好办了，发一个10进制转26进制的方法。
## 代码

```php
private function numberToStr26($n)
{
    $s = '';
    while ($n > 0) {
        $m = $n % 26;
        if ($m == 0) $m = 26;
        $s = chr($m + 64) . $s;
        $n = ($n - $m) / 26;
    }
    return $s;
}
```

## 效果图
![效果图](https://og5r5kasb.qnssl.com/wp-content/uploads/2015/03/QQ%E6%88%AA%E5%9B%BE20150307113935.png)