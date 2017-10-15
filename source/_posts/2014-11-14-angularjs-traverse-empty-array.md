---
layout: post
title: angularjs遍历空数组&索引数组
date: 2014-11-14 21:00:41.000000000 +08:00
type: post
published: true
status: publish
categories:
- angularjs
tags:
- ng-repeat
meta:
  _edit_last: '1'
  _thumbnail_id: '218'
  views: '9730'
  _wp_old_slug: ng-repeat%e9%81%8d%e5%8e%86%e7%a9%ba%e6%95%b0%e7%bb%84%e6%88%96%e6%97%a0%e9%94%ae%e5%90%8d%e7%9a%84%e6%95%b0%e7%bb%84%e9%97%ae%e9%a2%98%e7%9a%84%e8%a7%a3%e5%86%b3
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