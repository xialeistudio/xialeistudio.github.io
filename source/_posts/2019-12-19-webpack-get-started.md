---
title: Webpack4不求人系列(1)
date: 2019-12-19 12:00:00
categories:
- frontend
- javascript
tags:
- webpack
---

> Webpack是一个现在Javascript应用程序的模块化打包器，在Webpack中JS/CSS/图片等资源都被视为JS模块，简化了编程。当Webpack构建时，会递归形成一个模块依赖关系图，然后将所有的模块打包为一个或多个bundle。

![img](https://static.ddhigh.com/blog/2019-12-19-024407.jpg)

本文内容

1. 简介
2. 常用loader && plugin
3. 传统网站的webpack配置

## 简介

要系统地学习Webpack，需要先了解Webpack的四个**核心概念**:

+ 入口(entry)
+ 输出(output)
+ loader
+ plugin

webpack使用Node.js运行，因此所有的Node.js模块都可以使用，比如文件系统、路径等模块。

对Node.js基础不太了解的读者，可以参考我的[Node.js系列](https://www.ddhigh.com/2019/07/25/nodejs-guide-next-step.html)

配置文件`webpack.config.js`的一般格式为:

```javascript
const path = require('path'); // 导入Node.js的path模块


module.exports = {
  mode: 'development', // 工作模式
  entry: './src/index', // 入口点
  output: { // 输出配置
    path: path.resolve(__dirname, 'dist'), // 输出文件的目录
    filename: 'scripts/[name].[hash:8].js', // 输出JS模块的配置
    chunkFilename:'scripts/[name].[chunkhash:8].js', // 公共JS配置
    publicPath:'/' // 资源路径前缀，一般会使用CDN地址，这样图片和CSS就会使用CDN的绝对URL
  },
  module:{
    rules: [
      {
        test:/\.(png|gif|jpg)$/, // 图片文件
        use:[
          {
            loader:'file-loader', // 使用file-loader加载
            options:{ // file-loader使用的加载选项
              name:'images/[name].[hash:8].[ext]' // 图片文件打包后的输出路径配置
            }
          }
        ]
      }
    ]
  },
  plugins:[ // 插件配置
    new CleanWebpackPlugin()
  ]
};
```

> Webpack自己只管JS模块的输出，也就是output.filename是JS的配置，CSS、图片这些是通过loader来处理输出的

### 入口

入口指明了Webpack从哪个模块开始进行构建，Webpack会分析入口模块依赖到的模块(直接或间接)，最终输出到一个被称为*bundle*的文件中。

> 使用**entry**来配置项目入口。

**单一入口**

最终只会生成1个js文件

```javascript
module.exports = {
  entry: './src/index',
};
```

**多个入口**

最终会根据入口数量生成对应的js文件

```javascript
module.exports = {
  entry:{
  	home:'./src/home/index', // 首页JS
    about:'./src/about/index' // 关于页JS
  }
};
```

多个入口一般会在多页面应用中使用，比如传统的新闻网站。

### 输出

输出指明了Webpack将bundle输出到哪个目录，以及这些bundle如何命名等，默认的目录为`./dist`。

```javascript
module.exports = {
  output:{
    path:path.resolve(__dirname, 'dist'), // 输出路径
    filename:'scripts/[name].[hash:8].js', // 输出JS模块的文件名规范
    chunkFilename:'scripts/[name].[chunkhash:8].js', // 公共JS的配置
    publicPath:'/', // 资源路径前缀，一般会使用CDN地址，这样图片和CSS就会使用CDN的绝对URL
  }
};
```

**path**

path是打包后bundle的输出目录，**必须使用绝对路径**。所有类型的模块(js/css/图片等)都会输出到该目录中，当然，我们可以通过配置输出模块的名称规则来输出到path下的子目录。比如上例中最终输出的JS目录如下：

```
|----dist
		 |---- scripts
		 			 |---- home.aaaaaaaa.js
```

**filename**

**入口模块**输出的命名规则，在Webpack中，只有js是亲儿子，可以直接被Webpack处理，其他类型的文件(css/images等)需要通过loader来进行转换。

filename的常用的命名如下:

```
[name].[hash].js
```

+ [name] 为定义入口模块的名称，比如定义了home的入口点，这里的name最终就是home
+ [hash] 是模块内容的MD5值，一次打包过程中所有模块的hash值是相同的，由于浏览器会按照文件名缓存，因此每次打包都需要指定hash来改变文件名，从而清除缓存。

**chunkFilename**

**非入口模块**输出的命名规则，一般是代码中引入其他依赖，同时使用了optimization.splitChunks配置会抽取该类型的chunk

**hash**

Webpack中常见的hash有`hash`,`contenthash`,`chunkhash`，很容易弄混淆，这里说明一下。

+ hash 整个项目公用的hash值，不管修改项目的什么文件，该值都会变化
+ chunkhash 公共代码模块的hash值，只要不改该chunk下的代码，该值不会变化
+ contenthash 基于文件内容生成的hash，只要改了文件，对应的hash都会变化

**publicPath**

资源的路径前缀，打包之后的资源默认情况下都是相对路径，当更改了部署路径或者需要使用CDN地址时，该选项比较常用。

比如我们把本地编译过程中产生的所有资源都放到一个CDN路径中，可以这么定义：

```
publicPath: 'https://static.ddhigh.com/blog/'
```

那么最终编译的js,css,image等路径都是绝对链接。

### loader

loader用来在import时预处理文件，一般用来将非JS模块转换为JS能支持的模块，比如我们直接import一个css文件会提示错误，此时就需要loader做转换了。

比如我们使用loader来加载css文件。

```javascript
module.exports = {
  module:{
    rules:[
      {
        test: /\.(css)$/,
				use: ['css-loader']
      }
    ]
  }
};
```

#### 配置方式

Webpack中有**3**种使用loader的方式：

1. 配置式：在webpack.config.js根据文件类型进行配置，这是推荐的配置
2. 内联：在代码中import时指明loader
3. 命令行：通过cli命令行配置

#### 配置式

**module.rules**用来配置loader。**test**用来对加载的**文件名(包括目录)**进行正则匹配，只有当匹配时才会应用对应loader。

> 多个loader配置时从右向左进行应用

配置式Webpack的loader也有好几种形式，有些是为了兼容而添加的，主要使用的方式有以下3种。

```javascript
module.exports = {
  module:{
    rules:[
      {
        test: /\.less$/,
        loader:'css-loader!less-loader', // 多个loader中用感叹号分隔
      },
      {
        test:/\.css/,
        use:['css-loader'],//数组形式
      },
      {
        test:/\.(png|gif|jpg)$/,
        use:[ // loader传递参数时建议该方法
          {
            loader: 'file-loader',
            options:{ // file-loader自己的参数，跟webpack无关
              name: 'images/[name].[hash:8].js'
            }
          }
        ]
      }
    ]
  }
};
```

> 每个loader的options参数不一定相同，这个需要查看对应loader的官方文档。

### Plugin

loader一般用来做模块转换，而插件可以执行更多的任务，包括打包优化、压缩、文件拷贝等等。插件的功能非常强大，可以进行各种各样的任务。

下面是打包之前清空dist目录的插件配置示例。

```javascript
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
module.exports = {
	plugins: [
        new CleanWebpackPlugin(),
      ]
};
```

插件也可以传入选项，一般在实例化时进行传入。

```javascript
new MiniCssPlugin({
	filename: 'styles/[name].[contenthash:8].css',
  chunkFilename: 'styles/[name].[contenthash:8].css'
})
```

## 提取公共代码

Webpack4中提取公共代码只需要配置optimization.splitChunks即可。

```javascript
optimization: {
	splitChunks: {
  	cacheGroups: {
    	vendor: { // 名为vendor的chunk
      	name: "vendor",
        test: /[\\/]node_modules[\\/]/,
        chunks: 'all',
        priority: 10
      },
      	styles: { // 名为styles的chunk
        name: 'styles',
        test: /\.css$/,
        chunks: 'all'
      }
    }
  }
},
```

+ cacheGroups 缓存组
+ name chunk的名称
+ test 加载的模块符合该正则时被打包到该chunk
+ chunks 模块的范围，有initial(初始模块),async(按需加载模块),all(全部模块)

上面的例子中将node_modules中的js打包为vendor，以css结尾的打包为styles

## 常用的loader和plugin

### css-loader

>  加载css文件

```javascript
{
  test:/\.css$/
  loader:['css-loader']
}
```

### less-loader

> 加载less文件，一般需要配合css-loader

```javascript
{
  test:/\.less$/,
  loader:['css-loader','less-loader']
}
```

### file-loader

> 将文件拷贝到输出文件夹，并返回相对路径。一般常用在加载图片

```javascript
{
  test:/\.(png|gif|jpg)/,
  use:[
  	{
      loader:'file-loader',
      options:{
        name:'images/[name].[hash:8].[ext]'
      }
    }    
  ]
}
```

### babel-loader

> 转换ES2015+代码到ES5

```javascript
{
  test:/\.js$/,
  exclude: /(node_modules|bower_components)/, // 排除指定的模块
  use:[
    {
      loader:'babel-loader',
      options:{
        presets:['@babel/preset-env']
      }
    }
  ]
}
```

### ts-loader

> 转换Typescript到Javascript

```javascript
{
  test:/\.ts/,
  loader:'ts-loader'
}
```

### html-webpack-plugin

> 简化HTML的创建，该插件会自动将当前打包的资源(如JS、CSS)自动引用到HTML文件

```javascript
const HtmlWebpackPlugin = require('html-webpack-plugin');
module.exports =  {
  plugins:[
    new HtmlWebpackPlugin()
  ]
};
```

### clean-webpack-plugin

> 打包之前清理dist目录

```javascript
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
module.exports =  {
  plugins:[
    new CleanWebpackPlugin()
  ]
};
```

### mini-css-extract-plugin

> 提取、压缩CSS，需要同时配置loader和plugin

```javascript
const MiniCssPlugin = require('mini-css-extract-plugin');
module.exports =  {
  module:{
    rules:[
            {
                test: /\.less$/,
                use: [MiniCssPlugin.loader, 'css-loader', 'less-loader']
            },
            {
                test: /\.css$/,
                use: [MiniCssPlugin.loader, 'css-loader']
            },
    ]
  },
  plugins:[
    new MiniCssPlugin({
			filename: 'styles/[name].[contenthash:8].css',
      chunkFilename: 'styles/[name].[contenthash:8].css'
    }),
  ]
};
```

## 实战

下面使用Webpack来配置一个传统多页面网站开发的示例。

### 目录结构

```
├── package.json
├── src
│   ├── about						关于页
│   │   ├── index.html
│   │   ├── index.js
│   │   └── style.less
│   ├── common
│   │   └── style.less
│   └── home						首页
│       ├── images
│       │   └── logo.png
│       ├── index.html
│       ├── index.js
│       └── style.less
├── webpack.config.js
```

### 使用到的npm包

```
"clean-webpack-plugin": "^3.0.0",
"css-loader": "^3.2.1",
"exports-loader": "^0.7.0",
"extract-text-webpack-plugin": "^4.0.0-beta.0",
"file-loader": "^5.0.2",
"html-webpack-plugin": "^3.2.0",
"html-withimg-loader": "^0.1.16",
"less": "^3.10.3",
"less-loader": "^5.0.0",
"mini-css-extract-plugin": "^0.8.0",
"normalize.css": "^8.0.1",
"script-loader": "^0.7.2",
"style-loader": "^1.0.1",
"url-loader": "^3.0.0",
"webpack": "^4.41.2",
"webpack-cli": "^3.3.10",
"webpack-dev-server": "^3.9.0",
"zepto": "^1.2.0"
```

### 配置入口点

由于是传统多页网站，每个页面都需要单独打包一份JS，因此**每个页面需要一个入口**。

```javascript
entry: { // 入口配置，每个页面一个入口JS
        home: './src/home/index', // 首页
        about: './src/about/index' // 关于页
}
```

### 配置输出

本例我们不进行CDN部署，因此输出点配置比较简单。

```javascript
output: { // 输出配置
  path: path.resolve(__dirname, 'dist'), // 输出资源目录
  filename: 'scripts/[name].[hash:8].js', // 入口点JS命名规则
  chunkFilename: 'scripts/[name]:[chunkhash:8].js', // 公共模块命名规则 
  publicPath: '/' // 资源路径前缀
}
```

### 配置开发服务器

本地开发时不需要每次都编译完Webpack再访问，通过webpack-dev-server，我们可以边开发变查看效果，文件会实时编译。

```javascript
devServer: {
        contentBase: './dist', // 开发服务器配置
        hot: true // 热加载
},
```

### 配置loader

本例中没有使用ES6进行编程，但是引用了一个非CommonJS的js模块`Zepto`，传统用法中在HTML页面引入Zepto就会在window下挂载全局对象Zepto。但是在Webpack开发中不建议使用全局变量，否则模块化的优势将受到影响。

通过使用exports-loader和script-loader，我们可以将Zepto包装为CommonJS模块进入导入。

```javascript
module: {
        rules: [
            {
                test: require.resolve('zepto'),
                loader: 'exports-loader?window.Zepto!script-loader' // 将window.Zepto包装为CommonJS模块
            },
            {
                test: /\.less$/,
                use: [MiniCssPlugin.loader, 'css-loader', 'less-loader']
            },
            {
                test: /\.css$/,
                use: [MiniCssPlugin.loader, 'css-loader']
            },
            {
                test: /\.(png|jpg|gif)$/,
                use: [
                    {
                        loader: 'file-loader',
                        options: {
                            name: 'images/[name].[hash:8].[ext]'
                        }
                    }
                ]
            },
            {
                test: /\.(htm|html)$/i,
                loader: 'html-withimg-loader'
            }
        ]
    },
```

### 配置optimization

主要进行公共模块的打包配置。

```javascript
optimization: {
        splitChunks: {
            cacheGroups: {
                vendor: {
                    name: "vendor",
                    test: /[\\/]node_modules[\\/]/,
                    chunks: 'all',
                    priority: 10, // 优先级
                },
                styles: {
                    name: 'styles',
                    test: /\.css$/,
                    chunks: 'all'
                }
            }
        }
    },
```

### 配置plugin

```javascript
plugins: [
        new CleanWebpackPlugin(), // 清理发布目录
        new HtmlWebpackPlugin({
            chunks: ['home', 'vendor', 'styles'], // 声明本页面使用到的模块，有主页，公共JS以及公共CSS
            filename: 'index.html', // 输出路径，这里直接输出到dist的根目录，也就是dist/index.html
            template: './src/home/index.html', // HTML模板文件路径
            minify: { 
                removeComments: true, // 移除注释
                collapseWhitespace: true // 合并空格
            }
        }),
        new HtmlWebpackPlugin({
            chunks: ['about', 'vendor', 'styles'],
            filename: 'about/index.html', // 输出到dist/about/index.html
            template: './src/about/index.html',
            minify: {
                removeComments: true,
                collapseWhitespace: true
            }
        }),
        new MiniCssPlugin({
            filename: 'styles/[name].[contenthash:8].css',
            chunkFilename: 'styles/[name].[contenthash:8].css'
        }),
        new webpack.NamedModulesPlugin(), // 热加载使用
        new webpack.HotModuleReplacementPlugin() // 热加载使用
    ]
```

### 示例代码

部分示例代码如下:

```javascript
// src/about/index.js
const $ = require('zepto');
require('normalize.css');
require('../common/style.less');
require('./style.less');

$('#about').on('click', function () {
    alert('点击了about按钮');
});
```

和传统的JS有点不太一样，多了一些css的require，前面说过，webpack把所有资源当做JS模块，因此这是推荐的做法。

```html
<!--首页-->
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>首页</title>
</head>

<body>
    <ul>
        <li><a href="/">首页</a> </li>
        <li><a href="/about">关于</a></li>
    </ul>
    <div class="logo"></div>
    <button id="home">首页按钮</button>
</body>

</html>
```

页面中不再需要编写JS。

> 注意：html中使用<img />标签导入图片的编译，目前还没有好的解决办法，可以通过css background的形式进行处理

### 开发模式

开发模式下直接启用webpack-dev-server即可，会自动加载工作目录下的webpack.config.js

```
// package.json
"scripts": {
    "build": "webpack",
    "dev": "webpack-dev-server"
}
```

```bash
npm run dev
```

### 生产模式

生产模式下使用webpack编译，编译完成后输出最终文件。

```bash
npm run build
```

### 输出效果

```
├── about
│   └── index.html
├── images
│   └── logo.b15c113a.png
├── index.html
├── scripts
│   ├── about.3fb4aa0f.js
│   ├── home.3fb4aa0f.js
│   └── vendor:ed5b7d31.js
└── styles
    ├── about.71eb65e9.css
    ├── home.cd2738e6.css
    └── vendor.9df34e21.css
```

### 项目地址

项目已经托管到github，有需要的读者可以自取。

[https://github.com/xialeistudio/webpack-multipage-example](https://github.com/xialeistudio/webpack-multipage-example)