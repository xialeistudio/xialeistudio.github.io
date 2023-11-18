---
slug: golang-function
title: Golang程序设计——函数
date: 2021-03-17 10:22:36
categories:
- Engineering
---

本文学习Go语言函数知识。函数是基本的代码块，用于执行一个任务。在Go语言中，函数可以接收数量不固定的参数，也可以返回多个结果。

## 函数结构

在编程领域，函数向编译器和开发者提供了有关的信息，这些信息指明了函数该接收什么样的输入以及会产生什么样的输出。这些信息是通过函数第一行提供的，第一行称为函数签名。

Go语言声明函数语法如下：

```go
func 函数名称(参数名 参数类型) (返回值名称 返回值类型) {
  // 函数体
  return语句
}
```

1. 参数名在参数类型前面，如`a int`，这一点和其他语言是不同的
2. 函数参数数量可以不固定，但是只允许最后一个参数数量不固定，而且必须是同种类型
3. 返回值名称不是必须的，但是参数名是必须写的
4. 有返回值的函数，函数体内必须包含return语句

示例：函数定义与调用

```go
package main

import "fmt"

func sum(a, b int) int {
	return a + b
}
func main() {
	fmt.Printf("1+2=%d\n", sum(1, 2))
}
```

在Go语言中，如果多个参数或多个返回值类型相同，只需要在最后一个参数或返回值声明类型。

例如下面的函数签名在Go语言中是合法的。

```go
func sum2(a, b int) (c, d int) 
```

## 不定参数函数

不定参数也就是数量不固定的参数。例如C语言中的printf函数就是一个典型的不定参数函数。Go语言支持不定参数函数，但是不定参数的类型必须相同。要声明不定参数，需要使用3个点(...)。

示例：不定参数的加法函数

```go
package main

import "fmt"

func sum(nums ...int) int {
	total := 0
	for _, n := range nums {
		total += n
	}
	return total
}
func main() {
	fmt.Printf("1+2+3+4=%d\n", sum(1, 2, 3, 4))
}
```

在sum函数中，nums是一个包含所有参数的切片。

## 函数返回值

### 多返回值

在Go语言中，函数能声明多个返回值，在这种情况下，return可以返回多个结果。函数调用者可通过多变量声明接收多个返回值。

示例：多返回值函数

```go
package main

import (
	"errors"
	"fmt"
)

func div(a, b int) (int, error) {
	if b == 0 {
		return 0, errors.New("b is zero")
	}
	return a / b, nil
}

func main() {
	ret, err := div(2, 1)
	if err != nil {
		fmt.Println(err)
		return
	}
	fmt.Printf("2/1=%d\n", ret)
}
```

### 命名返回值

命名返回值让函数能够在返回前将返回值赋给命名变量，这种设计有利于提高程序可读性。要指定命名返回值，可在函数签名的返回值类型前面添加变量名。

示例：命名返回值函数

```go
package main

import (
	"fmt"
)

func sum(a, b int) (total int) {
	total = a + b
	return
}

func main() {
	fmt.Printf("1+2=%d\n", sum(1, 2))
}
```

使用命名返回值后，return关键字可以单独出现，当然，return关键字继续返回结果值也是合法的。

```go
func sum(a, b int) (total int) {
	total = a + b
	return total
}
```

## 函数类型

在Go语言中，函数是一种数据类型，可以将函数赋值给变量、或者作为参数传递，也可以作为返回值返回。

示例：将函数作为变量、参数、返回值。

```go
package main

import "fmt"

func main() {
	// 函数作为变量
	sum := func(a, b int) int {
		return a + b
	}
	fmt.Printf("1+1=%d\n", sum(1, 1))
	// 函数作为参数
	sum2(1, 1, func(total int) {
		fmt.Printf("1+1=%d\n", total)
	})
	// 函数作为返回值
	totalFn := sum3(1, 1)
	fmt.Printf("1+1=%d\n", totalFn())
}

func sum2(a, b int, callback func(int)) {
	total := a + b
	callback(total)
}

func sum3(a, b int) func() int {
	return func() int {
		return a + b
	}
}
```

## 匿名函数、闭包、延迟执行函数

### 匿名函数

匿名函数指没有名称的函数，只有函数签名（参数和返回值声明）和函数体，匿名函数经常用于回调、闭包、临时函数等。

示例：利用匿名函数实现事件总线。

