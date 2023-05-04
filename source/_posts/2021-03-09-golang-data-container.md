---
title: Golang程序设计——数据容器
date: 2021-03-09 16:21:34
categories:
- engineering
---

本文学习Go语言数据容器、包括数组、切片和映射。

## 数组

数组是一个数据集合，常用于存储用数字索引的同类型数据。Go语言的数组调用函数时使用的是值传递，因此形参会拷贝一份实参的值。

在Go语言中，声明数组需要同时指定长度和数据类型，数组长度是其类型的一部分，因此`[5]int`和`[1]int`是两种类型。

Go语言可以对数组进行写入、读取、删除、遍历等操作。

```go
package main

import "fmt"

func main() {
	// 声明数组并指明长度，不初始化，因此a的5个元素为int类型的零值（0）
	var a [5]int
	// 声明数组并指明长度，并初始化4个元素，因此b的最后1个元素为int类型零值（0）
	var b = [5]int{1, 2, 3, 4}
	// 声明数组，不指明长度，编译器会根据值数量推导长度为4
	var c = [...]int{1, 2, 3, 4}
	// 数组写入
	a[0] = 0
	a[1] = 1
	// 数组读取
	fmt.Printf("a[0]=%d\n", a[0])
	// 数组删除（赋零值）
	a[0] = 0
	// 数组的遍历
	for index, value := range c {
		fmt.Printf("c[%d]=%d\n", index, value)
	}
	// 输出b
	fmt.Printf("b=%v\n", b)
}
```

## 切片

### 使用切片

在Go语言中，数组是一个重要的类型，但是使用切片的情况更多。切片是底层数组中的一个连续片段，因此数组支持的特性切片也全部支持，必须顺序遍历、通过索引访问元素等等。

为何使用切片的情况更多呢？主要是因为Go语言的数组不支持自动扩容，而且不支持删除元素，更重要的是Go语言数组是值类型，切片是引用类型，在向函数传参时切片拥有更好的性能。

```go
package main

import "fmt"

func main() {
	// 声明一个大小为0的int类型切片
	var a = make([]int, 0)
	// 添加三个元素
	a = append(a, 1, 2, 3)
	fmt.Println(a)
	// 遍历元素
	for index, value := range a {
		fmt.Printf("a[%d]=%d\n", index, value)
	}
	// 声明一个大小为4的切片
	var b = make([]int, 4)
	// 将a的元素复制到b
	copy(b, a)
	// 删除指定下标的元素
	a = append(a[:1], a[2:]...)
	fmt.Printf("a=%v\n", a)
	fmt.Printf("b=%v\n", b)
	// 使用值初始化切片
	var c = []int{1, 2, 3, 4}
	fmt.Printf("c=%v\n", c)
	// 只定义，不初始化切片
	var d []int
	d = append(d, 1, 2, 3)
	fmt.Printf("d=%v\n", d)
}
```

声明切片可以不使用make初始化，append也不会报错。

### 运行时结构

切片运行时结构如下：

```go
type slice struct {
	array unsafe.Pointer
	len   int
	cap   int
}
```

1. array是底层数组

2. len是数组大小，可以通过len函数获取

3. cap是数组容量，可以通过cap函数获取

make函数创建切片有两种写法：

```go
make([]int, 0) // 1
make([]int, 0, 8) // 2
```

1. 声明了一个长度为0的切片，此时len为0，cap也为0

2. 声明一个长度为0，容量为8的切片，此时len为0，cap为8

### 追加元素

Go语言提供append函数追加元素到切片中，append会在必要时扩容底层数组。扩容规则如下：

1. 新容量小于1024时，每次扩容2倍。例如现有容量为2，扩容后为4

2. 新容量大于1024时，每次扩容1.25倍。例如现有容量为1024，扩容后为1280

```go
package main

import "fmt"

func main() {
	// 直接使用值初始化切片
	var a = []int{1, 2, 3, 4, 5}
	a = append(a, 6, 7)
	var b = []int{9, 10}
	// 追加b的全部元素到a
	a = append(a, b...)
	fmt.Printf("a=%v\n", a)
	fmt.Printf("b=%v\n", b)
}
```

### 范围操作符

切片支持取范围操作，新切片和原切片共享底层数组，因此对切片的修改会同时影响两个切片。

范围操作符语法如下：a[begin:end]，左闭右开区间。因此a[1:10]包含a切片索引为1~9的元素。

