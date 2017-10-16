---
title: Servlet中print-writer和outputstream编码问题
date: 2017-10-16 14:11:40
tags:
-java
-servlet
---
有个项目需要使用java开发一个简单的web接口用来请求加密数据，但是servlet之前只随便用了一下，平时工作也是以**node**为主。
# 问题
问题大致是"iso 88591 encoding之类的问题，稍微去google搜了一下，可能是搜的关键词不准确导致搜到的答案不理想，无意中看到有人讲writer和outputstream的问题。
# 原因
google到PrintWriter和OutputStream的区别

```
PrintWriter是以字符为单位，对所有的信息进行处理，而ServletOutputStream仅对二进制的资料进行处理。 
```

而我输出的是UTF8格式的字符串，所以OutputStream并不认识。

# 解决
使用**PrintWriter**输出即可。