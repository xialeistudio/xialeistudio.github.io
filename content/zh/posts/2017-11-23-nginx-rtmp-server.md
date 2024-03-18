---
slug: nginx-rtmp-server
title: 从零开始打造自己的直播服务器-Nginx安装
date: 2017-11-23 14:54:08
categories:
- Engineering
tags:
- rtmp
---
直播行业火了很长一段时间了，抛开那些复杂的实现，本系列将从零开始实现一个直播服务器。

## 功能
1. RTMP拉流(基于HLS)
2. RTMP推流(基于ffmpeg)
3. RTMP推流(基于HTTP)

## 安装Nginx
本文使用docker的ubuntu镜像作为种子机，非常干净!

文章最后会放出我写的Dockerfile，不想折腾的朋友可以直接拿过去build一个自己的镜像

以下操作在物理机ubuntu也可以进行。

1. 更新软件仓库
    ```bash
    apt-get update
    ```
2. 安装必要软件    
    ```bash
    apt-get install git gcc make wget libpcre3 libpcre3-dev openssl libssl-dev -y -q
    ```
3. 下载并解压nginx源码
    ```bash
    cd /usr/local/src
    wget http://nginx.org/download/nginx-1.12.2.tar.gz
    tar xf nginx-1.12.2.tar.gz
    ```
4. 下载nginx-rtmp-module源码
    ```bash
    git clone https://github.com/arut/nginx-rtmp-module.git
    ```
5. 开始编译安装(其他参数不是必须的，故本文略去，只添加以下参数对于一个RTMP服务器已足够)
    ```bash
    cd /usr/local/src/nginx-1.12.2
    ./configure --add-module=../nginx-rtmp-module --with-http_flv_module --with-http_mp4_module
    make
    make install
    ```
6. 修改配置文件 **/usr/local/nginx/nginx.conf**
    ```
    worker_processes  auto;
    daemon off;
    error_log  logs/error.log;
    pid        logs/nginx.pid;
    
    events {
        multi_accept on;
        worker_connections  65535;
        use epoll;
    }
    
    
    http {
        include       mime.types;
    
        log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                          '$status $body_bytes_sent "$http_referer" '
                          '"$http_user_agent" "$http_x_forwarded_for"';
    
        access_log  logs/access.log  main;
    
        sendfile        on;
        #tcp_nopush     on;
    
        #keepalive_timeout  0;
        keepalive_timeout  30;
    
        gzip  on;
    
        server {
            listen       80;
            server_name  localhost;
          
            location /stat {
              rtmp_stat all;
              rtmp_stat_stylesheet stat.xsl;
            }
    
            location /stat.xsl {
               root /usr/local/src/nginx-rtmp-module;
            }
            location /control {
              rtmp_control all;
            }
            location /hls {
              types {
                application/vnd.apple.mpegurl m3u8;
                video/mp2t ts;
              }
              root html;
              expires -1;
            }
            location ~\.flv {
              flv;
            }
            location ~\.mp4 {
              mp4;
            }
        }  
    }
    
    rtmp {
      server {
        listen 1935;
        chunk_size 4096;
        application hls {
          allow publish 127.0.0.1;
          live on;
          hls on;
          hls_path /usr/local/nginx/html/hls;
          hls_fragment 5s;
        }
      }
    }
    ```
    nginx在docker运行需要关闭daemon选项.
    **rtmp->server->application**为具体的直播应用,**hls**是我的直播应用名称，可以根据实际情况修改。
7. 启动服务器
    ```bash
    /usr/local/nginx/sbin/nginx -c /usr/local/nginx/conf/nginx.conf
    ```
    
## 安装ffmpeg
```bash
apt-get install ffmpeg
```

## 推流测试
### 推流地址
```
rtmp://localhost:1935/hls/demo
```
**hls**为上面配置的**application**名称，**demo**是直播名称，客户端使用**http://localhost/hls/demo.m3u8**进行播放

### 视频推流
```bash
ffmpeg -re -i a.mp4 -vcodec copy -f flv rtmp://localhost:1935/hls/demo
```
web中播放
```html
<video src="http://localhost/hls/demo.m3u8" controls></video>
```

### 音频推流
```bash
ffmpeg -re -i a.mp3 -acodec aac -f flv rtmp://localhost:1935/hls/demo
```
web中播放
```html
<audio src="http://localhost/hls/demo.m3u8" controls></audio>
```

### 推流与播放地址说明
1. 假设nginx配置**http端口**为**80**,**http目录为hls**,**rtmp端口**为**1935**,**application**名称为**hls**,需要播放的直播名称为**demo**
2. 推流地址**rtmp://localhost:1935/hls/demo**
3. 播放地址**http://localhost/hls/demo.m3u8**

### 重要说明
如果没有直播推流，nginx是不会产生m3u8文件的，这点需要注意!

### Docker镜像地址
[https://github.com/xialeistudio/docker-nginx-rtmp](https://github.com/xialeistudio/docker-nginx-rtmp)