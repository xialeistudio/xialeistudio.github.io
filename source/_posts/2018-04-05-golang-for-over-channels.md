---
title: golang for遍历channel时需要注意的问题
date: 2018-04-05 18:45:31
tags:
---

最近在做一个基于RabbitMQ的应用，由于官方的qos没有golang的版本，所以出了一点问题。问题代码如下：

```go
	_, ch, err := component.NewRabbitMQ()
	if err != nil {
		panic(err)
	}
	if err := ch.Qos(10, 0, true); err != nil {
		panic(err)
	}
	msgs, err := ch.Consume("push", "", false, false, false, false, nil)
	if err != nil {
		panic(err)
	}
	for m := range msgs {
		go func(d *amqp.Delivery) {
            defer func() { d.Ack(false) }
            // 处理消息
        }(&m)
    }
```

发现消费到10条消息，进程就退出了，但是exit code为0，表示系统是正常退出，由于做了日志记录可以确定消费了10条，所以初步确定是qos相关问题。

## 排查过程
1. 首先是把`d`的tag打印出来，发现全部是一样的，可以确定是重复的一条消息
2. 一开始想到可能是经典的`go协程执行在for循环结束以后`导致的，但是看我的代码不属于这种情况，有使用`&m`保证每一条消息都是不同循环传入的。所以判断可能是for循环的传递问题。
3. 确定方向之后开始写了一个测试项目用来验证我的想法是否正确。

## 测试代码

```go
package main

import "fmt"

func main() {
	ch := make(chan int, 10)
	for i := 0; i < 10; i++ {
		ch <- i
	}
	close(ch)
	for v := range ch {
		fmt.Println(&v)
	}
}
```

执行输出

```text
0xc420086008
0xc420086008
0xc420086008
0xc420086008
0xc420086008
0xc420086008
0xc420086008
0xc420086008
0xc420086008
0xc420086008
```

**到这里才焕然大悟，for循环中，如果循环变量不是指针，那么每次的变量是同一个，不过值变了。**，所以上例中的RabbitMQ go协程消费消息那里，需要直接传递值而不是指针，经过测试之后发现，问题确实解决了。

## 题外话

测试代码那里，如果不close掉channel是会发生死锁的，原因是 **当for循环读完channel的10个值之后会继续尝试读取下一个，而由于channel为空又没关闭，会一直阻塞形成死锁**

## TOOD

研究RabbitMQ Consumer部分的源码来看看消费channel被关闭的问题。