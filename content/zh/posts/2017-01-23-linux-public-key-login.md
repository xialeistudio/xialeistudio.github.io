---
slug: linux-public-key-login
date: 2017-01-23
title: 使用公钥登录Linux
categories:
- Engineering
---
服务器密码往往是随机字符串，难以记忆，通过配置公钥登录的方式来进行登录。
## 准备
+ 服务器A 192.168.1.2 客户机
+ 服务器B 192.168.1.3 服务器
## 配置

1. 登录**192.168.1.2**，终端执行
```bash
ssh-keygen -t rsa
```
2. 复制**~/.ssh/id_rsa.pub**文件的内容
3. 在服务器上添加公钥，登录**192.168.1.3**，终端执行
```bash
echo 刚才复制的内容 >> ~/.ssh/authorized_keys
```
## 测试
登录**192.168.1.2**，终端执行
```bash
ssh 192.168.1.3
```
首次登录的时候会进行公钥认证，输入**yes**即可。