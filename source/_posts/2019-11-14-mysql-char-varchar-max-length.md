---
title: MySQL中的CHAR和VARCHAR到底支持多长?
date: 2019-11-14 17:00:00
categories:
- backend
- mysql
---

最近在研究MySQL的数据类型，我们知道，选择合适的数据类型和数据长度对MySQL的性能影响是不可忽视的，小字段意味着可以MySQL可以读取更多的记录，从而加快查询速度。

网上该问题的答案有很多版本，还是通过实践得出的结论比较靠谱。

先说结论(MySQL版本5.7.27)

+ CHAR最大255**字符**，字符集对CHAR没有影响，CHAR()括号内填写最大字符数255
+ VARCHAR最大65535**字节**，字符集对VARCHAR有影响
  + UTF8字符集，每个字符大小3字节，所以65535/3 = 21845，最大支持21845字符，因此VARCHAR()括号中最大填写21845字符
  + GBK字符集，每个字符大小2字节，所以65535/2 = 32767.5，最大支持32767**字符**，因此VARCHAR()括号中最大填写32767字符

## 验证过程

### CHAR

UTF8字符集(1个字符占用3个字节)

```sql
CREATE TABLE `test`.`demo`  (
  `id` int(0) UNSIGNED NULL AUTO_INCREMENT,
  `title` char(256) NULL,
  PRIMARY KEY (`id`)
) CHARACTER SET = utf8 COLLATE = utf8_general_ci;
```

MySQL提示错误

```
1074 - Column length too big for column 'title' (max = 255); use BLOB or TEXT instead
```

GBK字符集(1个字符占用2个字节)

```sql
CREATE TABLE `test`.`demo`  (
  `id` int(0) UNSIGNED NULL AUTO_INCREMENT,
  `title` char(256) NULL,
  PRIMARY KEY (`id`)
) CHARACTER SET = gbk COLLATE = gbk_chinese_ci;
```

MySQL提示错误

```
1074 - Column length too big for column 'title' (max = 255); use BLOB or TEXT instead
```

> 结论：CHAR最大长度和字符集没有关系，因此CHAR()括号内填写字符大小，最终数据的字节大小随着字符集不同而不同

### VARCHAR

UTF8字符集(1个字符占用3个字节)

```sql
CREATE TABLE `test`.`demo`  (
  `id` int(0) UNSIGNED NULL AUTO_INCREMENT,
  `title` varchar(65535) NULL,
  PRIMARY KEY (`id`)
) CHARACTER SET = utf8 COLLATE = utf8_general_ci;
```

MySQL提示错误

```
1074 - Column length too big for column 'title' (max = 21845); use BLOB or TEXT instead
```

MySQL提示的最大长度为21845，通过UTF8字符集的大小可知VARCHAR()括号中指的是字符大小。

UTF8MB4字符集(1个字符占用4个字节)

```sql
CREATE TABLE `test`.`demo`  (
  `id` int(0) UNSIGNED NULL AUTO_INCREMENT,
  `title` varchar(65535) NULL,
  PRIMARY KEY (`id`)
) CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci;
```

MySQL提示错误

```
1074 - Column length too big for column 'title' (max = 16383); use BLOB or TEXT instead
```

MySQL提示的最大长度为16383，通过UTF8MB4字符集大小可知VARCHAR()括号中指的是字符大小。

![0.jpeg](https://static.ddhigh.com/blog/2019-10-22-102654.jpg)