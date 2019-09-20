---
title: golang限制协程数量
date: 2018-01-31 22:23:09
categories:
- backend
- go
---

## 为什么要限制协程数量

golang的go关键字并发实在是太简单，但是带来的问题是由于硬件和网络状况的限制，不受控制的增加协程是非常危险的做法，甚至有可能搞垮数据库之类的应用! 而并发控制在go中是非常常用的技巧，以此文来记录一下学习历程。

## 原理

由于channel的阻塞机制，通过设置缓冲channel的缓冲大小来控制同时执行的协程数量。

## demo代码

```go
package main

import (
	"log"
	"time"
)

func main() {
	start := time.Now()
	ch := make(chan int, 2)
	for i := 0; i <= 10; i++ {
		ch <- 1
		go worker(i, ch)
	}
	close(ch)
	log.Println("complete", time.Since(start).Seconds())
}

// 模拟耗时操作
func worker(i int, ch chan int) {
	log.Println("worker", i)
	time.Sleep(time.Second)
	<-ch
```

## 运行

```bash
go run demo.ho
```

## 输出

```text
2018/01/31 22:24:49 worker 1
2018/01/31 22:24:49 worker 0
2018/01/31 22:24:50 worker 2
2018/01/31 22:24:50 worker 3
2018/01/31 22:24:51 worker 4
2018/01/31 22:24:51 worker 5
2018/01/31 22:24:52 worker 6
2018/01/31 22:24:52 worker 7
2018/01/31 22:24:53 worker 8
2018/01/31 22:24:53 worker 9
2018/01/31 22:24:54 worker 10
2018/01/31 22:24:54 complete 5.01140112
```

## 结论

可以看到日志的输出时间，每秒出现两个，正好等于我们`make`函数的大小，而总时间也是为`10/2`左右，证明限制起到了作用。

虽然本文写起来很简单，但是包含的技巧可以说大型程序仍然会用到。正所谓“万丈高楼平地起”。