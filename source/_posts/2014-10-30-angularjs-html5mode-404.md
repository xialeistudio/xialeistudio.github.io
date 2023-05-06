---
layout: post
title: 解决 angularjs html5Mode 404的问题
date: 2014-10-30 13:02:01.000000000 +08:00
type: post
published: true
status: publish
categories:
- Engineering
---
采用location的html5Mode之后，链接是正常的，但是刷新的时候会404，此时就需要后端服务器配置URL重写了。

## nginx 配置

```
location / {
  try_files $uri $uri/ /index.html$is_args$args;
}
```

这样子就可以将所有不是文件夹且不是文件的请求转发到index.html。