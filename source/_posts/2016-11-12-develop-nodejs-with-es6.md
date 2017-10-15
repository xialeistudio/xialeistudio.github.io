---
layout: post
title: 使用ES6开发Nodejs程序
date: 2016-11-12 19:18:46.000000000 +08:00
type: post
published: true
status: publish
categories:
- nodejs
tags:
- es6
- babel
- nodejs
meta:
  _edit_last: '1'
  _thumbnail_id: '561'
  views: '104'
---
ES6发布有一段时间了。但是Nodejs对此支持度还有待加强，就像前端可以使用babel+webpack构建基于ES6的工作流，其实Nodejs也是可以的（不需要手动编译）。当然，最终部署到生产服务器时要记得部署编译后的版本，否则运行时编译对性能是一种损失。
## 实践

```bash
npm init -y
npm install babel-core babel-register babel-polyfill --save
npm install babel-preset-es2015 babel-preset-stage-3  babel-plugin-transform-class-properties --save
```

*有个需要注意的问题是，nodejs直接执行的那个js文件还是得用原生JS语法（具体取决于Nodejs支持ES6的程度），比如在Nodejs v4.2.6下，可以使用 const 关键字，这个是不需要babel的。*

推荐目录结构如下：

```
|--bin
   |--a.js
   |--b.js
|--bootstrap
   |--a.js
   |--b.js
```

在项目根目录添加 .babelrc 文件，代码如下：

```json
{
  "presets": [
    "stage-3",
    "es2015"
  ],
  "plugins": [
    "transform-class-properties"
  ]
}
```

*bin 目录是真正的业务逻辑部分，可以使用ES6开发*,bootstrap相当于一个启动脚本目录，示例代码如下（bootstrap/a.js）：

```javascript
require('babel-register');
require('babel-polyfill');
require('../bin/a');
```

## 单元测试
编写单元测试脚本也是可以使用ES6的，这里使用 mocha 为例，编写好测试用例后，在启动mocha命令时添加参数 --compilers，示例如下：

```bash
mocha --compilers=babel-register
```

## 代码编译
代码编译需要使用**babel-cli**，终端执行：

```bash
npm install babel-cli --save-dev
babel bin -d lib
```

执行完毕后babel会自动生成**lib**目录，该目录为编译后的代码。