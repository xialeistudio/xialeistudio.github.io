---
slug: android-asynctask-demo
title: android AsyncTask示例
date: 2016-06-23 23:12:24.000000000 +08:00
categories:
- Engineering
---

android实现异步的方法有很多种，本文只介绍用的比较多的AsyncTask。从类名就可以看出来该类是专为异步而生，API也很简单。

## AsyncTask接口原型

```java
public abstract class AsyncTask<Params, Progress, Result> {
...
}
```

该类是个抽象类，有三个泛型参数，说明如下：
+ Params	任务参数类型，比如加载网络图片时，这里传入String
+ Progress	更新进度时参数类型，一般传入Integer
+ Result	执行结果类型，比如加载网络图片时，结果为Bitmap

该类的主要方法如下：
+ doInBackground(Params... params)	非主线程	执行异步任务，params为声明类时的泛型
+ onPreExecute	主线程	准备执行异步任务时调用
+ onPostExecute(Result result)	主线程	异步任务执行完毕时调用，result为声明类时的泛型
+ onProgressUpdate(Progress... values)	主线程	任务进度有更新时调用，values为声明类时的泛型
+ publishProgress(Progress... values)	非主线程	更新异步任务进度，此方法一般在doInBackground中调用

## 示例
本文将使用一个图片批量下载程序作为示例   
根据需求可以确定，任务参数是String类型，进度是Integer类型，执行结果是List<Bitmap>类型，项目代码如下：

### 布局文件

```xml
<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <LinearLayout
        android:id="@+id/contentView"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical">

        <Button
            android:id="@+id/btnStart"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_gravity="center_horizontal"
            android:onClick="loadImage"
            android:text="@string/start" />

        <ProgressBar
            android:id="@+id/progressBar"
            style="?android:attr/progressBarStyleHorizontal"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginTop="16dp"
            android:progress="0"
            android:visibility="gone" />
    </LinearLayout>

</ScrollView>
```

### MainActivity.java

```java
package com.ddhigh.asynctaskdemo;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.AsyncTask;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ProgressBar;

import java.io.BufferedInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.URL;
import java.net.URLConnection;
import java.util.ArrayList;
import java.util.List;

public class MainActivity extends AppCompatActivity {

    private ProgressBar mProgressBar;
    private LinearLayout mLinearLayout;
    private final String[] urls = {
            "http://n.sinaimg.cn/news/crawl/20160623/rGdP-fxtmwep2657001.jpg",
            "http://n.sinaimg.cn/news/crawl/20160623/6mXQ-fxtmweh2331418.jpg",
            "http://n.sinaimg.cn/news/crawl/20160623/z6Io-fxtmwep2657003.jpg",
            "http://n.sinaimg.cn/news/crawl/20160623/U9QQ-fxtmweh2331421.jpg",
            "http://n.sinaimg.cn/news/crawl/20160623/BIdM-fxtmweh2331423.jpg"
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        mProgressBar = (ProgressBar) findViewById(R.id.progressBar);
        mLinearLayout = (LinearLayout) findViewById(R.id.contentView);

    }

    public void loadImage(View view) {
        ImageTask imageTask = new ImageTask();
        imageTask.execute(urls);
    }

    private class ImageTask extends AsyncTask<String, Integer, List<Bitmap>> {
        @Override
        protected void onPreExecute() {
            mProgressBar.setVisibility(View.VISIBLE);
            mProgressBar.setMax(urls.length);
        }

        @Override
        protected List<Bitmap> doInBackground(String... params) {
            List<Bitmap> list = new ArrayList<>();
            int i = 0;
            for (String url : params) {
                URLConnection connection;
                Bitmap bitmap;
                InputStream inputStream;
                try {
                    connection = new URL(url).openConnection();
                    inputStream = connection.getInputStream();
                    BufferedInputStream bufferedInputStream = new BufferedInputStream(inputStream);
                    bitmap = BitmapFactory.decodeStream(bufferedInputStream);
                    inputStream.close();
                    bufferedInputStream.close();
                    list.add(bitmap);
                    publishProgress(++i);
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
            return list;
        }

        @Override
        protected void onPostExecute(List<Bitmap> bitmaps) {
            for (Bitmap bitmap : bitmaps) {
                ImageView imageView = new ImageView(MainActivity.this);
                ViewGroup.LayoutParams layoutParams = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT);
                imageView.setLayoutParams(layoutParams);
                imageView.setImageBitmap(bitmap);
                mLinearLayout.addView(imageView);
            }
        }

        @Override
        protected void onProgressUpdate(Integer... values) {
            mProgressBar.setProgress(values[0]);
        }
    }
}
```

使用AsyncTask的核心在于重写相应方法实现自己的逻辑即可。

### 源码
[Android-AsyncTaskDemo](https://github.com/xialeistudio/Android-AsyncTaskDemo)