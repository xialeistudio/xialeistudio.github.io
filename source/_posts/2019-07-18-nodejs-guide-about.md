---
title: NodeJs简明教程(1)
date: 2019-07-18 10:02:46
categories:
- Engineering
---

本文是NodeJs简明教程的第一篇，将介绍NodeJs整体架构以及重点概念。

## NodeJs究竟是什么

来看一段官方的说法[1]：

> As an asynchronous event driven JavaScript runtime, Node is designed to build scalable network applications. In the following "hello world" example, many connections can be handled concurrently. Upon each connection the callback is fired, but if there is no work to be done, Node will sleep.

Google翻译版本：

> 作为异步事件驱动的JavaScript运行时，Node旨在构建可伸缩的网络应用程序。 在下面的“hello world”示例中，可以同时处理许多连接。 在每次连接时都会触发回调，但是如果没有工作要做，Node将会休眠。

结合上面的介绍，我们可以得出一个结论：

> NodeJs的本质是一个Javascript运行时。该运行时基于异步事件驱动进行运作。

### 异步

本文中的异步指异步IO。维基百科对异步IO的定义[2]：

> 异步IO是计算机操作系统对输入输出的一种处理方式：发起IO请求的线程不等IO操作完成，就继续执行随后的代码，IO结果用其他方式通知发起IO请求的程序。与异步IO相对的是更为常见的“同步（阻塞）IO”：发起IO请求的线程不从正在调用的IO操作函数返回（即被阻塞），直至IO操作完成。

一言以蔽之就是：

> 执行IO请求后，调用方不等执行结果就继续执行下面的代码，IO操作完成后执行者会告诉调用者“我执行完了”。在NodeJs中通知方式是“回调”。

### 事件驱动

事件驱动是相对 **线程驱动** 而言的。**线程驱动** 下服务器为每个请求新建一个线程去处理。 
维基百科对事件驱动的定义[3]：

> 事件驱动程序模型下的系统，基本上的架构是预先设计一个事件循环所形成的程序，这个事件循环程序不断地检查当前要处理的信息，根据要处理的信息运行一个触发函数进行必要的处理。其中这个外部信息可能来自一个目录夹中的文件，可能来自键盘或鼠标的动作，或者是一个时间事件。

以NodeJs的HTTP服务器为例，当调用`server.listen`函数时，NodeJs就会创建一个事件循环，当有客户端请求过来时，NodeJs将该请求入队列进行后续处理，主线程以及轮询客户端请求并入队列，队列中的请求执行完毕后会通过回调函数的形式通知主线程，如此循环。

### Javascript运行时

Javascript运行时是个比较复杂的概念，本文在介绍 **Javascript运行时** 之前介绍一下 **Javascript引擎**。

#### Javascript引擎

维基百科的定义[4]：

> JavaScript引擎是一个专门处理JavaScript脚本的虚拟机，一般会附带在网页浏览器之中。

个人理解：

> Javascript引擎主要是对Javascript代码进行词法、语法等分析，通过解释器转化为字节码，虚拟机执行该字节码，带有JIT(Just-In-Time，即时编译技术)的虚拟机会将热点代码编译为机器码，从而加速执行过程。感谢[luckymore](https://github.com/luckymore)的热心指正！

目前业内出名的Javascript引擎非V8莫属了。

#### 运行时的组成

Javascript可以运行在浏览器，也可以运行在服务器(NodeJs)中，有些API或者对象只有浏览器有(比如DOM,BOM等)，而有些API或者对象只有服务器中有(如文件操作，HTTP服务器等)。

> Javascript运行时包括了Javascript引擎、特定环境API、事件循环和事件队列。

### NodeJs架构图

NodeJs由C++语言基于libuv开发，分层设计，Javascript只是其基于V8提供的上层接口，换句话说，如果把上层接口换成其他语言实现，比如换成PHP实现，那么PHP就可以实现异步事件驱动的服务器，运行时名称就成为 **NODE-PHP**。

![NodeJs架构图](https://more-happy.ddhigh.com/FqnmcUJhX0mGNDjMAIa1lOSJhNHJ)

+ Node standard library NodeJs标准库，也是直接提供给开发者调用的顶层代码
+ Node bindings Javascript和libuv在该层进行通信，基于V8打通语言壁垒
+ V8 执行JS代码
+ libuv 高性能异步I/O、事件驱动、线程池的库，也是NodeJs高性能的保证
+ C-ares 提供异步DNS
+ http_parser、OpenSSL、Zlib 提供HTTP解析、openssl加解密、数据压缩等接口

### NodeJs到底是不是单线程

> 不是，主线程Javascript线程是单线程，libuv提供线程池，NodeJs不仅仅是一个Javascript引擎，而是一套运行时，不能将Javascript线程孤立出来。

## NodeJs为什么这么快

1. 单线程解决了多线程环境下线程切换开销以及可能的线程同步开销
2. 异步+事件驱动保证了NodeJs主线程不会阻塞，会一直接受请求(这也是受人诟病的地方，其他语言实现的服务器，请求过大会排队处理，NodeJs会将请求全部入队，导致内存暴涨)

## NodeJs优缺点以及适合的场景

1. 由于主线程Javascript线程是单线程，所以主线程不能做CPU密集操作（比如什么加解密之类的，这种操作只能有Javascript线程运行，会阻塞事件循环），所以NodeJs适合I/O密集场景，比如常见的（TCP/HTTP服务器）
2. 对于前端开发者来说，几乎没有语言门槛
3. 跨平台，NodeJs在主流操作系统都有对应的二进制程序
4. 标准库强大，第三方库也很多，降低了造轮子成本
5. 易于部署，服务器安装一个NodeJs程序配合NPM包管理器即可运行，不用像PHP那样还要安装扩展，配置前端HTTP服务器

## 结语

欢迎继续关注本系列文章。

## 参考文献

1. [About NodeJs](https://nodejs.org/en/about/)
2. [异步IO](https://zh.wikipedia.org/zh-hans/%E5%BC%82%E6%AD%A5IO)
3. [事件驱动]( https://zh.wikipedia.org/wiki/%E4%BA%8B%E4%BB%B6%E9%A9%85%E5%8B%95%E7%A8%8B%E5%BC%8F%E8%A8%AD%E8%A8%88)
4. [Javascript引擎](https://zh.wikipedia.org/wiki/JavaScript%E5%BC%95%E6%93%8E)