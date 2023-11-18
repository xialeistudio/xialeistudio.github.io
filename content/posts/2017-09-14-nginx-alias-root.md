---
slug: nginx-alias-root
date: 2017-09-14
title: Nginx alias和root指令
categories:
- Engineering
---
Nginx的root指令相信大家用的都挺多，用来指定document_root，但是如果是针对特定path的请求才启用的话，root指令显得不好用
```
location /web {
    root /home/wwwroot/site1;
}
```
访问 *http://demo.com/web/a.js*的时候,nginx会去查找*/home/wwwroot/site1/web/a.js*，一般就会404了。因为文件是放在site1目录下的。
这时候就需要alias指令了。
```
location /web/{
    alias /home/wwwroot/site1/;
}
```
访问 *http://demo.com/web/a.js*的时候,nginx会去查找*/home/wwwroot/site1/a.js*。

注意 alias location末尾斜杠以及alias的末尾斜杠