---
title: Golang程序设计——基本语法
date: 2021-02-26 16:04:33
categories:
- Engineering
---

本文学习Go语言基本语法，例如变量和常量、数据类型、运算符、条件语句、循环语句。

## 变量和常量

变量和常量是计算机程序不可或缺的部分。本节将介绍如何在Go程序中声明、使用变量和常量、还将介绍声明方式和作用域。

### 变量声明

在Go语言中，声明变量的方式有多种。在前面的文章介绍过，Go语言是一种静态类型语言，因此声明变量时必须指明其类型。

例：声明string类型的变量。

```go
package main

import "fmt"

func main() {
	var s1 string = "Hello World"
	var s2 = "Hello World"
	var s3 string
	s3 = "Hello World"
	fmt.Println(s1, s2, s3)
}
```

+ 使用关键字var声明变量。

+ 如果变量类型可以通过值推导则不用声明类型。s2通过值可以推导类型为string类型。

+ 变量可以在声明后赋值，未赋值的变量值为该类型的零值。

> 变量的类型很重要，因为这决定了可将什么值赋给该变量。例如，对于类型为string的变量，不能将整数赋值给它。将不匹配的值赋值给变量时，将导致编译错误。

例：将string类型的值赋值给int类型的变量。

```go
package main

import "fmt"

func main() {
	var i int
	i = "Hello World"
	fmt.Println(i)
}
```

编译该文件将导致编译错误。

```
go build main.go 
# command-line-arguments
./main.go:7:4: cannot use "Hello World" (type untyped string) as type int in assignment
```

### 多变量声明

例：声明多个**类型相同**的变量并进行赋值（显式指定类型）。

```go
package main

import "fmt"

func main() {
	var s1, s2 string = "S1", "S2"
	fmt.Println(s1, s2)
}
```

例：声明多个**类型不同**的变量并进行赋值（不能显式指定类型）。

```go
package main

import "fmt"

func main() {
	var s1, i1= "S1", 1
	fmt.Println(s1, i1)
}
```

例：声明多个**类型不同**的变量（显式指定类型）。

```go
package main

import "fmt"

func main() {
	var (
		s1 string
		i1 int
	)
	s1 = "Hello"
	i1 = 10
	fmt.Println(s1, i1)
}
```

> 声明变量后可以再次赋值，但是同一个变量只允许声明一次，否则将导致编译错误。

### 简短变量声明

在**函数**中声明变量时，可以用更简洁的方式。

```go
package main

import "fmt"

func main() {
	s1 := "Hello World"
	fmt.Println(s1)
}
```

+ :=表示简短变量声明，可以不使用var，不指定类型，但是必须进行赋值。

+ 只能在函数中使用简短变量声明。

### 变量声明最佳实践

Go语言提供了多种变量声明方式，下面的声明方式都是合法的。

```go
var s string = "Hello"
var s1 = "Hello"
var s2 string
s2 = "Hello"
s3 := "Hello"
```

该使用哪种方式呢？

Go语言对此有一个限制——只能在函数内部使用简短变量声明，在函数外部必须使用var进行声明。

> 在标准库中遵循的约定如下：有初始值的情况下，在函数内使用简短变量声明，在函数外使用var并省略类型；无初始值的情况下使用var并指定类型。

```go
package main

import "fmt"

var s = "Hello World"

func main() {
	s1 := "Hello World"
	fmt.Println(s, s1)
}
```

### 变量和零值

在Go语言中，声明变量时如果未初始化，则变量为默认值，该默认值也称为零值。在其他语言中未初始化的值为null或undefined。

```go
package main

import "fmt"

func main() {
	var s string
	var i int
	var b bool
	var f float32
	fmt.Printf("%v %v %v %v\n", s, i, b, f)
}
```

在Go语言中，检查变量是否为空，必须与该类型的零值比较。例如检测string类型的变量是否为空，可以与""判定。

```go
package main

import "fmt"

func main() {
	var s string
	if s == "" {
		fmt.Println("s为空")
	}
}
```

### 变量作用域

作用域指变量可以在什么地方使用，而不是说变量在哪里声明的。Go语言使用基于块的词法作用域，简单来说就是{}会产生一个作用域。

Go语言作用域规则如下：

1. 一对大括号({})表示一个块，块是可以嵌套的
2. 对于在块内声明的变量，可以在本块以及子块中访问
3. 子块可以访问父块的变量，父块不能访问子块的变量

例：Go语言的作用域。

```go
package main

import "fmt"

func main() {
	var s1 = "s1"
	{
		var s2 = "s2"
		// 可以访问s1,s2
		fmt.Println(s1, s2)
		{
			var s3 = "s3"
			// 可以访问s1,s2,s3
			fmt.Println(s1, s2, s3)
		}
	}
	// 只能访问s1
	fmt.Println(s1)
}
```

