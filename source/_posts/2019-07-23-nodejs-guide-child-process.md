---
title: NodeJs简明教程(8)
date: 2019-07-23 10:52:47
categories:
- backend
- nodejs
---

> NodeJs简明教程将从零开始学习NodeJs相关知识，助力JS开发者构建全栈开发技术栈！

关注获取更多`NodeJs精品文章`
![二维码](https://more-happy.ddhigh.com/FuFpZh9QTZVatcBtupR4MtOGPGTJ?imageView2/1/w/200)

本文是NodeJs简明教程的第八篇，将介绍NodeJs **子进程** 模块相关的基本操作。

> child_process 模块提供了衍生子进程的能力（以一种与 popen(3) 类似但不相同的方式）。

NodeJs的JS线程虽然是单线程，不能利用多核CPU，也不能执行CPU密集型的任务，但是通过派生子进程的形式加上**IPC(进程间通信)**，可以充分利用多核CPU。

## spawn

 `spawn`可以执行`指定的命令`，`spawn`的函数原型如下：

```js
child_process.spawn(command[,args][,options])
```

+ command `<string>` 要执行的命令
+ args `<string[]>` 传给命令的参数列表
+ options `<Object>` 额外选项
  + cwd `<string>` 子进程`workdir`
  + env `<Object>` 子进程环境变量

```js
const { spawn } = require('child_process');
const ls = spawn('ls', ['-lh', '/usr']); // 命令配置

ls.stdout.on('data', (data) => { // 监听命令执行的标准输出
  console.log(`stdout: ${data}`);
});

ls.stderr.on('data', (data) => { // 监听命令执行的标准错误输出
  console.log(`stderr: ${data}`);
});

ls.on('close', (code) => { // 监听子进程退出
  console.log(`子进程退出，使用退出码 ${code}`);
});
```

以上例程输出(不同机器输出可能不一样)

```text
stdout: total 0
drwxr-xr-x  970 root  wheel    30K  7 19 23:00 bin
drwxr-xr-x  306 root  wheel   9.6K  7 12 22:35 lib
drwxr-xr-x  249 root  wheel   7.8K  7 19 23:00 libexec
drwxr-xr-x   15 root  wheel   480B  4  1 14:15 local
drwxr-xr-x  239 root  wheel   7.5K  7 12 22:35 sbin
drwxr-xr-x   46 root  wheel   1.4K  9 21  2018 share
drwxr-xr-x    5 root  wheel   160B  9 21  2018 standalone

子进程退出，使用退出码 0
```

## exec

`exec`也可以执行`指定的命令`，与`spawn`区别是执行结果通过回调通知，`spawn`是通过事件，`exec`函数原型如下：

```js
exec(command[,options][,callback])
```

+ command `<string>` 要执行的命令，命令参数使用空格分隔
+ options `<Object>` 额外选项
  + cwd `<string>` 子进程`workdir`
  + env `<Object>` 子进程环境变量
  + timeout `<number>` 子进程执行超时
+ callback `<Function>` 执行结果回调
  + error `<Error>` 执行错误(不是子进程的错误输出)
  + stdout `<string|Buffer>` 子进程标准输出
  + stderr `<string|Buffer>` 子进程标准错误输出

```js
const exec = require('child_process').exec;

exec('ls -lh /usr',function(err,stdout,stderr) {
    if(err) {
        console.log('执行错误', err);
    }
    console.log('stdout', stdout);
    console.log('stderr', stderr);
});
```

以上例程输出

```text
stdout: total 0
drwxr-xr-x  970 root  wheel    30K  7 19 23:00 bin
drwxr-xr-x  306 root  wheel   9.6K  7 12 22:35 lib
drwxr-xr-x  249 root  wheel   7.8K  7 19 23:00 libexec
drwxr-xr-x   15 root  wheel   480B  4  1 14:15 local
drwxr-xr-x  239 root  wheel   7.5K  7 12 22:35 sbin
drwxr-xr-x   46 root  wheel   1.4K  9 21  2018 share
drwxr-xr-x    5 root  wheel   160B  9 21  2018 standalone

子进程退出，使用退出码 0
```

## execFile

`execFile`类似于`exec`，但默认情况下不会派生shell， 相反，指定的可执行文件 file 会作为新进程直接地衍生，使其比 `exec`稍微更高效。

支持与`exec`相同的选项。 由于没有衍生 shell，因此`不支持 I/O 重定向和文件通配等行为`。`execFile`原型：

```js
execFile(file[,args][,options][,callback])
```

+ file `<string>` 要执行的命令或可执行文件路径
+ args `<string[]>` 字符串数组形式的参数列表
+ options `<Object>` 额外选项
  + cwd `<string>` 子进程`workdir`
  + env `<Object>` 子进程环境变量
  + timeout `<number>` 子进程执行超时
+ callback `<Function>` 执行结果回调
  + error `<Error>` 执行错误(不是子进程的错误输出)
  + stdout `<string|Buffer>` 子进程标准输出
  + stderr `<string|Buffer>` 子进程标准错误输出

```js
const execFile = require('child_process').execFile;
execFile('ls', ['--version'], function(error, stdout, stderr) {
    if(err) {
        console.log('执行错误', err);
    }
    console.log('stdout', stdout);
    console.log('stderr', stderr);
});
```

以上例程输出同`exec`

## fork

`fork`是`spawn`的一个特例，专门用于派生新的`NodeJs进程`。`spawn`可以派生`任何进程`。`fork`方法原型如下：

```js
fork(modulePath[,args][,options])
```

+ modulePath `<string>` 要执行的JS路径
+ args `<string[]>` 字符串数组形式的参数列表
+ options `<Object>` 额外选项
  + cwd `<string>` 子进程的`workdir`
  + env `<Object>` 环境变量
  + silent `<boolean>` 如果为 true，则子进程的 stdin、stdout 和 stderr 将会被输送到父进程，否则它们将会继承自父进程。默认`false`

b.js

```js
const fork = require('child_process').fork;

const child = fork('./a.js',{silent:true}); // silent为true时可以监听子进程标准输出和标准错误输出
child.stdout.on('data',function(data){ // 监听子进程标准输出
    console.log('child stdout', data.toString('utf8'));
});
child.stderr.on('data', function(data){ // 监听子进程标准错误输出
    console.log('child stderr', data.toString('utf8'));
});
child.on('close', function(){
    console.log('child exit');
});
```

a.js

```js
console.log('我是子进程`);
```

终端执行`node b.js`，以上例程输出：

```text
child stdout 我是子进程

child exit
```

## 结语

子进程模块的介绍到此就告一段落了，一般情况下使用`spawn`和`execFile`即可。有任何疑问请扫码加群交流：

![微信群](https://more-happy.ddhigh.com/FpffwgkBeSWPyHRUJJmi9J9SFX_l?imageView2/1/w/200)