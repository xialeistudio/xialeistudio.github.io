---
slug: webpack-loader-development
title: Webpack4不求人(4)——编写自定义Loader
date: 2020-03-11 12:00:00
categories:
- Engineering
tags:
- webpack
---

在前面的内容中，我们学习了Webpack的基本知识、常用脚手架和性能优化，虽然说大部分的开发场景社区已经又成熟的模块给我们使用，但是遇到特殊情况还是需要自己有独立开发的能力，因此今天我们一起来学习如何编写自定义Loader。

## 基本Loader

Webpack中loader是一个CommonJs风格的函数，接收输入的源码，通过同步或异步的方式替换源码后进行输出。

```javascript
module.exports = function(source, sourceMap, meta) {
  
}
```

+ source是输入的内容
+ sourceMap是可选的
+ meta是模块的元数据，也是可选的

需要注意的是，该导出函数必须使用function，不能使用箭头函数，因为loader编写过程中会经常使用到`this`访问选项和其他方法。

我们先编写一个基本的Loader，完成的工作很简单，那就是把输出的字符串进行替换。

1.新建loader-example目录，执行npm初始化，并安装webpack

```bash
mkdir loader-example
cd loadeer-example
npm init -y
npm install webpack webpack-cli
```

2.构建项目目录

```
|----loader # loader目录
		|----replace-loader.js # 替换字符串的Loader
|----src   # 应用源码
		|----index.js # 首页
|----package.json
|----webpack.config.js
```

3.编写loader/replace-loader.js

```javascript
module.exports = function(source) {
  return source.replace(/World/g, 'Loader');
};
```

本例中我们Loader只是简单的将源码中的”World“替换成了”Loader“。

4.编写src/index.js

```javascript
console.log('Hello World');
```


5.编写webpack.config.js

```javascript
const path = require('path');

module.exports = {
  entry: './src/index',
  target: 'node', // 我们编译为Node.js环境下的JS，等下直接使用Node.js执行编译完成的文件
  output:{
    path: path.resolve(__dirname, 'build'),
    filename: '[name].js'
  },
  module:{
    rules:[
      {
        test:/\.js$/,
        use: 'replace-loader'
      }
    ]
  },
  resolveLoader: {
  	modules: ['./node_modules', './loader'] // 配置loader的查找目录
  }
};
```

6.编写package.json

```json
{
  "scripts":{
    "build":"webpack"
  }
}
```

7.执行构建

```bash
npm run build
```

8.构建完成后，执行build/main.js

```bash
node build/main.js
```

此时终端输出如下，我们编写的Loader工作正常。

```
Hello Loader
```

## Loader选项

我们使用第三方loader时经常可以看到传递选项的情况：

```javascript
{
  test:/\.js$/,
  use:[
    {
      loader:'babel-loader',
      options:{
        plugins:['@babel/transform-runtime'],
        presets:['@babel/env']
      }
    }
  ]
}
```

在Loader编写时，Webpack中官方推荐通过loader-utils来读取配置选项，我们需要先安装。

```bash
npm install loader-utils
```

我们给刚才编写的replace-loader传递一个选项，允许自定义替换结果。

```javascript
const loaderUtils = require('loader-utils');

module.exports = function(source) {
	const options = loaderUtils.getOptions(this);
  return source.replace(/World/g, options.text);
};
```

接下来编辑webpack.config.js，给replace-loader传递选项。

```javascript
module.exports = {
  module:{
    rules:[
      {
        test:/\.js$/,
        use:[
          {
            loader:'replace-loader',
            options:{
              text: 'Webpack4'
            }
          }
        ]
      }
    ]
  },
  resolveLoader:{
    modules: ['./node_modules', './loader']
  }
};
```

执行构建之后用Node.js执行build/main.js，可以看到输出的内容已经发生变化了。

```
Hello Webpack4
```

## 异步Loader

