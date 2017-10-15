---
layout: post
title: 解决wordpress d8主题使用七牛镜像插件后无法评论的问题
date: 2014-11-01 13:46:44.000000000 +08:00
type: post
published: true
status: publish
categories:
- wordpress
tags:
- comment
- qiniu
meta:
  _edit_last: '1'
  views: '3563'
  _thumbnail_id: '216'
  _wp_old_slug: wordpress-d8-theme-qiniu
---
上午有热心的网友给我反映说评论功能出bug了，初步查看是七牛出了问题，利用chrome的开发者工具可以查看请求。
![示意图](https://og5r5kasb.qnssl.com/wp-content/uploads/2014/11/blob3.png)   
PS：这张图是今天截的，所以域名是正常的，昨天实际上请求的是 static.ddhigh.com (本站的CDN域名)。   
查看HTTP请求发现整站就请求了一个jquery文件，但是这个文件比较大有140K，查看源代码发现评论的代码已经合并在里面了。   
![示意图](https://og5r5kasb.qnssl.com/wp-content/uploads/2014/11/blob4.png)   
按照以上步骤可以查看到评论时执行的脚本，当然这里的域名已经修复了。

278行，昨天的是 

```
url:window._deel.url+"/ajax/comment.php"
```

在控制台输入

```javascript
console.log(_deel);
```

![示意图](https://og5r5kasb.qnssl.com/wp-content/uploads/2014/11/blob5.png)

域名是CDN域名，所以ajax请求实际上被提交到**七牛**去了。
## 修正方法
利用ssh工具连接你的服务器（不是七牛），找到对应的jquery文件278行，改成你的站点域名（如本站的www.ddhigh.com）,更新下缓存即可。