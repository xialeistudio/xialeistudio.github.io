---
title: 修复M1使用gomonkey提示permission defined错误
date: 2023-04-20 12:00:00
categories:
- backend
- go
---

## 问题

Go单元测试在M1上使用`github.com/agiledragon/gomonkey/v2 v2.9.0`包提示`permission defined`。
网上查阅消息得知是由于内存安全导致，不能同时对内存进行写和执行

## 解决方法
下面分享一种比较简单的方法，需要修改本地的go源码。

修改`go/pkg/mod/github.com/agiledragon/gomonkey/v2@v2.9.0/modify_binary_darwin.go`的`modifyBinary`方法。
将
```go
	err := mprotectCrossPage(target, len(bytes), syscall.PROT_READ|syscall.PROT_WRITE|syscall.PROT_EXEC)
```
修改为
```go
	err := mprotectCrossPage(target, len(bytes), syscall.PROT_READ|syscall.PROT_WRITE)
```
