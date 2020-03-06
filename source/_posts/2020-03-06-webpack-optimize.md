---
title: Webpack4不求人(3) ——性能优化
date: 2020-03-06 12:00:00
categories:
- frontend
- javascript
---

## 限定Webpack处理文件范围

项目比较小的情况下Webpack的性能问题几乎可以忽略，但是一旦项目复杂度上升，Webpack会有额外的性能损失需要我们进行优化。

通过前面内容的学习我们可以知道Webpack主要干下面这些事情：

1. 通过entry指定的入口脚本进行依赖解析。
2. 找到文件后通过配置的loader对其进行处理。

因此，我们可以从这方面入手进行优化，减少Webpack搜索文件的范围，减少不必要的处理。

###  loader配置

在之前的内容中介绍过loader可以使用test、include、exclude配置项来匹配需要Loader处理的文件，因此推荐给每个loader定义test之后还定义include或exclude。

```javascript
module.exports = {
  module:{
  	rules:[
      {
        test:/\.js$/,
        use:'babel-loader',
        include: path.resolve(__dirname, 'src'), // 只处理src目录下的js文件
      }
    ]
  }
};
```

### resolve.extensions配置

导入未添加扩展名的模块时，Webpack会通过resolve.extensions后缀去检查文件是否存在。由于resolve.extensions是一个数组，如果数组项比较多，正确的后缀放置得越靠后，Webpack尝试次数就会越多，影响到性能。

因此配置resolve.extensions时需要遵守以下规则：

+ 尽量减少后缀列表，不要将不可能存在的文件后缀配置进来
+ 出现频率越高的后缀尽量写到前面，比如可以将.js写在第一个
+ 业务代码中导入模块时，可以手动加上后缀导入，省去Webpack查找过程

###  module.noParse配置

module.noParse可以告诉Webpack忽略未采用模块系统文件的处理，可以有效地提高性能。比如常见的jQuery非常大，又没有采用模块系统，让Webpack解析这类型文件完全是浪费性能。

因此我们可以配置如下的module.noParse:

```javascript
module.exports = {
  module:{
  	noParse:[/jQuery/]
  }
};
```

## IgnorePlugin

在导入模块时，IgnorePlugin可以忽略指定模块的生成。比如moment.js在导入时会自动导入本地化文件，一般情况下几乎不使用而且又比较大，此时可以通过IgnorePlugin忽略对本地化文件的生成，减小文件大小。

```javascript
module.exports = {
  plugins:[
    new webpack.IgnorePlugin(/\.\/local/, /moment/)
  ]
};
```

## DllPlugin

使用过Windows操作系统的读者应该会经常看到以.dll扩展名的文件，这些文件叫做动态链接库，包含了其他程序或动态链接库的函数和数据。

Webpack的DllPlugin的思想是类似的，先将公共模块打包为独立的Dll模块，然后在业务代码中直接引用这些模块。采用DllPlugin之后会大大提升Webpack构建速度，原因在于，包含大量复用模块的动态链接库只需要编译一次，之后的构建中会直接引用这些构建好的模块。

在Webpack中使用动态链接库有以下两个步骤：

1. 通过webpack.DllPlugin插件打包出Dll库
2. 通过webpack.DllReferencePlugin引用打包好的Dll库

下面以React项目为例进行说明。

Dll库需要单独构建，因此我们需要一份单独的配置Webpack文件。

1.新建webpack.dll.config.js

```javascript
const webpack = require('webpack');

module.exports = {
	entry:{
  	react: ['react', 'react-dom']
  },
  output:{
    filename: '_dll_[name].js', // 输出的文件名
    path: path.resolve(__dirname, 'dist'), // 输出到dist目录
    library: '_dll_[name]'
  },
  plugins: [
    // name要等于output.library里的name
    new webpack.DllPlugin({
      name: "_dll_[name]",
      path: path.resolve(__dirname, "dist", "manifest.json") // 清单文件路径
    })
  ]
};
```

2.编辑webpack.config.js

```javascript
const webpack = require('webpack');

module.exports = {
	entry: './src/main',
  output:{
    filename: '[name].js', // 输出的文件名
    path: path.resolve(__dirname, 'dist'), // 输出到dist目录
  },
  plugins: [
    // 传入manifest.json
    new webpack.DllReferencePlugin({
      manifest: path.resolve(__dirname, "dist", "manifest.json") // 清单文件路径
    })
  ]
};
```

3.添加构建命令

```json
{
  "scripts":{
 		"build-dll":"webpack --config webpack.dll.config.js",
    "build":"webpack"
  }
}
```

4.构建Dll

```bash
npm run build-dll
```

5.构建应用

```bash
npm run build
```

> Dll需要先构建，否则应用将构建失败

## HappyPack

Webpack默认情况下是单进程执行的，因此无法利用多核优势，通过HappyPack可以变成多进程构建，从而提升构建速度。下面我们一起来看看如何使用happypack来加速构建。

1.安装happypack

```bash
npm isntall happypack
```

2.编辑配置文件，需要将Loader配置到HappyPack插件中，由HappyPack对Loader进行调用。

