---
title: Go语言程序设计
date: 2021-02-25 11:13:02
categories:
- backend
- go
---

## Go语言概述

### 语言历史

Go语言也称为Golang，是由Google公司开发的一种静态强类型、编译型、语言原生支持并发、具有垃圾回收功能的编程语言。起源于2007年，并在2009年正式对外发布。Go语言是非常年轻的一门语言，它的主要目标是“兼具 Python 等动态语言的开发速度和 C/C++等编译型语言的性能与安全性”。

Go语言是编程语言设计的又一次尝试，是对类C语言的重大改进，它不但能让你访问底层操作系统，还提供了强大的网络编程和并发编程支持。Go语言的用途众多，可以进行网络编程、系统编程、并发编程等等。

Go语言的推出，旨在不损失应用程序性能的情况下降低代码的复杂性，具有“部署简单、并发性好、语言设计良好、执行性能好”等优势。

Go语言有时候被描述为“21世纪的C语言”。Go 从C语言继承了相似的表达式语法、控制流结构、基础数据类型、调用参数传值、指针等很多思想，还有C语言编译后的运行效率。

Go语言没有类和继承的概念，通过组合来实现代码复用，同时它通过接口（interface）的概念来实现多态性。所以Go语言的面向对象编程和传统面向对象语言（如C++和Java）并不相同。

Go语言有一个吉祥物，在会议、文档页面和博文中，大多会包含下图所示的 Go Gopher，这是才华横溢的插画家 Renee French 设计的，她也是 Go 设计者之一 Rob Pike 的妻子。

