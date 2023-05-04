---
title: Shell脚本快速入门(2)
date: 2020-02-11 12:00:00
categories:
- engineering
tags:
- shell
---

今天我们来学习Shell的运算符和流程控制。

## 运算符

Shell和其他编程语言一样支持多种运算符，包括：

+ 算术运算符
+ 关系运算符
+ 逻辑运算符
+ 字符串运算符
+ 文件测试运算符

下面我们一起来看看。

### 算术运算符

> 原生bash不支持简单的数学运算，需要借助expr命令。

例如，输出两个数的和：

```bash
sum=`expr 1 + 1`
echo $sum
```

注意：

> 操作数和操作符之间必须用空格分开；
>
> 表达式必须使用反引号包裹；

|操作符|说明|示例|
| ---- | ---- | ---- |
| + | 加法 | expr 1 + 1 |
| - | 减法 | expr 1 - 1 |
| * | 乘法 | expr 1 \\* 1 需要转义*号 |
| / | 除法 | expr 1 / 1 |
| % | 取余 | expr 2 % 2 |

完整示例如下：

```bash
a=1
b=2
# 加法
val=`expr $a + $b`
echo "$a+$b=$val"

# 减法
val=`expr $a - $b`
echo "$a-$b=$val"

# 乘法
val=`expr $a \* $b` # 必须转义
echo "$a*$b=$val"

# 除法
val=`expr $a / $b`
echo "$a/$b=$val"

# 取余
val=`expr $a % $b`
echo "$a%$b=$val"
```

### 关系运算符 

关系运算符是比较两个操作数的数学大小关系，支持数字和数字字符串(如"1")

| 运算符 | 说明                               | 例子            |
| ------ | ---------------------------------- | --------------- |
| -eq    | 检测两数是否相等                   | [ `$a -eq $b` ] |
| -ne    | 检测两数是否不等                   | [ `$a -ne $b` ] |
| -gt    | 检查左边是否大于右边(greater than) | [ `$a -gt $b` ] |
| -lt    | 检查左边是否小于右边(less than)    | [ `$a -lt $b` ] |
| -ge    | 检查左边是否大于等于右边           | [ `$a -ge $b` ] |
| -le    | 检查左边是否小于等于右边           | [ `$a -le $b` ] |
| ==     | 判断两数是否相等                   | [ `$a == $b` ]  |
| !=     | 判断两数是否不想等                 | [ `$a != $b` ]  |

下面是一个if比较的示例，if语法将在本文介绍流程控制的时候进行详细学习。

```bash
a=10
b=20

if [ $a -eq $b ]
then
	echo "$a=$b"
else
	echo "$a!=$b"
fi
```

### 逻辑运算符

逻辑运算符就是与(AND)、或(OR)、非(NOT)。

| 运算符 | 说明   | 示例                                                  |
| ------ | ------ | ----------------------------------------------------- |
| !      | 逻辑非 | [ !false]返回true                                     |
| -o     | 逻辑或 | [ `$a -gt 0 -o $b -gt 0`] 当a和b有一个大于0时返回true |
| -a     | 逻辑与 | [ `$a -gt 0 -a $b -gt 0` ]当a和b都大于0时返回true     |

下面是结合关系运算符的例子：

```bash
a=1
b=2

if [ $a != $b ]
then
	echo "1!=2"
else
	echo "1=2"
fi

if [ $a -gt 0 -o $b -gt 0 ]
then
	echo "a或b大于0"
else
	echo "a和b都不大于0"
fi

if [ $a -gt 0 -a $b -gt 0 ]
then
	echo "a和b都大于0"
else
	echo "a和b不都大于0"
fi
```

### 字符串运算符

Shell被常用来处理字符串数据，因此有一些专门适用于字符串的运算符。

| 运算符 | 说明                     | 示例           |
| ------ | ------------------------ | -------------- |
| =      | 检查两个字符串是否相等   | [ `$a = $b` ]  |
| !=     | 检查两个字符串是否不想等 | [ `$a != $b` ] |
| -z     | 检查字符串长度是否为0    | [ `-z $a` ]    |
| -n     | 检查字符串长度是否不为0  | [ `-n $a` ]    |
| $      | 检查字符串是否为空       | [ `$a` ]       |

下面是一些示例：

```bash
a="hello"
b="world"

if [ $a = $b ]
then
	echo "$a和$b相同"
else
	echo "$a和$b不同"
fi

if [ -z $a ]
then
	echo "$a长度为0"
else
	echo "$a长度不为0"
fi

if [ -n $a ]
then
	echo "$a长度不为0"
else
	echo "$a长度为0"
fi

if [ $a ]
then
	echo "$a不为空"
else
	echo "$a为空"
fi
```

### 文件测试运算符

文件测试运算符用于检测文件的各种状态。下表列出了常用的文件测试运算符。

