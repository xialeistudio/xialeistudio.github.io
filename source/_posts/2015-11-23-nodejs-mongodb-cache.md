---
layout: post
title: nodejs mongodb 缓存模块
date: 2015-11-23 12:04:03.000000000 +08:00
type: post
published: true
status: publish
categories:
- open-source-projects
tags:
- nodejs
- npm
meta:
  _edit_last: '1'
  _oembed_7eef88cc50cad73e0b3bc29ff9f96853: "{{unknown}}"
  _thumbnail_id: '561'
  _wp_old_slug: npmnodejs-mongodb-%e7%bc%93%e5%ad%98%e6%a8%a1%e5%9d%97
  views: '511'
---
## 项目地址
[https://github.com/xialeistudio/mongodb-cache](https://github.com/xialeistudio/mongodb-cache)
## 项目说明
基于mongodb的nodejs缓存模块
## 使用

```bash
npm install xl-cache --save
```

```javascript
var cache = require('xl-mongodb-cache');
```
+ 连接服务器

```javascript
cache.connect('mongodb://localhost:27017/app');
```

+ 写入缓存

```javascript
cache.set(key, value, duration).then(function(data) {
  console.log(data);
}).catch(console.error);
```

+ 读取缓存

```javascript
cache.get(key).then(function(data) {
  console.log(data);
}).catch(console.error);
```

+ 删除缓存

```javascript
cache.remove(key).then(function(data) {
  console.log(data);
}).catch(console.error);
```