```javascript
const HappyPackPlugin = require('happypack');
const path = require('path');

module.exports = {
	entry: './src/main',
  output:{
    path: path.resolve(__dirname, 'build'),
    filename:'[name].js'
  },
  module:{
    rules:[
      {
        test:/\.js$/,
        use:'happypack/loader?id=js', // 配置id为js
        include:[
          path.resolve(__dirname,'src')
        ]
      },
      {
        test:/\.scss$/,
        use:'happypack/loader?id=scss', // 配置id为scss
        include:[
          path.resolve(__dirname,'src')
        ]
      },
      {
        test:/\.css$/,
        use:'happypack/loader?id=css', // 配置id为css
        include:[
          path.resolve(__dirname,'src')
        ]
      }
    ]
  },
  plugins:[
    new HappyPackPlugin({
      id:'js', // id为js的loader配置
      use:[
        {
          loader:'babel-loader',
          options:{
            plugins:['@babel/transform-runtime'],
            presets:['@babel/env']
          }
        }
      ]
    }),
    new HappyPackPlugin({
      id:'scss', // id为scss的loader配置
      use:['style-loader','css-loader','sass-loader']
    }),
    new HappyPackPlugin({
      id:'css', // id为css的loader配置
      use:['style-loader','css-loader']
    }),
  ]
};
```

## Tree-Shaking

Tree-Shaking原始的本意是”摇动树“，这样就会将一些分支”摇掉“，从而减少主干大小。而Webpack中的Tree-Shaking是类似的，在Webpack项目中，有一个入口文件，相当于树的主干，入口文件又依赖了许多模块。实际开发中，虽然依赖了某个模块，但其实只使用了其中的部分代码，通过Tree-Shaking，可以将模块中未使用的代码剔除掉，从而减少构建结果的大小。

> 注意：只有使用ES6模块系统的代码，在mode为production时，Tree-Shaking才会生效。因此，在编写代码时尽量使用import/export的方式。

## 按需加载

在开发中，我们一般会将业务代码打包为app.js，其他第三方依赖打包为vendor.js。这样会有一个比较大的问题，如果依赖的第三方模块过多，vendor.js会越来越大，而在浏览器加载时需要完全加载完vendor.js才可以，这样就会造成无谓的等待，因为我们当前页面可能只使用了一部分代码。此时可以使用Webpack来实现按需加载，只有在真正用到这个模块时才会加载相应的js。

比如基于echarts开发了一个数据可视化页面，可以在这个路由组件下面使用异步的方式加载echarts的代码：

```javascript
import('echarts').then(modules => {
  const echarts = modules.default;
  const chart = echarts.init(document.querySelector('#chart'));
});
```

不过使用按需加载时，构建代码中会包含Promise调用，因此低版本浏览器需要注入Promise的polyfill实现。

## 提取公共代码

Webpack4中可以将多个公共模块打包一份，减少代码冗余，Webpack4之前的版本是使用webpack内置的CommonsChunkPlugin实现的，Webpack4直接配置`optimization`即可。

```javascript
module.exports = {
  optimization:{
    splitChunks:{
      cacheGroups:{
        common:{ // 应用代码中公共模块
          chunks: 'all',
          // 最小公共模块引用次数
          minChunks: 2
        },
        vendor:{ // node_modules中第三方模块
					test: /node_modules/,
          chunks: 'all',
          minChunks: 1
        }
      }
    }
  }
};
```

第三方库代码的变更一般比较少(通过package.json的版本可以指定依赖版本)，因此构建出来的vendor.js基本不会变就可以利用浏览器的缓存机制进行缓存。

而应用代码的变更是比较频繁的，因此单独打包为common.js，浏览器可以单独缓存，如果应用代码发生变更，浏览器只用重新下载common.js文件，而不用重新下载vendor.js。

## 热更新

HMR(Hot Module Replacement)是Webpack提供的常用功能之一，它允许在运行时对模块进行修改，而无需刷新整个页面(LiveReload需要刷新页面才能加载)，这样有以下优势：

+ 保留应用状态，比如使用Vue/React时如果使用LiveReload，组件状态全部丢失，而HMR不会
+ 只更新变更的内容，节省开发时间

使用以下配置即可打开内置的HMR功能：

```javascript
const webpack = require('webpack');

module.exports = {
	devServer: {
    hot: true, // 启用热加载
    contentBase: './dist',
  },
  plugins:[
		new webpack.NamedModulesPlugin(), // 打印更新的模块路径
    new webpack.HotModuleReplacementPlugin() // 热更新插件
  ]
};
```

## 小结

本文我们对Webpack4最常用的性能优化技术进行了学习，这些优化方法对业务代码的侵入性非常小（只有按需加载优化会要求使用import()函数进行加载），在实际的开发中，可以结合这些技术进行针对性的优化，比如开发时编译慢，可能就需要使用HappyPack插件进行多进程编译以加快编译速度等等。

![0.jpeg](https://static.ddhigh.com/blog/2019-10-22-102654.jpg)