> 简单来说，就是块内可以访问块外的变量，块外不能访问块内变量。

### 声明常量

常量只在整个程序运行过程中都不变的值，常量必须在声明时赋值，声明后不可以更改。

Go语言使用const关键字声明常量。

```go
package main

import "fmt"

const s = "Hello"

func main() {
	const s2 = "World"
	const s3,s4 = "Hello","World"
	fmt.Println(s, s2)
}
```

> 常量也支持一次声明多个，此外常量的作用域和变量作用域一致。

## 数据类型

Go语言提供了丰富的数据类型，按类别分为布尔型、数值型（整数、浮点数、复数）、字符串型 、派生型。其中派声型包括指针类型、数组类型、结构体类型、接口类型、Channel类型、函数类型、切片类型和Map类型。

派生类型我们将在后面的内容中进行介绍。

### 布尔类型

布尔类型值只能为true或false。某些语言允许使用1和0来表示true和false，但Go语言不允许。

布尔类型的零值为false。

```go
package main

import "fmt"

func main() {
	var b bool
	if b {
		fmt.Println("b是true")
	} else {
		fmt.Println("b是false")
	}
} 
```

### 数值型

Go语言中数值型包含整数、浮点数以及复数。

**整数型**

| **类型** | **字节数**           | **范围**     |
| -------- | -------------------- | ------------ |
| byte     | 1                    | 0 ~ 28       |
| uint8    | 1                    | 0 ~ 28       |
| int8     | 1                    | -27 ~ 27-1   |
| uint16   | 2                    | 0 ~ 216      |
| int16    | 2                    | -215 ~ 215-1 |
| uint32   | 4                    | 0 ~ 232      |
| int32    | 4                    | -231 ~ 231-1 |
| uint64   | 8                    | 0 ~ 264      |
| int64    | 8                    | 263 ~ 263-1  |
| int      | 平台相关(32位或64位) |              |
| uint     | 平台相关(32位或64位) |              |

**浮点数**

| **类型** | **字节数** | **范围**               |
| -------- | ---------- | ---------------------- |
| float32  | 4          | -3.403E38 ~ 3.403E38   |
| float64  | 8          | -1.798E308 ~ 1.798E308 |

**复数**

略

### 字符串类型

字符串可以是任何字符序列，包括数字、字母和符号。Go语言使用Unicode来存储字符串，因此可以支持世界上所有的语言。

下面是一些字符串示例：

```go
var s = "$%^&*"
var s2 = "1234"
var s3 = "你好"
```

## 运算符

运算符用于在程序运行时执行数据运算和逻辑运算。Go语言支持的运算符有：

+ 算术运算符

+ 逻辑运算符

+ 关系运算符

+ 位运算符

### 算术运算符

算术运算符是用来对数值类型进行算术运算的。下表列出了Go语言支持的算术运算符。

| 运算符 | 说明 |
| ------ | ---- |
| +      | 相加 |
| -      | 相减 |
| *      | 相乘 |
| /      | 相除 |
| %      | 取余 |
| ++     | 自增 |
| --     | 自减 |

```go
package main

import "fmt"

func main() {
	var (
		a = 10
		b = 20
	)
	fmt.Printf("a+b=%d\n", a+b)
	fmt.Printf("a-b=%d\n", a-b)
	fmt.Printf("a*b=%d\n", a*b)
	fmt.Printf("a/b=%d\n", a/b)
	fmt.Printf("a%%b=%d\n", a%b)
	a++
	fmt.Printf("a++=%d\n", a)
	a--
	fmt.Printf("a--=%d\n", a)
}
```

> 和其他语言不同的是，Go语言不提供++a，--a运算符，只提供a++，a--。

### 关系运算符

关系运算符用来判断两个值的关系。下表列出了Go语言支持的关系运算符。

| 运算符 | 说明                                   |
| ------ | -------------------------------------- |
| ==     | 判断两个值是否相等                     |
| !=     | 判断两个值是否不相等                   |
| >      | 判断运算符左边的值是否大于右边的值     |
| <      | 判断运算符左边的值是否小于右边的值     |
| >=     | 判断运算符左边的值是否大于等于右边的值 |
| <=     | 判断运算符左边的值是否小于等于右边的值 |

```go
package main

import "fmt"

func main() {
	var (
		a = 10
		b = 20
	)
	if a == b {
		fmt.Println("a==b")
	} else {
		fmt.Println("a!=b")
	}

	if a < b {
		fmt.Println("a<b")
	} else {
		fmt.Println("a>=b")
	}

	if a <= b {
		fmt.Println("a<=b")
	} else {
		fmt.Println("a>b")
	}
}
```

### 逻辑运算符

逻辑运算符用来对操作数进行逻辑判断。下表列出了Go语言支持的逻辑运算符。

