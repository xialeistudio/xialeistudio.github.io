---
layout: post
title: angularjs遍历空数组&索引数组
date: 2014-11-14 21:00:41.000000000 +08:00
type: post
published: true
status: publish
categories:
- frontend
- angularjs
---
今天做开发时发现控制老是报错，虽然不影响使用，但是作为有那么一点“强迫症”的我来说，无法忍受。通过调试发现是ng-repeat对一个空数组遍历出错，另外，['ab','cd','ad']这样只有值没有键的数组也会遍历出错。

## 解决办法
```html
<li class="media" ng-repeat="item in comments track by $index">
    <div class="media-body">
        <strong></strong>
<p> <br />
<time></time>
<br />
<span ng-if="item.comment_author_url.length>0">
            <i class="fa fa-globe"></i> 
            <a href="" target="_blank"></a>
            </span>
        </p>
    </div>
</li>
```

特别注意**track by $index**