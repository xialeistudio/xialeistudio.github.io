---
layout: post
title: SVN命令行提交“--This line, and those below, will be ignored--”
date: 2014-12-29 17:35:47.000000000 +08:00
type: post
published: true
status: publish
categories:
- linux
tags:
- subversion
meta:
  _edit_last: '1'
  _thumbnail_id: '332'
  views: '2130'
  _wp_old_slug: svn%e5%91%bd%e4%bb%a4%e8%a1%8c%e6%8f%90%e4%ba%a4-this-line-and-those-below-will-be-ignored-%e7%9a%84%e8%a7%a3%e5%86%b3
---
今天phpstorm突然抽风，导致svn不能用，无奈只好用svn命令来提交。

```bash
svn commit -m "init"
```

结果报错

```bash
--This line, and those below, will be ignored--

M webroot/thatyear/js/main.js
~ 
~ 
~ 
~ 
~ 
~ 
~ 
~ 
~ 
"svn-commit.2.tmp" 4L, 83C
```

直接保存发现会出现以下结果

```bash
Log message unchanged or not specified
(a)bort, (c)ontinue, (e)dit:
```

输入**c**提交   
*我这是设置了SVN提交默认编辑器的时候才会这样，默认是不会设置的。*按以下操作设置提交的编辑器   

```bash
vi ~/.subversion/config 
```

找到[helpers]下的 editor-cmd 节，更改为vi即可   

```bash
[helpers]
editor-cmd = /usr/bin/vi
```