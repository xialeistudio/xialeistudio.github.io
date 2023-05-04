---
layout: post
title: Nodejs导出大数据到Excel
date: 2016-11-13 13:16:59.000000000 +08:00
type: post
published: true
status: publish
categories:
- engineering
---
在实际开发中，数据导出使用频率比数据导入高得多，而数据导出时来源一般是数据库，会有上万的数据导出，如果不做特殊处理的话，会导致NodeJs进程直接被killed。   
今天要提到的npm包是 **xlsx-writestream**，话不多说，进入正题。

```bash
npm init -y
npm install xlsx-writestream --save
```

```javascript

//编辑executor.js
import Writer from 'xlsx-writestream';
import fs from 'fs';
export default class ExcelWriteExecutor{
 /**
 * 构造方法
 * @param path 路径
 * @param options
 */
constructor(path, options = {}) {
  this.path = path;
  options.out = path;
  this.options = options;
  this.writer = new Writer(this.path, this.options);
  this.writer.getReadStream().pipe(fs.createWriteStream(this.path));
}

addRow(row) {
  this.writer.addRow(row);
}

addRows(rows) {
  this.writer.addRows(rows);
}

 /**
 * 输出
 */
execute() {
  return new Promise((resolve)=> {
    this.writer.finalize();
      setTimeout(resolve, 50);//延迟50毫秒是因为 finalize 调用结束之后，excel打开会报错，可能是没写入完成的原因，加了延迟之后正常，延迟值根据需要自己测试可以更改
    });
  }
}
//测试代码
async function test() {
  const executor = new ExcelWriteExecutor(`${__dirname}/test-write.xlsx`);
  executor.addRow({
  '姓名': 'fff',
  '电话': '15911111111',
  '公司': 'ddaaa',
  '职位': 'ddaaaxxxx',
  '生日': '',
  '邮箱': '',
  '选择城市': '',
  '单位/公司': '',
  '职务': '',
  '具体地址': '',
  '院系班级': '',
  '常住住址': ''
});
  await executor.execute();
}
```

在程序执行过程中，Excel会使用stream来操作，避免了NodeJs内存占用过大问题。
