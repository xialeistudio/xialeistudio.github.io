---
title: Shell脚本快速入门(1)
date: 2020-02-10 12:00:00
categories:
- devtools
tags:
- shell
---

Shell 是一个用 C 语言编写的程序，用户可以通过Shell脚本语言来进行程序开发。与其他脚本语言不同，Shell脚本所需的解释器一般是内置在操作系统的，而像Node.js、PHP等脚本语言需要手动安装解释器程序才可以。

接下来将和大家一起来学习Shell脚本编程。

## Shell解释器

Shell解释器种类众多，笔者的电脑上内置以下Shell:

```
/bin/bash
/bin/csh
/bin/ksh
/bin/sh
/bin/tcsh
/bin/zsh
```

其中bash和sh是最常见的Shell解释器，一般情况下，这两种Shell没有区别，本文以bash为例。

## Hello World

打开文本编辑器(vim或者vscode)，新建文件 **hello.sh**，扩展名为sh(常用)。

```bash
#!/bin/bash
echo "Hello World!"
```

第1行用来指明本脚本需要使用什么解释器来执行。`#!`是一个约定的语法。

`echo`用来输出文本。

## 执行Shell脚本

有两种方法可以执行Shell脚本：

1. 作为可执行程序。给脚本添加可执行权限之后执行即可。

   ```bash
   chmod +x ./hello.sh # 添加可执行权限
   ./hello.sh # 执行脚本
   ```
   
2. 作为解释器脚本。直接运行指定的解释器程序，并将脚本路径传入，本方式不要求脚本有可执行权限。

   ```bash
   /bin/bash hello.sh # 使用/bin/bash来执行hello.sh
   ```

## Shell语法

和其他编程语言一样，Shell脚本也有自己的一套语法规则，我们现在来系统学习一下。

### 变量

#### 命名规则

定义变量时，变量名不加美元符号$，如：

```bash
name="xialei"
```

和其他编程语言不同的时，Shell脚本中`变量名和等号之间不能有空格`。Shell变量名的命名规则如下：

+ 只能包含英文字母、数字和下划线，且不能以数字开头
+ 不能包含空格
+ 不能使用关键字命名(通过下划线连接关键字是允许的)
+ 不能使用标点符号

以下是合法的示例

```bash
var1
var_2
_var3
MAX_PAGE
```

以下是不合法的示例

```bash
$var
```

#### 赋值

Shell有以下两种复制方式。

1. 直接赋值。直接在等号后面指定变量值。

   ```bash
   name="xialei
   admin=1
   ```
   
2. 使用命名执行结果。可以将其他命令的执行结果赋值给变量。（以下两种方式是等效的）

   ```bash
   file=`ls /etc` # 反引号(键盘Tab上面的键)
   file1=$(ls /etc)
   ```

已经存在的变量，可以被重新赋值。

```bash
name="hello"
echo $name

name="world"
echo $name
```

#### 使用变量

> 使用变量时在变量名前添加$符号，定义时不加。

```bash
name="xialei"
echo $name
echo ${name}
```

变量名两边的花括号是可选的，一般情况下不用加，但是如果涉及到边界识别问题，则需要手动添加花括号。

```bash
name="xialei"
echo "I'm ${name}studio." # 正确示例
echo "I'm $namestudio." # 错误示例
```

如果不添加花括号，Shell会将`namestudio`作为变量，该变量是不存在的，因此代码执行逻辑就不是我们想要的了。

#### 只读变量

如果某些变量在定义后就无法更改该变量的值，可以设置使用`readonly`设置为只读变量，对只读变量赋值会跑出错误。

```bash
name="xialei"
readonly name
name="zhangsan"
```

上述例子执行结果如下

```
./hello.sh: line 5: name: readonly variable
```

#### 释放变量

使用`unset`可以释放变量。变量被释放后不能使用(使用不会报错,shell中使用未定义变量当做空值处理)，此外unset命令无法释放只读变量。

```bash
name="xialei"
unset name # 不要$
echo $name
```

#### 变量类型

Shell脚本运行时，存在以下三种变量：

+ 局部变量。在脚本中定义的变量，只对当前脚本有效
+ 环境变量。所有程序都能访问到环境变量，此外Shell脚本也可以在运行时定义环境变量
+ Shell变量。Shell变量是由Shell解释器设置的变量。Shell变量中有一部分是局部变量，有一部分是环境变量。

### 数据类型

Shell支持数字、字符串和数组三种数据类型。下面我们分别进行学习。

#### 字符串

字符串可以使用单引号、双引号，也可以不使用引号。

单引号

```bash
name='xialei'
```

+ 单引号内的任何字符都会原样使用，不解析变量，也不解析转义字符。这一点和PHP有点类似

双引号

```bash
name='xialei'
msg="Hello, ${name}"
echo $msg
```

+ 双引号内的字符串会进行变量解析和转义字符解析

##### 字符串拼接

字符串拼接有以下两种方式。

引号拼接(支持双引号和单引号)

```bash
name='xialei'
msg='Hello '$name', welcome!'
echo $msg
```

内部嵌套(只支持双引号，因为单引号不解析变量)

```bash
name='xialei'
msg="Hello ${name}, welcome!"
echo $msg
```

#### 数组

Shell只支持一维数组，不限定数组大小。

数组的索引由0开始，读取元素的索引可以使用整数或表达式。

##### 数组定义

数组元素使用`小括号`括起来，每个元素之间用`空格`分割。

```bash
users=(xialei zhangsan lisi)
```

##### 读取数组元素

语法如下:

```bash
${数组名称[下标]}
```

比如上例中读取第2个人

```bash
users=(xialei zhangsan lisi)
echo ${users[1]} # 输出zhangsan
```

使用`@`作为下标可以获取数组的所有元素。

```bash
users=(xialei zhangsan lisi)
echo ${users[@]} # 输出 xialei zhangsan lisi
```

##### 获取数组长度

语法如下

```bash
length=${#数组名[@]}
```

比如输出users数组的长度

```bash
users=(xialei zhangsan lisi)
echo ${#users[@]}
```

今天的内容主要是让大家对Shell有一个宏观的认识，介绍了Shell的变量以及数据类型，下一篇将重点介绍Shell的运算符和流程控制。

![0.jpeg](https://static.ddhigh.com/blog/2019-10-22-102654.jpg)

(未完待续)