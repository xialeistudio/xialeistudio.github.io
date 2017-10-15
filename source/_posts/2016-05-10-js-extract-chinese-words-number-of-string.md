---
layout: post
title: JS提取字符串中文英文数字
date: 2016-05-10 17:06:28.000000000 +08:00
type: post
published: true
status: publish
categories:
- javascript
tags:
- js
- regex
meta:
  _edit_last: '1'
  views: '630'
---
最近在做导出excel的时候，发现导出成功，文件大小也正常，但是Office 2013打不开，检查数据库发现，导出数据中有非中文字符导致Excel异常。   

我们知道JS是支持unicode字符集的，符合导出规则的字符应该是"中文"、"英文"、"数字"。

## 正则表达式

```javascript
/([\u4e00-\u9fa5\w]*)/ig
```

## 提取字符串

```javascript
/**
* 获得可打印字符
* @param str 需要提取的字符串
*/
function getPrintableChars(str) {
  const matches = str.match(/([\u4e00-\u9fa5\w]*)/ig);
  let a = '';
  matches.forEach(item=> item && (a += item));
  return a;
}
```