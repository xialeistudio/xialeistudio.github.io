---
title: NodeJs简明教程(5)
date: 2019-07-20 13:00:27
categories:
- Engineering
---

本文是NodeJs简明教程的第五篇，将介绍NodeJs path模块相关的基本操作。

> path 模块提供用于处理文件路径和目录路径的实用工具。 

**注意：path模块只是处理文件路径，说白了就是字符串处理，跟文件系统无关**

## 读取路径的文件名

> path.basename() 方法返回 path 的最后一部分，类似于 Unix 的 basename 命令。 尾部的目录分隔符将被忽略。

1. 返回带扩展名
   
    ```js
    const path = require('path');

    console.log(path.basename('/usr/local/a.txt'))
    
    // 输出 a.txt
    ```

2. 返回不带扩展名

    ```js
    const path = require('path');

    console.log(path.basename('/usr/local/a.txt','.txt'))
    
    // 输出 a
    ```

## 读取文件路径的目录名

> path.dirname() 方法返回 path 的目录名，类似于 Unix 的 dirname 命令。 尾部的目录分隔符将被忽略。
> path.extname() 方法返回 path 的扩展名，从最后一次出现 .（句点）字符到 path 最后一部分的字符串结束。 如果在 path 的最后一部分中没有 . ，或者如果 path 的基本名称（参阅 path.basename()）除了第一个字符以外没有 .，则返回空字符串。

```js
const path = require('path');

console.log(path.dirname('/usr/local/a.txt'))

// 输出 /usr/local
```

## 获取文件扩展名

> path.extname() 方法返回 path 的扩展名，从最后一次出现 .（句点）字符到 path 最后一部分的字符串结束。

```js
const path = require('path');

console.log(path.extname('/usr/local/a.txt'));

// 输出 .txt
```

## 检测路径是否为绝对路径

> path.isAbsolute() 方法检测 path 是否为绝对路径。

```js
const path = require('path');
// linux || macosx
console.log(path.isAbsolute('/usr/local')); // 输出 true
console.log(path.isAbsolute('usr/local')); // 输出 false
// windows
console.log(path.isAbsolute('//server')); // 输出 true
console.log(path.isAbsolute('\\\\server')); // 输出 true
console.log(path.isAbsolute('c:\windows')); // 输出 true
console.log(path.isAbsolute('foo/bar')); // 输出 false
```

## 生成规范化的路径

> path.join() 方法使用平台特定的分隔符作为定界符将所有给定的 path 片段连接在一起，然后规范化生成的路径。
> 零长度的 path 片段会被忽略。 如果连接的路径字符串是零长度的字符串，则返回 '.'，表示当前工作目录。

```js
const path = require('path');

console.log(path.join('/a','b','c','..')); // 输出 /a/b

console.log(path.join('.','a','b','..','c')); // 输出 a/c
```

## 解析路径

> path.parse() 方法返回一个对象，其属性表示 path 的重要元素。 尾部的目录分隔符将被忽略。
> 返回对象属性如下：
> dir 目录
> root 根目录
> base 带扩展名的文件名或者目录名(最后一级是目录的情况下)
> name 文件名(不带扩展名)或目录名
> ext 文件扩展名(如果是目录则为空字符串)

```js
const path = require('path');

path.parse('/home/user/dir/file.txt');
// 返回:
// { root: '/',
//   dir: '/home/user/dir',
//   base: 'file.txt',
//   ext: '.txt',
//   name: 'file' }
```

## 获取两个路径的相对路径

> path.relative() 方法根据当前工作目录返回 from 到 to 的相对路径。

```js
const path = require('path');

console.log(path.relative('/data/orandea/test/aaa', '/data/orandea/impl/bbb')); 
// 输出 ../../impl/bbb
```

## 获取规范化的绝对路径

> path.resolve() 方法将路径或路径片段的序列解析为绝对路径。

```js
const path = require('path');

console.log(path.resolve('/foo/bar', './baz')); // 输出 /for/bar/baz
console.log(path.resolve('/foo/bar', '/tmp/file/');); // 输出 /tmp/file
console.log(path.resolve('a','b','../c/img.gif'));
// 假设当前工作目录 /home/wwwroot，上述语句输出 /home/wwwroot/a/c/img.gif

console.log(path.resolve()); // 假设当前工作目录 /home/wwwroot 输出 /home/wwwroot
```

## 结语

`path`模块的主要就是处理路径相关，经常和`fs`模块共同使用。
