---
title: Java中加载文件的几种方式
date: 2020-02-01 12:00:00
categories:
- Engineering
---

在Java程序中加载外部文件有多中方式，每种方式也存在区别，本文将理清这些加载方式之间的区别。

## 文件IO方式

```java
package org.xialei.example.resource;

import java.io.File;
import java.io.IOException;

public class Main {
    public static void main(String[] args) throws IOException {
        File file = new File("app.properties");
        System.out.println(file.getAbsolutePath());
    }
}
```

常见的读取方式，使用该方式读取文件时规则如下：

> 如果传入的是绝对路径，则以系统根目录作为绝对路径的起点。
>
> 如果传入的是相对路径，则以当前工作目录作为起点。

本例中，运行`java`命令的目录即为工作目录，app.properties从工作目录开始查找。

## Class.getResourceAsStream

```java
package org.xialei.example.resource;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

public class Main {
    public static void main(String[] args) throws IOException {
        try (InputStream is = Main.class.getResourceAsStream("app.properties")) {
            Properties properties = new Properties();
            properties.load(is);
            System.out.println(properties.getProperty("name"));
        }
    }
}
```

使用该方式读取文件时规则如下：

> 如果传入的是相对路径，则以当前class所在的包作为起点。
>
> 如果传入的是绝对路径，则以classpath的根目录为起点。

+ `Main.class.getResourceAsStream("app.properties")` 会读取`/org/xialei/example/resource/app.properties`文件。
+ `Main.class.getResourceAsStream("/app.properties")`会读取"classpath:/app.properties"文件

## ClassLoader.getResourceAsStream

```java
package org.xialei.example.resource;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

public class Main {
    public static void main(String[] args) throws IOException {
        try (InputStream is = Main.class.getClassLoader().getResourceAsStream("org/xialei/example/resource/app.properties")) {
            Properties properties = new Properties();
            properties.load(is);
            System.out.println(properties.getProperty("name"));
        }
    }
}
```

使用该方式时规则如下:

> 使用classpath根目录作为起点。

本例中，`org/xialei/example/resource/app.properties`就是从classpath根目录进行查找的。

![0.jpeg](https://static.ddhigh.com/blog/2019-10-22-102654.jpg)