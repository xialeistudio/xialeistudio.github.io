---
layout: post
title: IllegalStateException： Can not perform this action after onSaveInstanceState
date: 2014-11-13 11:11:36.000000000 +08:00
type: post
published: true
status: publish
categories:
- engineering
---
今天使用Fragment的时候，出现了这个错误 IllegalStateException: Can not perform this action after onSaveInstanceState。查看一下控制台，发现是FragmentManager的commit()方法报错的，看字面意思应该是

*onSaveInstanceState这个方法之后不能处理这个操作（指commit()）。*

因为onSaveInstanceState
方法是在该Activity即将被销毁前调用，来保存Activity数据的，如果在保存完状态后再给它添加Fragment就会出错。解决办法就是把commit（）方法替换成 commitAllowingStateLoss()就行了，其效果是一样的。