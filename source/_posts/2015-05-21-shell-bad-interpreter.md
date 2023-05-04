---
layout: post
title: linux运行dos格式脚本导致的bad interpreter
date: 2015-05-21 12:01:15.000000000 +08:00
type: post
published: true
status: publish
categories:
- engineering
---

## 问题

在使用php作为linux上shell脚本运行时出现了以下错误：

```php
#!/usr/bin/env php
<?php
phpinfo();
```

```bash
chmod +x test.php
./test.php
/usr/local/php/bin/php^M: bad interpreter: No such file or directory
```

原因是你的文本以DOS文件形式保存，导致文件头有不可见字符，导致bash shell无法解析。

## 解决办法

```bash
yum install dos2unix -y
dos2unix test.php
```

再执行就没问题了