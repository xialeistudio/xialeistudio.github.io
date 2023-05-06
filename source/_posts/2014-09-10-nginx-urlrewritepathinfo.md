---
layout: post
title: nginx url重写和pathinfo配置
date: 2014-09-10 12:13:47.000000000 +08:00
type: post
published: true
status: publish
categories:
- Engineering
---
nginx近年来的上涨趋势确实挺快的，但是apache作为老牌HTTP服务器，拥有的生态圈是nginx比不上的。一个最简单的例子，URL重写，apache的话利用无所不能的.htaccess文件就可以了。nginx还要改主配置文件。

## URL重写配置
### 主配置文件

```
location /
{
  if (!-e $request_filename) {
    rewrite ^/(.*)$ /index.php?$1 last;
  }
}
```

*if和(中间要有括号*,url重写这里就配置完了。
## pathinfo配置
nginx原生是不支持pathinfo的，但是通过配置fastcgi参数可以达到效果
### 主配置文件

```
location ~ [^/]\.php(/|$)
{
  # comment try_files $uri =404; to enable pathinfo
  #try_files $uri =404;
  fastcgi_pass  unix:/tmp/php-cgi.sock;
  fastcgi_index index.php;
  include fastcgi.conf;
  include pathinfo.conf;
}
```

### fastcgi.conf

```
fastcgi_param  SCRIPT_FILENAME    $document_root$fastcgi_script_name;
fastcgi_param  QUERY_STRING       $query_string;
fastcgi_param  REQUEST_METHOD     $request_method;
fastcgi_param  CONTENT_TYPE       $content_type;
fastcgi_param  CONTENT_LENGTH     $content_length;
fastcgi_param  SCRIPT_NAME        $fastcgi_script_name;
fastcgi_param  REQUEST_URI        $request_uri;
fastcgi_param  DOCUMENT_URI       $document_uri;
fastcgi_param  DOCUMENT_ROOT      $document_root;
fastcgi_param  SERVER_PROTOCOL    $server_protocol;
fastcgi_param  HTTPS              $https if_not_empty;
fastcgi_param  GATEWAY_INTERFACE  CGI/1.1;
fastcgi_param  SERVER_SOFTWARE    nginx/$nginx_version;
fastcgi_param  REMOTE_ADDR        $remote_addr;
fastcgi_param  REMOTE_PORT        $remote_port;
fastcgi_param  SERVER_ADDR        $server_addr;
fastcgi_param  SERVER_PORT        $server_port;
fastcgi_param  SERVER_NAME        $server_name;
# PHP only, required if PHP was built with --enable-force-cgi-redirect
fastcgi_param  REDIRECT_STATUS    200;
```

### pathinfo.conf

```
fastcgi_split_path_info ^(.+?\.php)(/.*)$;
set $path_info $fastcgi_path_info;
fastcgi_param PATH_INFO       $path_info;
try_files $fastcgi_script_name =404;
```

## 结语
从这些配置可以看出来，nginx的可定制性还是很强的，同样的，apache下的.htaccess文件，经过一些改写也能在nginx上成功运行~