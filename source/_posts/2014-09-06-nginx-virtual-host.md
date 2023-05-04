---
layout: post
title: nginx虚拟主机配置
date: 2014-09-06 20:02:20.000000000 +08:00
type: post
published: true
status: publish
categories:
- engineering
---

最近服务器上用的环境是lnmp，之前一直在用apache，配置虚拟主机也是很方便的。今天查资料发现Nginx的虚拟主机配置更加简单。


```
server {

    listen       80;

    server_name  domain1;

    location / {

        root   html/domain1;

        index  index.html index.htm index.php;

    }

    location ~ \.php$ {

    root    html/domain1;

    fastcgi_pass   127.0.0.1:9000;

    fastcgi_index  index.php;

    fastcgi_param  SCRIPT_FILENAME  $document_root$fastcgi_script_name;

    include    fastcgi_params;

        }

}

server {

    listen    80;

    server_name  domain2;

    location / {

        root   html/domain2;

        index  index.html index.htm index.php;

        }

    location ~ \.php$ {

        root    html/domain2;

        fastcgi_pass   127.0.0.1:9000;

        fastcgi_index  index.php;

        fastcgi_param  SCRIPT_FILENAME  $document_root$fastcgi_script_name;

        include    fastcgi_params;

    }

}
```

保存之后，执行 

```bash
nginx -s reload
```