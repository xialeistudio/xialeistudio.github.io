---
layout: post
title: 百度推送收到消息时带参数启动activity
date: 2016-02-19 17:09:21.000000000 +08:00
type: post
published: true
status: publish
categories:
- engineering
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