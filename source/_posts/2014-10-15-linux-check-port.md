---
layout: post
title: linux检查端口占用
date: 2014-10-15 21:49:22.000000000 +08:00
type: post
published: true
status: publish
categories:
- linux
tags:
- shell
- netstat
meta:
  _edit_last: '1'
  views: '3127'
  _thumbnail_id: '174'
  _wp_old_slug: linux%e6%a3%80%e6%9f%a5%e5%93%aa%e4%b8%aa%e7%ab%af%e5%8f%a3%e8%a2%ab%e5%8d%a0%e7%94%a8%ef%bc%8c%e5%b9%b6%e6%9d%80%e6%ad%bb%e8%af%a5%e8%bf%9b%e7%a8%8b
---
```bash
netstat -lnp | grep 80
```