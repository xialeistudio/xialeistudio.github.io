---
layout: post
title: SVN命令行提交“--This line, and those below, will be ignored--”
date: 2014-12-29 17:35:47.000000000 +08:00
type: post
published: true
status: publish
categories:
- devtools
tags:
- svn
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