```go
package main

import "fmt"

func main() {
	// 直接使用值初始化切片
	var a = []int{1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
	var b = a[1:10]
	fmt.Println(b)
	// 修改新切片元素
	b[0] = 11
	fmt.Println(a)
	fmt.Println(b)
}
```

可以看到修改b索引为0的元素为11之后，a切片也同时受到影响。

范围操作符的切片这一点在编程中要特别注意！

### 删除元素

利用范围操作符和append函数可以删除指定的切片元素。

```go
package main

import "fmt"

func main() {
	// 直接使用值初始化切片
	var a = []int{1, 2, 3, 4, 5}
	// 删除第2个元素
	a = append(a[:1], a[2:]...)
	fmt.Println(a)
	// 删除第2、3个元素
	a = []int{1, 2, 3, 4, 5}
	a = append(a[:1], a[3:]...)
	fmt.Println(a)
}
```

### 复制元素

通过copy函数可以复制切片的全部或部分元素。在复制切片之前，需要声明好目标切片并设置len。

*len**必须大于**0**，否则将不会复制任何元素。*

```go
package main

import "fmt"

func main() {
	// 直接使用值初始化切片
	var a = []int{1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
	var b = make([]int, 0, 8)
	copy(b, a)
	fmt.Println(b)
	var c = make([]int, 8)
	copy(c, a[9:10])
	fmt.Println(c)
}
```

程序输出如下：

```
[]
[10 0 0 0 0 0 0 0]
```

可以看到切片b没有任何值，切片c成功复制了a的最后一个元素。

## 映射

映射也叫字典、哈希表，数组和切片是通过数字索引访问的顺序集合，而映射是通过键来访问的无序集合。映射在查找方面非常高效，有着O(1)的时间复杂度，是非常常用的数据结构。

### 使用映射

映射必须初始化之后才能使用，这一点和切片不同。

```go
package main

import "fmt"

func main() {
	// 使用make初始化映射
	var a = make(map[string]int)
	a["zhangsan"] = 18
	a["lisi"] = 28
	fmt.Printf("a=%v\n", a)
	// 使用值初始化映射
	var b = map[string]int{
		"zhangsan": 18,
		"lisi":     28,
	}
	fmt.Printf("b=%v\n", b)
	// 遍历映射
	for key, value := range b {
		fmt.Printf("%s=%d\n", key, value)
	}
}
```

下面是未初始化映射的使用

```go
package main

import "fmt"

func main() {
	var a map[string]int
	a["zhangsan"] = 1
	for k, v := range a {
		fmt.Printf("%s=%d\n", k, v)
	}
}

```

该程序会产生运行时错误：

```
panic: assignment to entry in nil map
goroutine 1 [running]:
main.main()
/Users/example/go/src/go-microservice-inaction/src/2.1/main.go:7 +0x5d
```

### 运行时结构

映射的运行时结构如下：

```go
type hmap struct {
	count      int
	flags      uint8
	B          uint8
	noverflow  uint16
	hash0      uint32
	buckets    unsafe.Pointer
	oldbuckets unsafe.Pointer
	nevacuate  uintptr
	extra      *mapextra
}
```

部分字段说明如下：

1. count是目前映射的键值对数量

2. B是映射的容量，对数。例如B为8，则映射容量为28=256

3. buckets中存储具体的键值对

4. oldbuckets在扩容中会使用到

5. nevacuate 扩容进度指示器

当装载因子超过6.5时，映射将发生扩容操作。装载因子计算公式：count/2B。例如当前为为166，此时装载因子为166/28=0.6484375，继续插入元素时，装载因子变为167/28= 0.65234375，此时会触发自动扩容。

每次扩容会增加1倍的空间，同时会对已存在的键值对进行渐进式迁移（一次迁移一小部分）。

### 添加元素

Go语言映射添加元素和其他语言类似，使用[]语法即可。

```go
var m = make(map[string]int)
m["name"] = 18
```

添加元素时运行时会自动处理扩容和键值对迁移，无需用户程序关心。

### 删除元素

要从映射中删除元素，需要使用delete函数。

```go
var m = map[string]int{
  "zhangsan":18,
}
delete(m, "zhangsan") 
```

## 小结

本章介绍了Go语言常用的数据容器，其中对切片和映射的底层原理进行了简单介绍。Go语言通过内置切片和映射解决了C语言需要手动实现这两种常用数据结构的问题，提高了开发效率。在下一章将介绍Go语言的函数。

![img](https://static.ddhigh.com/blog/2021-03-09-162926-2.png)