---
layout: post
title: 百度推送收到消息时带参数启动activity
date: 2016-02-19 17:09:21.000000000 +08:00
type: post
published: true
status: publish
categories:
- android
tags:
- android
- 百度推送
meta:
  _edit_last: '1'
  _thumbnail_id: '241'
  _wp_old_slug: "%e7%99%be%e5%ba%a6%e6%8e%a8%e9%80%81%e6%94%b6%e5%88%b0%e6%b6%88%e6%81%af%e6%97%b6%e5%b8%a6%e5%8f%82%e6%95%b0%e5%90%af%e5%8a%a8activity"
  views: '1016'
---
一般来说，在BPushReceiver的onNotificationClicked或者onMessage方法收到推送消息后会去启动一个activity。此时整个应用有以下几种状态：
+ 应用进程不存在
+ 应用进程存在，但是不在前台
+ 应用进程存在，在前台

在BPushReceiver的onNotificationClicked或者onMessage方法中使用Intent来启动activity：

```java
Intent intent = new Intent();
intent.setClass(context.getApplicationContext(), MainActivity.class);
intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_SINGLE_TOP);
if (url != null && !url.isEmpty()) {
    Bundle bundle = new Bundle();
    bundle.putString("url", url);
    intent.putExtras(bundle);
}

Log.d(TAG, "start app");
context.getApplicationContext().startActivity(intent);
```

需要注意的是，针对不同的应用状态，MainActivity中触发的方法也不同：
+ 应用进程不存在时,onCreate被调用
+ 应用进程存在，不管是不是在前台，onNewIntent被调用

针对以上状态，合理的使用onCreate和onNewIntent就可以在任何时候呆参数启动APP了。