在Loader中，如果存在异步调用，那么就无法直接通过return返回构建后的结果了，此时需要使用到Webpack提供的回调函数将数据进行回调。

Webpack4给Loader提供了`this.async()`函数，调用之后返回一个callback，callback的签名如下:

```javascript
function callback(
  err: Error|null,
  content: string|Buffer,
  sourceMap?:SourceMap,
  meta?: any
)
```

例如我们需要在loader中调用setTimeout进行等待，则相应的代码如下：

```javascript
module.exports = function(source) {
  const callback = this.async();
  setTimeout(() => {
    const output = source.replace(/World/g, 'Webpack4');
    callback(null, output);
  }, 1000);
}
```

执行构建，Webpack会等待一秒，然后再输出构建内容，通过Node.js执行构建后的文件，输出如下

```
Hello Webpack4
```

## "Raw" Loader

默认情况下，资源文件会被转化为 UTF-8 字符串，然后传给 loader。通过设置 `raw`，loader 可以接收原始的 `Buffer`。比如处理非文本文件时(如图片等等)。

```javascript
module.exports = function(source) {
  assert(source instanceof Buffer);
  return someSyncOperation(source);
};
module.exports.raw = true; // 设置当前Loader为raw loader, webpack会将原始的Buffer对象传入
```

## 读取loader配置文件

babel-loader在使用时可以加载.babelrc配置文件来配置plugins和presets，减少了webpack.config.js的代码量，便于维护。接下来我们编写一个i18n-loader，通过读取语言配置文件完成语言转换。

### 项目结构

```
|----loader
		|----i18n-loader.js # loader
|----i18n
		|----zh.json # 中文语言包
|----src
		|----index.js # 入口文件
|----webpack.config.js
```

i18n/zh.json

```json
{
    "hello": "你好",
    "today": "今天"
}
```

loader/i18n-loader.js

```javascript
const loaderUtils = require('loader-utils');
const path = require('path');

module.exports = function (source) {
    const options = loaderUtils.getOptions(this);
    const locale = options ? options.locale : null;

    // 读取语言配置文件
    let json = null;
    if (locale) {
        const filename = path.resolve(__dirname, '..', 'i18n', `${locale}.json`);
        json = require(filename);
    }

    // 读取语言标记 {{}}
    const matches = source.match(/\{\{\w+\}\}/g); 
    for (const match of matches) {
        const name = match.match(/\{\{(\w+)\}\}/)[1].toLowerCase();
        if (json !== null && json[name] !== undefined) {
            source = source.replace(match, json[name]);
        } else {
            source = source.replace(match, name);
        }
    }
    return source;
}
```

src/index.js

```javascript
console.log('{{Hello}}, {{Today}} is a good day.');
```

webpack.config.js

```javascript
const path = require('path');

module.exports = {
    entry: './src/index',
    output: {
        path: path.resolve(__dirname, 'build'),
        filename: '[name].js'
    },
    target: 'node',
    module: {
        rules: [
            {
                test: /\.js$/,
                use: [
                    {
                        loader: 'i18n-loader',
                        options: { // 传递选项
                            locale: 'zh'
                        }
                    }
                ]
            }
        ]
    },
    resolveLoader: {
        modules: ['./node_modules', './loader']
    }
};
```

package.json

```json
{
  "scripts":{
    "build":"webpack"
  }
}
```

### 执行构建

```
npm run build
```

构建完毕后使用Node.js执行build/main.js输出如下：

```
你好, 今天 is a good day.
```

可以看到i18n-loader成功读取了配置文件。

## 小结

本文简要介绍了Webpack中如何编写一个自定义的loader，权当抛砖引玉，更多的用法等待读者在实际工作中去挖掘，要想掌握Webpack的高级知识，Loader是必不可少的技能，有时候如果社区找不到合适的Loader，大家可以根据需要自己进行开发。

![0](https://static.ddhigh.com/blog/2020-03-11-060831.png)