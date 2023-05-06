---
title: log4go尝鲜
date: 2017-11-21 17:06:16
categories:
- Engineering
---
# 序言
日志系统对于软件是必不可少的，可以帮助我们记录关键信息，后期处理问题的时候会很方便。业界有很多出名的日志库，log4日志库相信每个人都不陌生，像log4j之于Java，log4php之于PHP等等。其实golang也有很多的log4实现，本文要使用的是**alecthomas**实现的版本。

# 项目地址
[https://github.com/alecthomas/log4go](https://github.com/alecthomas/log4go)

# 安装
```bash
go get github.com/alecthomas/log4go
```

# 使用代码配置
1. 新建golang项目
2. 在项目根目录下新建*main.go*文件，代码如下

    ```go
    package main
    import "github.com/alecthomas/log4go"
    
    func main() {
        defer log4go.Close()
        log4go.AddFilter("stdout", log4go.DEBUG, log4go.NewConsoleLogWriter()) // DEBUG级别+打印到控制台
        log4go.AddFilter("file", log4go.INFO, log4go.NewFileLogWriter("test.log", true)) // INFO级别+输出到文件，并开启rotate
        log4go.Debug("这是DEBUG日志") // 输出测试
        log4go.Info("这是INFO日志") // 输出测试
    }
    ```
    *如果程序是守护进程，此处不用调用log4go.Close，因为log4go使用协程异步写入日志，此处可以调用log4go.Close也可以Sleep来实现写入，下文会有Sleep测试*
3.  `go run main.go`
4. 此时可以看到终端输出，还可以发现项目目录下生成了*test.log*文件

    ```
    [17:11:35 CST 2017/11/21] [DEBG] (main.main:9) 这是DEBUG日志
    [17:11:35 CST 2017/11/21] [INFO] (main.main:10) 这是INFO日志
    ```

5. 重新执行时可以发现**test.log**被rotate到了**test.log.1**

# 使用配置文件
log4go支持使用xml来作为配置文件
1. 在项目根目录新建**log4go.xml**

    ```xml
    <logging>
        <filter enabled="true">
            <tag>stdout</tag>
            <type>console</type>
            <level>DEBUG</level>
        </filter>
        <filter enabled="true">
            <tag>file</tag>
            <type>file</type>
            <level>INFO</level>
            <property name="filename">test.log</property>
            <property name="rotate">true</property>
            <property name="maxlines">2</property>
            <property name="daily">true</property>
        </filter>
    </logging>
    ```
2. 添加了**console**和**file**两个filter，跟代码添加其实是一样的，不同的是xml的可配置性更高。具体配置参数需要查看log4go对应的go源文件
3. 修改**main.go**

    ```go
    package main
    
    import (
        "github.com/alecthomas/log4go"
        "time"
    )
    
    func main() {
        log4go.LoadConfiguration("log4go.xml")
        log4go.Debug("这是DEBUG日志")
        log4go.Info("这是INFO日志")
        time.Sleep(time.Second)
    }
    ```
4. 运行程序，终端依旧正确输出，同时也会生成*test.log*

# 后记
log4go良好的设计带来了简洁又强大的使用体验，更多的使用细节以及更多的logger类型等待读者去发掘与实现，本文只做一个简单的介绍，即便如此也应该能够应付大部分场景了。