![img](https://static.ddhigh.com/blog/2021-02-25-111457-2.jpg)

### 语言特性

**语法简单**

Go语言的设计思想类似Unix的“少即是多”。Go语言的语法规则严谨，没有歧义，这使得Go语言简单易学。Go语言保留了指针，但通常情况下禁止指针运算（保留unsafe包操作指针的能力）。此外，Go语言还内置切片和字典，在保留运行性能的同时也提高了开发效率。

**语言级别支持并发**

主流的并发模型有多进程模型、多线程模型。和主流多并发模型不同，Go语言采用了基于CSP的协程实现，并且在运行时做了更深度的优化处理。这使得语言级别上并发编程变得极为容易，无须处理回调、也无需关注线程切换，只需要添加一个go关键字即可。

“通过通信去共享内存，而不是通过共享内存去通信”，go语言内置的channel数据结构配合go关键字实现并发通信及控制，这对于需要考虑内存可见性等问题的多线程模型来说，是一个良好的解决方案。

**高效的垃圾回收**

Go语言的每次升级，垃圾回收器必然是核心组件里修改最多的部分。从并发清理，到降低STW时间，直到Go的1.5版本实现并发标记，逐步引入三色标记和写屏障等等，都是为了能让垃圾回收在不影响用户逻辑的情况下更好地工作。从最开始的秒级别STW到目前的微秒级STW，Go语言开发团队一直在垃圾回收方面进行努力。

**静态链接**

静态编译的好处显而易见。将运行时、依赖库直接打包到可执行文件内部，简化了部署和发布操作，无须事先安装运行环境和下载诸多第三方库。虽然相比动态编译增加了可执行文件的大小，但是省去了依赖库的管理。随着微服务和容器化的发展，这也成为了Go语言的杀手锏之一，一个二进制文件即可运行服务。

**标准库**

功能完善、质量可靠的标准库为编程语言提供了有力的支持。在不借助第三方扩展的情况下，就可完成大部分基础功能开发，这大大降低了学习和使用成本。

Go语言标准库可以说极为丰富。其中值得称道的是net/http，仅须简单几条语句就能实现一个高性能 Web Server。

**工具链**

完整的工具链对于项目开发极为重要。Go语言在此做得相当不错，无论是编译、格式化、错误检查、帮助文档，还是第三方包下载、更新都有对应的工具。

值得一提的gofmt工具，为了解决开发者经常遇到的“代码风格不统一”的难题，官方直接通过gofmt指定一套标准，可以看出go语言在工程方面确实解决了许多实际问题。

此外Go语言内置完整测试框架，其中包括单元测试、性能测试、代码覆盖率、数据竞争，以及用来调优的pprof，这些都是保障代码能正确而稳定运行的必备利器。

### Go语言应用场景

Go 语言从发布1.0版本以来备受众多开发者关注并得到广泛使用，Go 语言的简单、高效、并发特性吸引了众多传统语言开发者的加入，而且人数越来越多。

鉴于Go语言的特点和设计的初衷，Go语言作为服务器编程语言，很适合处理日志、数据打包、虚拟机处理、文件系统、分布式系统、数据库代理等；网络编程方面，Go语言广泛应用于Web应用、API应用、下载应用等；除此之外，Go语言还适用于内存数据库和云平台领域，目前国外很多云平台都是采用Go开发。

+ 服务器编程。例如处理日志、数据打包、虚拟机处理、文件系统等。

+ 分布式系统、数据库代理器、中间件等。例如Etcd。

+ 网络编程。这一块目前应用最广，包括Web应用、API应用、下载应用等等。

+ 开发云平台。目前国内外很多云平台在采用Go开发。

### Go语言知名项目

Go发布之后，很多公司特别是云计算公司开始用Go重构他们的基础架构，很多基础设施都是直接采用Go进行了开发，诞生了许多热门项目。

**基础设施**

代表项目：docker、kubernetes、etcd、consul等。

**数据库**

代表项目：influxdb、cockroachdb等。

**微服务**

代表项目：go-kit、micro、kratos等。



## 安装Go语言

Go语言可用于FreeBSD、Linux、Windows和macOS等操作系统。有关对这些平台的要求，请参与Go语言网站列出的系统需求。

Go语言的官方网站为https://golang.org/，国内的用户可以访问https://golang.google.cn/dl/。通常情况下，按照本文的步骤进行安装不会出现问题，遇到安装问题的读者，请通过公众号与我联系。

### Windows系统

**下载链接**

+ 32位下载地址：https://golang.google.cn/dl/go1.15.8.windows-386.msi

+ 64位下载地址：https://golang.google.cn/dl/go1.15.8.windows-amd64.msi

默认安装到C:\go目录下，建议不要更改安装目录。

**GOPATH配置**

安装完毕后需要配置GOPATH，GOPATH是Go语言用来存放第三方源码、二进制文件、类库等文件的路径。

1. 例如系统用户名为demo，则需要新建以下三个目录：

  + C:\Users\demo\go\src 存放源码

  + C:\Users\demo\go\pkg 存放类库

  + C:\Users\demo\go\bin 存在二进制文件

2. 环境变量设置：

  + 新增GOPATH，值为C:\Users\demo\go

  + 新增PATH（已存在则编辑），值为C:\Users\demo\go\bin

### Linux系统

Linux具有众多发行版，如Ubuntu、CentOS、RedHat、Debian等等，所有发行版的安装步骤是一致的，区别是根据CPU架构选择不同的发布包。

常见的个人计算机CPU架构为amd64，下载amd64架构的发布包即可。

**Linux配置命令**

```bash
# 下载压缩包
wget https://golang.google.cn/dl/go1.15.8.linux-amd64.tar.gz
# 移动到opt目录
mv go1.15.8.linux-amd64.tar.gz /opt
# 解压
tar xf go1.15.8.linux-amd64.tar.gz
# 新建GOPATH目录
cd ~
mkdir go
cd go
mkdir pkg src bin
# 编辑 ~/.bashrc文件, 添加bin路径到PATH环境变量中
echo 'GOPATH=用户主目录/go' >> ~/.bashrc
echo 'PATH=/opt/go/bin:$GOPATH/bin:$PATH' >> ~/.bashrc
# 更新环境变量
source ~/.bashrc
# 测试安装结果
go version
```

### macOS系统

Apple公司于2020年发布了采用M1芯片(arm64架构)的硬件产品，支持M1芯片的Go语言版本为1.16，根据CPU架构选择对应的pkg包安装即可。

+ amd64: https://golang.google.cn/dl/go1.15.8.darwin-amd64.pkg

+ arm64: https://golang.google.cn/dl/go1.16.darwin-arm64.pkg

**macOS配置命令**

```bash
# 新建GOPATH目录
cd ~
mkdir go
cd go
mkdir pkg src bin
# 编辑 ~/.bashrc文件, 添加bin路径到PATH环境变量中
echo 'GOPATH=用户主目录/go' >> ~/.bashrc
echo 'PATH=$GOPATH/bin:$PATH' >> ~/.bashrc
# 更新环境变量
source ~/.bashrc
# 测试安装结果
go version
```

## 配置集成开发环境

本节将介绍如何在本地计算机上配置集成开发环境，以下步骤使用macOS版本作为示例，其他操作系统类似。

Visual Studio Code(简称VSCode)是由微软开发的、同时支持Windows、Linux和macOS操作系统的开源编辑器，它支持测试，并且内置了git功能，提供了丰富的语言支持与常用编程工具。

1. 打开官方网站 https://code.visualstudio.com/，点击蓝色按钮下载即可。

2. 新版本的VSCode不再内置中文语言包，需要安装语言包扩展。安装VSCode后打开VSCode编辑器，在扩展窗口中搜索“Chinese”，安装第一个即可。

![image-20191022102923920](https://static.ddhigh.com/blog/2021-02-25-111457-2.png)

3. 用VSCode新建一个空项目，打开项目之后新建main.go，此时VSCode右下角会弹出Go工具链安装的提示，选择”Install All“即可。

## 编写HTTP服务器

### 代码

```go
package main

import (
	"io"
	"net/http"
)

func main() {
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		io.WriteString(w, "hello world")
	})
	http.ListenAndServe(":8080", nil)
}
```

### 程序结构说明

+ package 关键字声明文件所在的包，每个go文件都必须声明。每个可执行程序都必须包含main包，程序的入口点为main包的func main函数
+ import 关键字声明需要导入的包，代码中需要使用http服务器相关方法，因此导入了http包
+ func main程序的入口点

### 编译并运行程序

编译并运行文件是开发过程中的一个常见步骤，Go提供了完成这个步骤的快捷途径。

Go语言提供了build和run两个命令来编译运行Go程序：

+ go build 会编译可执行文件，并不执行
+ go run 不会创建可执行文件，直接执行

使用go run运行HTTP服务器，之后通过浏览器打开即可。

## 小结

本文介绍了Go语言的安装以及集成开发环境的配置。通过HTTP服务器演示了Go程序的开发过程。

下一章将学习Go语言的基本语法：

+ 变量和常量
+ 数据类型
+ 运算符
+ 条件语句
+ 循环语句

