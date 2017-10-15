---
layout: post
title: ReactRouter不在组件中进行导航
date: 2016-05-17 12:41:35.000000000 +08:00
type: post
published: true
status: publish
categories:
- react
tags:
- front-end
- react
- react router
meta:
  _edit_last: '1'
  _wp_old_slug: reactrouter%e4%b8%8d%e5%9c%a8%e7%bb%84%e4%bb%b6%e4%b8%ad%e8%bf%9b%e8%a1%8c%e5%af%bc%e8%88%aa
  views: '480'
---
项目使用了**Flux+React Router**架构，有一些需要操作路由的地方是放在Action层的，比如登录之类，但是Action层不是React组件，需要操作路由的话有点麻烦。   

当然最终还是有一个办法的，利用**window.location.href=**，但是既然用了react，再用这种导航模式未免不妥。   

查看react router源码发现,**hashHistory,browseHistory**中有**push**方法，经过测试之后可行。

```javascript
import {hashHistory} from 'react-router';
hashHistory.push('/login');
```