---
title: 使用docker-composer部署nodejs应用
date: 2017-11-01 16:28:23
categories:
- Engineering
---
## 新建Dockerfile
在应用目录下新建**Dockerfile**
```dockerfile
FROM node:8
WORKDIR /usr/src/app
ADD . /usr/src/app
RUN npm install --registry=https://registry.npm.taobao.org
USER node
EXPOSE 8080
```
8080 端口请根据实际情况调整。建议大于1024，否则使用**node**用户启动应用时可能权限不足

## 新建docker-compose.yml
在应用目录下新建**docker-compose.yml**
```yaml
version: "2"
services:
  jsconsole:
    build: .
    volumes:
      - .:/usr/src/app
      - /usr/src/app/node_modules
    ports:
      - "127.0.0.1:8081:8080"
    command: "npm start"
    restart: always
```
**127.0.0.1:8081**是**宿主机IP和端口**，我前端采用了**nginx**做反向代理。如果是直接提供公网服务的话把**127.0.0.1**去掉
## 构建镜像
在应用根目录下执行
```bash
docker-compose build
```
## 构建并运行
在应用根目录下执行**-d**是后台执行
```bash
docker-compose up -d
```
