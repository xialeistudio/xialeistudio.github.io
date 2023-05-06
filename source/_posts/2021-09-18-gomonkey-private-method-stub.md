---
title: gomonkey私有方法打桩
date: 2021-09-18 15:38:23
categories:
- Engineering
tags:
- testing
---

> ApplyMethod基于反射实现，无法对私有方法打桩，本文将解决这一问题。

## 被测代码

```go
type Dao struct {
}
// 私有方法
func (d *Dao) method1() error {
   return errors.New("failed")
}

// Method 公有方法
func (d *Dao) Method() error {
   return d.method1()
}
```

+ `method1`是私有方法，使用`ApplyMethod`无法打桩

## 测试代码

```go
func TestDao_Method(t *testing.T) {
   // 基于ApplyFunc可以读取到私有方法的地址并进行替换
   g := gomonkey.ApplyFunc((*Dao).method1, func(_ *Dao) error {
      return errors.New("打桩返回的错误")
   })
   defer g.Reset()

   d := Dao{}
   fmt.Println(d.Method())
}
```

## 执行
执行时需要添加`-gcflags=-l`禁止内联(内联后函数地址发生变化，某些函数会直接转化为语句调用)

```
=== RUN   TestDao_Method
打桩返回的错误
--- PASS: TestDao_Method (0.00s)
PASS
```
## 注意事项
1. 执行测试命令时添加`-gcflags=-l`
2. ``gomonkey.ApplyFunc`需要传递`(*Dao).method1`(结构体指针对应的函数)
3. 被测方法的接收器必须是`结构体指针`(因为第2步是传递指针)
```go
func (d *Dao) method1() error {
   return errors.New("failed")
}
```
