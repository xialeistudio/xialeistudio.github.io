---
title: golang通用连接池的实现
date: 2018-02-01 20:04:00
categories:
- engineering
---

golang的channel除了goroutine通信之外还有很多其他的功能，本文将实现一种基于channel的通用连接池。

## 何为通用？

连接池的实现不依赖具体的实例，而依赖某个接口，本文的连接池选用的是`io.Closer`接口，只要是实现了该接口的对象都可以被池管理。
当然，你可以实现基于`interface{}`的连接池，这样任何对象都可以被管理。

## 实现原理

将连接句柄存入channel中，由于缓存channel的特性，获取连接时如果池中有连接，将直接返回，如果池中没有连接，将阻塞或者新建连接（没超过最大限制的情况下）。
由于面向接口编程，所有创建连接的逻辑是不清楚的，这里需要传入一个函数，该函数返回一个`io.Closer`对象。

## 实现

由于并发问题，在需要操作池中互斥数据的时候需要加锁。

```go
package pool

import (
	"errors"
	"io"
	"sync"
	"time"
)

var (
	ErrInvalidConfig = errors.New("invalid pool config")
	ErrPoolClosed    = errors.New("pool closed")
)

type factory func() (io.Closer, error)

type Pool interface {
	Acquire() (io.Closer, error) // 获取资源
	Release(io.Closer) error     // 释放资源
	Close(io.Closer) error       // 关闭资源
	Shutdown() error             // 关闭池
}

type GenericPool struct {
	sync.Mutex
	pool        chan io.Closer
	maxOpen     int  // 池中最大资源数
	numOpen     int  // 当前池中资源数
	minOpen     int  // 池中最少资源数
	closed      bool // 池是否已关闭
	maxLifetime time.Duration
	factory     factory // 创建连接的方法
}

func NewGenericPool(minOpen, maxOpen int, maxLifetime time.Duration, factory factory) (*GenericPool, error) {
	if maxOpen <= 0 || minOpen > maxOpen {
		return nil, ErrInvalidConfig
	}
	p := &GenericPool{
		maxOpen:     maxOpen,
		minOpen:     minOpen,
		maxLifetime: maxLifetime,
		factory:     factory,
		pool:        make(chan io.Closer, maxOpen),
	}

	for i := 0; i < minOpen; i++ {
		closer, err := factory()
		if err != nil {
			continue
		}
		p.numOpen++
		p.pool <- closer
	}
	return p, nil
}

func (p *GenericPool) Acquire() (io.Closer, error) {
	if p.closed {
		return nil, ErrPoolClosed
	}
	for {
		closer, err := p.getOrCreate()
		if err != nil {
			return nil, err
		}
		// todo maxLifttime处理
		return closer, nil
	}
}

func (p *GenericPool) getOrCreate() (io.Closer, error) {
	select {
	case closer := <-p.pool:
		return closer, nil
	default:
	}
	p.Lock()
	if p.numOpen >= p.maxOpen {
		closer := <-p.pool
		p.Unlock()
		return closer, nil
	}
	// 新建连接
	closer, err := p.factory()
	if err != nil {
		p.Unlock()
		return nil, err
	}
	p.numOpen++
	p.Unlock()
	return closer, nil
}

// 释放单个资源到连接池
func (p *GenericPool) Release(closer io.Closer) error {
	if p.closed {
		return ErrPoolClosed
	}
	p.Lock()
	p.pool <- closer
	p.Unlock()
	return nil
}

// 关闭单个资源
func (p *GenericPool) Close(closer io.Closer) error {
	p.Lock()
	closer.Close()
	p.numOpen--
	p.Unlock()
	return nil
}

// 关闭连接池，释放所有资源
func (p *GenericPool) Shutdown() error {
	if p.closed {
		return ErrPoolClosed
	}
	p.Lock()
	close(p.pool)
	for closer := range p.pool {
		closer.Close()
		p.numOpen--
	}
	p.closed = true
	p.Unlock()
	return nil
}
```

## 结论

基于该连接池，可以管理所有`io.Closer`对象。比如`memcached`,`redis`等等，非常方便！