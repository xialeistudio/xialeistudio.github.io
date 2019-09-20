---
title: NodeJs简明教程(4)
date: 2019-07-20 11:38:51
categories:
- backend
- nodejs
---

本文是NodeJs简明教程的第四篇，将介绍NodeJs文件系统模块相关的基本操作。

> fs 模块提供了一个 API，用于以模仿标准 POSIX 函数的方式与文件系统进行交互。

## 读取文件

文件系统的大部分函数都存在 **异步调用** 和 **同步调用** 两种形式。

### 异步

异步模式下，回调函数的第一个参数总为 **Error** 对象，且函数一般无返回值。

1. 如果为null，则本次调用未出错
2. 如果不为null，证明本次调用出错

新建 `index.js` 文件：

```js
const fs = require('fs');

fs.readFile('./index.js', { encoding: 'utf8' }, (err, data) => {
    if (err) {
        console.error('读取文件失败', err);
        return;
    }
    console.log(data);
})
```

`readFile`的第二个参数如果不指定编码，回调函数取到的`data`对象是`Buffer`，需要手动转字符串。读取文本文件可以指定编码，但是读取二进制文件(`比如读取图片文件`)

1. 在当前目录执行 `node index.js`
2. 输出如下：

    ```text
    const fs = require('fs');

    fs.readFile('./index.js', { encoding: 'utf8' }, (err, data) => {
        if (err) {
            console.error('读取文件失败', err);
            return;
        }
        console.log(data);
    })
    ```

### 同步模式

同步模式下，返回值为调用函数的结果，如果调用失败，将抛出**Error**对象：

```js
const fs = require('fs');

try {
    const data = fs.readFileSync('./index.js', { encoding: 'utf8' });
    console.log(data);
} catch (e) {
    console.log('读取失败', e)
}
```

输出数据和同步模式一致。

可以看到同步模式和异步模式下处理错误的方式是不同的。

> 各位读者在生产中尽量不要使用同步函数，否则会阻塞事件循环。
> 当然，有一种情况例外，需要同步读取配置文件然后才启动服务器的这种情况是可以的。

## 写入文件

新建`index.js`，代码如下：

```js
const fs = require('fs');

const data = 'Hello World';

fs.writeFile('./a.txt', data, (error) => {
    if (error) {
        console.error('保存失败', error);
        return;
    }
    console.log('保存成功');
})
```

1. 执行`node index.js`
2. 输出`保存成功`，同时当前目录会多出内容为`Hello World`的文本文件。

## 常用API

1. `fs.copyFile(src,dest[,flags],callback)` 复制文件
2. `fs.stat(path[,options],callback)` 读取文件状态
3. `fs.unlink(path,callback)` 删除文件
4. `fs.rename(oldPath,newPath,callback)` 重命名文件
5. `fs.mkdir(path[,options],callback)` 新建目录
6. `fs.rmdir(path,callback)` 删除目录
   
## 结语

文件系统的学习暂时到此为止，用到的时候大家可以详细查看文件，文件系统的函数调用方式和本文的示例都是类似的，各位读者可以举一反三。