```go
package main

import "fmt"

func main() {
	emitter := make(map[string]func())
	addEventListener(emitter, "event1", func() {
		fmt.Println("event1 called")
	})
	emit(emitter, "event2")
}
// 添加事件监听器
// emitter 事件总线
// event 事件名
// callback 回调函数
func addEventListener(emitter map[string]func(), event string, callback func()) {
	emitter[event] = callback
}

// 触发事件
// emitter 事件总线
// event 事件名
func emit(emitter map[string]func(), event string) {
	callback, ok := emitter[event]
	if ok {
		callback()
	}
}
```

main函数调用addEventListener时传入的第三个函数即为匿名函数。

### 闭包

闭包可以理解为定义在一个函数内部的函数。在本质上，闭包是函数和其引用环境的组合体。引用环境即使在外部函数执行结束也不会被回收，因此可以利用闭包保存保存执行环境。

示例：利用闭包提供唯一ID生成器。

```go
package main

import "fmt"

func main() {
	s1 := sequenceId()
	s2 := sequenceId()
	fmt.Printf("s1 -> %v\n", s1())
	fmt.Printf("s1 -> %v\n", s1())
	fmt.Printf("s2 -> %v\n", s2())
	fmt.Printf("s2 -> %v\n", s2())
}

func sequenceId() func() int {
	var id int
	return func() int {
		id++
		return id
	}
}
```

输出如下

```go
s1 -> 1
s1 -> 2
s2 -> 1
s2 -> 2
```

函数sequenceId定义了一个局部变量id，并返回了一个子函数，子函数内部访问了外部的id，因此这构成一个典型的闭包。在前面的内容中我们学习过变量作用域，内部总是可以访问外部的变量或常量，而外部无法访问内部的变量或常量。此外，由于变量id被子函数使用，因此在sequenceId函数返回后，id也不会被销毁。

每调用一次sequenceId函数都会返回一个新的子函数以及对应的id，因此s1和s2之间的输出互不影响。

> 注意：由于闭包会导致被引用的变量无法销毁，因此需要注意使用，避免产生内存泄漏。

### 延迟执行函数

在实际编程中往往会打开一些资源，例如文件、网络连接等等，这些资源在使用完毕时（无论是正常关闭或者函数异常）需要主动关闭，当函数的结束分支太多或者逻辑比较复杂时容易发生忘记关闭的情况导致资源泄漏。

Go语言提供了defer关键字用来延迟执行一个函数，一般使用该函数延迟关闭资源。多个defer语句会按照先进后出的方式执行，也就是最后声明的最先执行，典型的栈结构。

示例：defer执行顺序。

```go
package main

import "fmt"

func main() {
	defer f1()
	defer f2()
	fmt.Println("call main")
}

func f1() {
	fmt.Println("call f1")
}

func f2() {
	defer fmt.Println("defer call f2")
	fmt.Println("call f2")
}
```

输出如下

```
call main
call f2
defer call f2
call f1
```

1. 第一行输出call main是因为main函数中只有一个非defer语句，因此call main最先执行

2. 第二行输出call f2是因为f2函数内部有一个非defer语句

3. 第三行输出defer call f2是因为f2函数的fmt.Println("call f2")执行完毕后才能执行defer

4. 第四行输出call f1是因为defer f1()最先声明因此最后执行

示例：基于defer和闭包构造一个函数执行耗时记录器。

```go
package main

import (
	"fmt"
	"time"
)

type Person struct {
	Name string
	Age  int
	Sex  string
}

func main() {
	defer spendTime()()
	time.Sleep(time.Second)
	fmt.Println("call main")
}

func spendTime() func() {
	startAt := time.Now()
	return func() {
		fmt.Println(time.Since(startAt))
	}
}
```

输出如下

```
call main
1.002345498s
```

spendTime()会返回一个闭包，因此定义defer时会初始化startAt为当前时间，defer执行时会执行闭包函数得到函数耗时。main函数为了测试方便休眠了一秒钟，因此可以看到输出是超过1秒的。

## 小结

本文介绍了如何在Go语言中使用函数。包括不定参数函数、多返回值和命名返回值函数以及将函数作为类型使用的方法，最后介绍了匿名函数、闭包和延迟执行函数。接下来的内容中将介绍Go语言中的结构体。

![img](https://static.ddhigh.com/blog/2021-03-09-162926-2.png)