---
layout: post
title: 重复调用file_get_contents的问题
date: 2016-09-18 17:56:46.000000000 +08:00
type: post
published: true
status: publish
categories:
- backend
- php
---
笔者在写Restful API的时候需要取得原始请求体，读了若干次输入流（将读取操作封装成了函数），发现就第一个参数有值，以后的读取都没有值。

起初以为是参数名写错导致读取失败，检查发现不是这个问题。

单步调试发现php://input只有第一次读取有值，以后的调用都是空。遇到这种问题往往需要查PHP的官方文档。

在文档中找到以下说明：

*php://input 是个可以访问请求的原始数据的只读流。 POST 请求的情况下，最好使用 php://input 来代替 $HTTP_RAW_POST_DATA，因为它不依赖于特定的 php.ini 指令。 而且，这样的情况下 $HTTP_RAW_POST_DATA 默认没有填充， 比激活 always_populate_raw_post_data 潜在需要更少的内存。 enctype="multipart/form-data" 的时候 php://input 是无效的。*

还有一个特别说明:

*在 PHP 5.6 之前 php://input 打开的数据流只能读取一次； 数据流不支持 seek 操作。 不过，依赖于 SAPI 的实现，请求体数据被保存的时候， 它可以打开另一个 php://input 数据流并重新读取。 通常情况下，这种情况只是针对 POST 请求，而不是其他请求方式，比如 PUT 或者 PROPFIND。*

而笔者本地的PHP是5.5.25版本的，所以只能读第一次。