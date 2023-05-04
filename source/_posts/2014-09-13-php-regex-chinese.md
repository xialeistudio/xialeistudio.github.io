---
layout: post
title: PHP正则表达式匹配中文
date: 2014-09-13 11:20:26.000000000 +08:00
type: post
published: true
status: publish
categories:
- engineering
tags:
- regex
---
正常的正则表达式匹配英文和数字以及一些常用字符还是很简单的，如

```php
/^\w$/
/^[0-9]$/
/^[\-\_]$/
```

等等，但是匹配中文的话就有些麻烦了。UTF-8的中文根据unicode编码，所以我们需要手动构造UTF-8字符串

```php
/^[\x{4e00}-\x{9fa5}]$/u
```

请注意大括号，因为没有大括号PHP会报错

```bash
Warning: preg_match() [function.preg-match]: Compilation failed: PCRE does not support \L, \l, \N, \U, or \u at offset 3 in test.php on line 3
```

因为\x是表示十六进制数的，所以需要用大括号括起来

另外，需要增加 u 修饰符。

此修正符启用了一个 PCRE 中与 Perl 不兼容的额外功能。模式字符串被当成 UTF-8。

本修正符在 Unix 下自 PHP 4.1.0 起可用，在 win32 下自 PHP 4.2.3 起可用。

很多时候google的作用确实比 X度 大，学会google吧！