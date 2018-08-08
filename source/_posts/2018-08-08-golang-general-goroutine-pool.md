---
title: golang40行代码实现通用协程池
date: 2018-08-08 11:07:25
categories:
- golang
tags:
- golang
- goroutine
---

## 代码仓库

[goroutine-pool](https://github.com/xialeistudio/goroutine-pool)

## golang 的协程管理

golang 协程机制很方便的解决了并发编程的问题，但是协程并不是没有开销的，所以也需要适当限制一下数量。

### 不使用协程池的代码(示例代码使用 chan 实现，代码略啰嗦)

```go
func (p *converter) upload(bytes [][]byte) ([]string, error) {
	ch := make(chan struct{}, 4)
	wg := &sync.WaitGroup{}
	wg.Add(len(bytes))
	ret := make([]string, len(bytes))

	// 上传
	for index, item := range bytes {
		ch <- struct{}{}
		go func(index int, imageData []byte) {
			defer func() {
				wg.Done()
				<-ch
			}()

			link, err := qiniu.UploadBinary(imageData, fmt.Sprintf("%d.png", time.Now().UnixNano()))
			if err != nil {
				log.Println("上传图片失败", err.Error())
				return
			}
			ret[index] = link
		}(index, item)
	}

	wg.Wait()
	return ret, nil
}
```

需要实现的需求有两个:

1.  限制最大协程数，本例为 4
2.  等待所有协程完成，本例为`bytes切片长度`

### 使用协程池的代码

```go
func (p *converter) upload(bytes [][]byte) ([]string, error) {
	ret := make([]string, len(bytes))
	pool := goroutine_pool.New(4, len(bytes))

	for index, item := range bytes {
		index := index
		item := item
		pool.Submit(func() {
			link, err := qiniu.UploadBinary(item, fmt.Sprintf("%d.png", time.Now().UnixNano()))
			if err != nil {
				log.Println("上传图片失败", err.Error())
				return
			}

			ret[index] = link
		})
	}
	pool.Wait()
	return ret, nil
}
```

可以看到最大的区别是只需要关注业务逻辑即可，并发控制和等待都已经被协程池接管

## 写在最后

希望本文能减轻你控制协程的负担
