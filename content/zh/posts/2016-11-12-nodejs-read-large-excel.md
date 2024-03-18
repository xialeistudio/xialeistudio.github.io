---
slug: nodejs-read-large-excel
title: Nodejs读取大excel
date: 2016-11-12 19:08:06.000000000 +08:00
categories:
- Engineering
---
## 背景
Nodejs读取Excel时如果不使用stream处理的话，会导致内存溢出，毕竟要一次性加载excel的全部行数到内存中，而Nodejs单进程是有内存限制的，所以在读取超大excel的时候需要使用到stream，如果自己使用Nodejs自带的stream模块去解析excel的话，我想这个过程会很麻烦，本文使用npm提供的*excel-stream*，该模块使用**stream+event**方式读取excel，所以不用担心内存溢出问题。

## 使用
打开终端执行：

```bash
npm init -y
npm install excel-stream --save
```

新建index.js

```javascript
import excel from 'excel-stream';
import excel from 'excel-stream';
import events from 'events';
import fs from 'fs';
export default class ExcelReadExecutor extends events.EventEmitter{
  static EVENT_DATA = 'data';
  static EVENT_ERROR = 'error';
  static EVENT_CLOSE = 'close';
  /**
   * 构造方法
   * @param path 路径
   * @param options
   */
  constructor(path, options = {}) {
    this.path = path;
    this.options = options;
  }

  /**
   * 读取
   */
  execute() {
    fs.createReadStream(this.path)
      .pipe(excel(this.options))
      .on('data', (data)=> this.emit(ExcelReadExecutor.EVENT_DATA, data))
      .on('error', (data)=> this.emit(ExcelReadExecutor.EVENT_ERROR, data))
      .on('close', (data)=> this.emit(ExcelReadExecutor.EVENT_CLOSE, data));
  }
}
```


当调用*execute*方法之后，就会触发相应的事件了。
## 测试
新建test.js，并新建一个excel文件（文件路径为index.js同级目录，excel文件名为**test.xlsx**）插入几行数据进行测试。

```javascript
const executor = new ExcelReadExecutor(`${__dirname}/test.xlsx`, {sheet: 'test'});
executor
  .on(ExcelReadExecutor.EVENT_DATA, (data)=&gt; {
    console.log(data);
  })
  .on(ExcelReadExecutor.EVENT_CLOSE, ()=&gt; {
    console.log('end');
  })
  .on(ExcelReadExecutor.EVENT_ERROR, console.error);
executor.execute();
```

每成功读取一行就会触发一次EVENT_DATA事件，读取完成后会触发EVENT_CLOSE。
