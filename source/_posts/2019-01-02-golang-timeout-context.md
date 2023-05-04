---
title: 一起学context（二）——超时控制
date: 2019-01-02 17:54:59
categories:
- engineering
tags:
- context
---

上一篇文章讲到如何使用context来传值，实际上context还有另外一个重要功能——goroutine的超时控制。
很多时候goroutine如果不设超时，一旦发生阻塞将无限等待，协程数会越来越多，导致耗尽服务器内存。

## 分类
拥有超时控制的context有以下几种：
1. context.WithTimeout(parent Context, timeout time.Duration) (Context, CancelFunc) 指定时长超时结束
2. context.WithCancel(parent Context) (ctx Context, cancel CancelFunc) 手动结束
3. context.WithDeadline(parent Context, d time.Time) (Context, CancelFunc) 指定时间结束

一般常用的话就`context.WithTimeout`

## 示例代码

所有超时控制结束的代码结构都是类似的，示例代码如下：

```golang
package main

import (
	"context"
	"time"
	"fmt"
)

func main() {
	ctx, cancel := context.WithTimeout(context.TODO(), time.Second*3)
	defer cancel() // 防止任务比超时时间短导致资源未释放
	// 启动协程
	go task(ctx)
	// 主协程需要等待，否则直接退出
	time.Sleep(time.Second * 4)
}

func task(ctx context.Context) {
	ch := make(chan struct{}, 0)
	// 真正的任务协程
	go func() {
		// 模拟两秒耗时任务
		time.Sleep(time.Second * 2)
		ch <- struct{}{}
	}()
	select {
	case <-ch:
		fmt.Println("done")
	case <-ctx.Done():
		fmt.Println("timeout")
	}
}
```
task函数是一般情况下ctx的处理代码，很多第三方框架会声明具体函数的第一个参数为context.Context来允许设定代码超时时间。