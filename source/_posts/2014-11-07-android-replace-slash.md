---
layout: post
title: android 替换斜杠
date: 2014-11-07 14:01:45.000000000 +08:00
type: post
published: true
status: publish
categories:
- android
tags:
- regex
---
## 问题
最近写安卓的时候服务端返回的数据会带上“\n”，但是在android这边不能换行，初次想到的解决方法是利用

```java
String.replace("\n","\n")
```

给替换掉，结果是不行的。之前记得java的反斜杠是需要转义的，就用

```java
String.replaceAll("\n","\\n")
```

试了一下，结果依旧不行。后来去查了谷歌--，发现要 \\\\n 才可以 匹配到 \n,这么多斜杠，头都晕了，一个个来解释：
+ 第一个和第二个反斜杠是一组，由于java的转义，实际为 "\"
+ 第三个和第四个同理，

经过以上两步之后，\\\\n 实际上是 \\n ，由于是正则的关系，\\n 可以匹配到字符串的\n了。

## 解决方法
```java
String.replaceAll("\\n","\\n")
```

第一个参数是正则，第二个是普通字符串。不得不吐槽下Java的正则表达式。。