---
slug: react-router-navigation-outside-of-components
title: ReactRouter不在组件中进行导航
date: 2016-05-17 12:41:35.000000000 +08:00
categories:
- Engineering
---
项目使用了**Flux+React Router**架构，有一些需要操作路由的地方是放在Action层的，比如登录之类，但是Action层不是React组件，需要操作路由的话有点麻烦。   

当然最终还是有一个办法的，利用**window.location.href=**，但是既然用了react，再用这种导航模式未免不妥。   

查看react router源码发现,**hashHistory,browseHistory**中有**push**方法，经过测试之后可行。

```javascript
import {hashHistory} from 'react-router';
hashHistory.push('/login');
```