| 操作符  | 说明                                               | 示例           |
| ------- | -------------------------------------------------- | -------------- |
| -d file | 检查文件是否是目录                                 | [ `-d $file` ] |
| -f file | 检查文件是否是普通文件(不是目录，也不是块设备文件) | [ `-f $file`]  |
| -r file | 检查文件是否可读                                   | [ `-r $file` ] |
| -w file | 检查文件是否可写                                   | [ `-w $file` ] |
| -x file | 检查文件是否可执行                                 | [ `-x $file` ] |
| -s file | 检查文件大小是否为0                                | [ `-s $file` ] |
| -e file | 检查文件或文件夹是否存在                           | [ `-e $file` ] |
| -S      | 检查文件是否是Socket文件                           | [ `-S $file` ] |
| -L      | 检查文件是否存在且是一个符号链接                   | [ `-L $file` ] |

下面是一些示例：

```bash
file="/etc/passwd"

if [ -d $file ]
then
	echo "$file是目录"
else
	echo "$file不是目录"
fi

if [ -f $file ]
then
	echo "$file是普通文件"
else
	echo "$file不是普通文件"
fi

if [ -e $file ]
then
	echo "$file存在"
else
	echo "$file不存在"
fi
```

## 流程控制

Shell的流程控制也包含判断和循环，我们一起来学习一下。

### if/else

语法

```bash
if condition
then
	 语句1
	 语句2
	 ...
	 语句N
elif condition2
then
	 语句1
	 语句2
	 ...
	 语句N
else
	 语句1
	 语句2
	 ...
	 语句N
fi
```

> + elif和else分支是可以省略的
>
> + if/fi 需要配对

下面是一些示例：

```bash
a=1
b=2
if [ $a == $b ]
then
   echo "a = b"
elif [ $a -gt $b ]
then
   echo "a > b"
elif [ $a -lt $b ]
then
   echo "a < b"
else
   echo "所有条件都不匹配"
fi
```

### for循环

语法如下

```bash
for item in item1 item2 ... itemN
do
	语句1
	语句2
	...
	语句N
done
```

> + do/done需要配对
> + in列表支持文件列表、字符串、数字和其他数组数据

下面是循环输出`/etc`下文件和目录的示例：

```bash
for dir in `ls /etc`
do
	echo "$dir"
done
```

### while

语法如下

```bash
while condition
do
	语句1
	语句2
	...
	语句N
done
```

下面是一个示例

```bash
c=1
while(( $c<=10 ))
do
    echo $c
		c=`expr $c + 1`
done
```

### switch

语法如下

```bash
case 值 in
模式1)
	语句1
	语句2
	...
	语句N
	;;
模式2)
	语句1
	语句2
	...
	语句N
	;;
*)
	语句1
	语句2
	...
	语句N
	;;
easc
```

> + 模式匹配之后不会再执行其他模式语句(不需要手动break)
> + case/easc 必须配对
> + 每个模式语句的末尾必须添加两个分号
> + 使用*号捕获其他模式

如下是一个示例

```bash
echo '输入星期几'
read day
case $day in
	1)
		echo "星期一"
		;;
	2)
		echo "星期二"
		;;
	...
	*)
		echo "输入的数字无效"
		;;
```

> + read是从标准输入读取一行赋值给指定变量

### break

break命令允许跳出循环体。下面是一个示例

```bash
sum=0

while read n
do
	if [ $n -gt 0 ]
	then
		sum=`expr $sum + $n`
	else
		break
	fi
done
```

### continue

continue命令允许跳过本次循环，直接进行下一轮循环。下面是一个示例

```bash
sum=0

while read n
do
	if [ $n -gt 0 ]
	then
		sum=`expr $sum + $n`
	else
		continue # 本次输入不合法，跳过，
	fi
done
```

## 九九乘法表

结合今日所学，我们用Shell来打印一个九九乘法表：

```bash
#!/bin/bash

i=1

while [ $i -le 9 ] # i <= 9
do
	j=1
	while [ $j -le 9 ] # j <= 9
	do
		if [ $i -ge $j ] # if($i >= $j)
		then
			val=`expr $i \* $j`
			echo -n "$j*$i=$val "
		fi
		j=`expr $j + 1` # j++
	done
	echo
	i=`expr $i + 1` # i++
done
```

执行结果如下:

```
1*1=1 
1*2=2 2*2=4 
1*3=3 2*3=6 3*3=9 
1*4=4 2*4=8 3*4=12 4*4=16 
1*5=5 2*5=10 3*5=15 4*5=20 5*5=25 
1*6=6 2*6=12 3*6=18 4*6=24 5*6=30 6*6=36 
1*7=7 2*7=14 3*7=21 4*7=28 5*7=35 6*7=42 7*7=49 
1*8=8 2*8=16 3*8=24 4*8=32 5*8=40 6*8=48 7*8=56 8*8=64 
1*9=9 2*9=18 3*9=27 4*9=36 5*9=45 6*9=54 7*9=63 8*9=72 9*9=81 
```

今天的内容是Shell中比较重要的，也是最常用的语法。下一篇将对Shell的输入输出进行学习。

![0.jpeg](https://static.ddhigh.com/blog/2019-10-22-102654.jpg)

(未完待续)