| 运算符 | 说明                                                        |
| ------ | ----------------------------------------------------------- |
| &&     | 逻辑与。两边操作数都为true则结果为true，否则为false         |
| \|\|   | 逻辑或。两边操作数只要有一个为true则结果为true，否则为false |
| !      | 逻辑非。如果操作数为true则结果为false，否则为true           |

```go
package main

import "fmt"

func main() {
	var a, b = true, false
	if a && b {
		fmt.Println("a和b同时为true")
	} else {
		fmt.Println("a和b至少一个为false")
	}

	if a || b {
		fmt.Println("a和b至少一个为true")
	} else {
		fmt.Println("a和b都为false")
	}
	if !a {
		fmt.Println("a是false")
	} else {
		fmt.Println("a是true")
	}
}
```

### 位运算符

位运算符用来对整数进行二进制位操作。下表列出了Go语言支持的位运算符。

| 运算符 | 说明     |
| ------ | -------- |
| &      | 按位与   |
| \|     | 按位或   |
| ^      | 按位异或 |
| >>     | 右移     |
| <<     | 左移     |

```go
package main

import "fmt"

func main() {
	var (
		a = 1
		b = 2
	)
	fmt.Printf("a&b=%d\n", a&b)
	fmt.Printf("a|b=%d\n", a|b)
	fmt.Printf("a^b=%d\n", a^b)
	fmt.Printf("a>>1=%d\n", a>>1)
	fmt.Printf("a<<1=%d\n", a<<1)
}
```

## 条件语句

条件语句是计算机程序的重要组成部分，几乎所有编程语言都支持。简单地说，条件语句检查指定的条件是否满足，并在满足时执行指定的操作。

下表列出了Go语言支持的条件语句。

| if                  | 由一个布尔表达式后紧跟一个或多个语句组成。 |
| ------------------- | ------------------------------------------ |
| if...else if...else | 由多个布尔表达式分支组成，并提供例外分支   |
| switch              | 基于不同条件执行不同操作，并提供默认操作   |

例：if的使用。

```go
package main

import "fmt"

func main() {
	var a = 10
	if a > 10 {
		fmt.Println("a大于10")
	} else if a == 10 {
		fmt.Println("a等于10")
	} else {
		fmt.Println("a小于10")
	}
}
```

例：switch的使用。

```go
package main

import "fmt"

func main() {
	var a = 10

	switch a {
	case 1:
		fmt.Println("a等于1")
	case 2:
		fmt.Println("a等于2")
	case 10:
		fmt.Println("a等于3")
	default:
		fmt.Println("默认分支")
	}
}
```

> 和其他语言不同，Go语言的case分支不需要添加break。

## 循环语句

在其他语言中一般会提供for、while、foreach等关键字实现循环，而在Go语言中只提供for关键字，但是也实现了类似的效果。

### for

for循环有着经典的三段式结构：

1. 循环初始化

2. 循环终止条件

3. 循环步进条件

```go
package main

import "fmt"

func main() {
  for i := 0; i < 10; i++ {
		fmt.Println(i)
  }
}
```

### while

while循环指定循环终止条件，不满足条件时循环一直执行并向终止条件靠拢，满足条件后终止循环。（无终止条件的循环称为死循环）

```go
package main

import "fmt"

func main() {
  i := 0
  for i < 10 {
		fmt.Println(i)
    i++
  }
}
```

死循环不需要终止条件。

```go
package main

import (
  "fmt"
  "time"
)

func main() {
  i := 0
  for {
    fmt.Println(i)
    i++
    time.Sleep(time.Second)
  }
}
```

### foreach

foreach循环多用来遍历列表、字典等数据结构。

```go
package main

import "fmt"

func main() {
  list := []int{1, 2, 3, 4, 5}
  for index, value := range list {
		fmt.Println(index, value)
  }
}
```

### continue

continue用来跳过本次循环继续执行下次循环。

```go
package main

import "fmt"

func main() {
  for i := 0; i < 5; i++ {
    if i == 1 {
      continue
    }
    fmt.Println(i)
  }
}
```

该程序判断i为1时跳过并执行下次循环，该程序输出如下。

```
0
2
3
4
```

### 3.1.5   break

break用来跳出循环，后续循环将不执行。

```go
package main

import "fmt"

func main() {
  for i := 0; i < 5; i++ {
    if i == 1 {
      break
    }
    fmt.Println(i)
  }
}
```

该程序判断i为1时跳出循环，该程序输出如下。

```
0
```

## 小结

本文介绍了Go语言的基本语法，包括变量和常量的使用、基础数据类型、流程控制等知识。下一章将介绍Go语言的数据容器类型，包括数组、切片和映射。

![img](https://static.ddhigh.com/blog/2021-02-26-161953-2.png)