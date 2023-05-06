---
layout: post
title: jquery插件写法
date: 2014-09-06 20:08:22.000000000 +08:00
type: post
published: true
status: publish
categories:
- Engineering
---
## 项目地址
[http://xialeistudio.github.io/search/](http://xialeistudio.github.io/search/)

jquery插件确实是数不胜数，只要你用心找，肯定能找得到!

但是一些小功能想自己写，找的话估计时间还长些，本文简单开发一个 基于jquery的获取url查询字符串的 小插件。

插件的模版（$.extend扩展jquery内置方法)

```javascript
(function($) {
  $.x_search = function(_name,target) { //x_search是插件名字,_name、target是参数
  };
})(jQuery);
```

```javascript

/** 
 * $.x_search 
 * @extends jquery 2.1.1(基于该版本开发，其他版本自测) 
 * @fileOverview 获取url queryString 
 * @author xialeistudio 
 * @email 1065890063@qq.com 
 * @site www.ddhigh.com 
 * @version 0.0.1 
 * @date 2014-08-12 
 * @license MIT 
 * @example 
 * 获取当个Key 
 * $.x_search('name'); 
 * 获取所有 
 * $.x_search(); 
 */ (function($) { 
  $.x_search = function(_name,target) { 
    if(typeof target == 'undefined'){ 
      target =  window.location.search; 
    } 
    if (typeof _name == 'undefined') { 
      //所有 
      var query =target.substr(1, window.location.search.length-1).split('&'); 
      var data = []; 
      for (var i = 0; i < query.length; i++) { 
        var tmp = query[i].split('='); 
        data.push({ 
          key: tmp[0], 
          data: decodeURIComponent(tmp[1]) 
        }); 
      } 
      return data; 
    } 
    else { 
      //指定Key 
      try { 
        var regex = new RegExp(_name+'=([^&]+)?'); 
        return decodeURIComponent(target.match(regex)[1]); 
      } 
      catch (e) { 
        return null; 
      } 
    } 
  }; })(jQuery);
```
