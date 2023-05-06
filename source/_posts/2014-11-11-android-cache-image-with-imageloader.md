---
layout: post
title: android使用ImageLoader缓存图片
date: 2014-11-11 12:10:17.000000000 +08:00
type: post
published: true
status: publish
categories:
- Engineering
---
缓存和异步是两个极大提升用户体验的好东西，android加载图片时的开销还是挺大的，要是不做缓存同步加载，网速不给力的情况下，等个十几秒是有可能的。

今天要说的是一个叫做ImageLoader的库

GITHUB:[https://github.com/nostra13/Android-Universal-Image-Loader](https://github.com/nostra13/Android-Universal-Image-Loader)

使用这个库有以下几步：
+ 导入libs目录
+ 声明自己的MyApplication类（继承Application）
+ 在onCreate()方法中

```java
public void onCreate() {
        super.onCreate();
        DisplayImageOptions options = new DisplayImageOptions.Builder()  
        .cacheInMemory()  //缓存在内存中
        .cacheOnDisc()  //磁盘缓存
        .build();  
        ImageLoaderConfiguration config2 = new ImageLoaderConfiguration.Builder(this)
        .defaultDisplayImageOptions(options)
          .threadPriority(Thread.NORM_PRIORITY - 2)
          .denyCacheImageMultipleSizesInMemory()
          .discCacheFileNameGenerator(new Md5FileNameGenerator())
          .tasksProcessingOrder(QueueProcessingType.LIFO)
          .build();
        ImageLoader.getInstance().init(config2);
}
```

+ 在要加载图片的地方使用

```java
DisplayImageOptions options = new DisplayImageOptions.Builder()
				.cacheInMemory() // 缓存用
				.cacheOnDisc()
				.bitmapConfig(Bitmap.Config.RGB_565)//防止溢出
				.displayer(new RoundedBitmapDisplayer(139)) // 图片圆角显示，值为整数
				.build();
ImageLoader.getInstance().displayImage(url, avatar, options);
```

其中 url 是图片URL地址，avatar为ImageView,options为动态配置，这里加了一个防止溢出的参数。

好了，使用起来是不是很简单呢~我们压根不用操心异步和缓存的问题了