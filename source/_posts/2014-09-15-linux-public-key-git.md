---
layout: post
title: linux利用ssh公钥部署git代码
date: 2014-09-15 09:18:01.000000000 +08:00
type: post
published: true
status: publish
categories:
- backend
- linux
---
## 背景
阿里云的使用门槛降低，直接导致了很多人优先使用VPS而不是以前的虚拟主机，毕竟虚拟主机存在诸多限制。阿里云犹如一台全新的服务器，所有软件都要自己安装。作为一个写PHP的，代码部署就略麻烦了，以前使用FTP的时候很方便部署，但是不适合长期开发（因为没有版本控制），所以使用GIT会很方便。
## 问题
在windows开发机上使用https方式进行git操作是没问题的，但是在linux上进行git操作的时候就会出错误，会让你输入帐号密码，就算是对的帐号密码也不行。这种情况下需要使用 ssh 方式进行GIT。
## 解决方法
1. 生成密钥 在终端下输入 `ssh-keygen -t rsa`
2. 接下来的询问全部直接按回车
3. 最后得到了两个文件：id_rsa和id_rsa.pub
4. cat ~/.ssh/id_rsa.pub
5. 将显示的内容全部复制下来
6. 进入你的git网站，比如oschina的git
7. 添加ssh公钥
8. 保存
9. enjoy!