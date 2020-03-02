# Webpack4不求人(2) ——手把手搭建TypeScript+React16+ReactRouter5同构应用脚手架

## 同构应用

使用同一份应用代码，同时提供浏览器环境和服务器环境下的应用，解决传统浏览器单页应用的两个顽固问题：

+ 不利于SEO，浏览器环境代码是在客户端渲染，大部分爬虫都只能爬到一个空白的入口文件
+ 代码在浏览器渲染，低端机可能会卡顿

接下来我们一起从零开始搭建基于Webpack的React同构应用脚手架。

## SSR流程

1. Web应用构建完成后输出CSS、JS和HTML
2. SSR应用构建完成后输出一个CommonJs模块文件，可以将虚拟DOM在服务端渲染为HTML字符串
3. Node.js新建HTTP服务器，收到请求后调用SSR模块导出的render函数输出HTML到客户端

## 初始化项目

```bash
mkdir react-ssr-example
cd react-ssr-example
yarn init -y

yarn add webpack webpack-cli webpack-dev-server -D # 安装Webpack
yarn add react react-dom react-router-dom # 安装React
yarn add @types/react @types/react-dom @types/react-router-dom -D # 安装React声明文件
yarn add express # 安装express
yarn add css-loader sass-loader node-sass mini-css-extract-plugin # 安装CSS相关模块
yarn add ts-loader typescript # 安装TypeScript
yarn add html-webpack-plugin # 安装HTML处理插件
```

## 目录结构

脚手架的完整目录如下：(这些文件一步步都会有)

```
|----build # 构建结果目录
		|----styles # 样式
				|----main.css
		|----bundle.ssr.js # SSR应用文件
		|----bundle.web.js # Web应用文件
		|----index.html # Web应用入口HTML
|----src # 应用源码
		|----home # 首页组件
				|----index.scss # 首页SCSS
				|----index.tsx # 首页组件
		|----signin # 登录页组件
				|----index.scss # 登录页SCSS
				|----index.tsx # 登录页组件
		|----App.tsx # 应用路由设置
		|----index.html # Web应用入口HTML
		|----main.ssr.tsx # SSR入口文件
		|----main.web.tsx # Web入口文件
|----index.js #　express服务器入口
|----package.json
|----tsconfig.json # TypeScript配置文件
|----webpack.config.js # Web应用webpack配置
|----webconfig.ssr.config.js # SSR应用Webpack配置
```

## 工具配置

1.TypeScript配置，新建tsconfig.json

```json
{
    "compilerOptions": {
      "target": "es5", 
      "module": "commonjs", 
      "jsx": "react", 
      "strict": true,
      "lib": [
        "DOM"
      ],
      "esModuleInterop": true
    },
    "include": [
      "./src/**/*.ts",
      "./src/**/*.tsx"
    ],
    "exclude": [
      "node_modules"
    ]
  }
```

主要是添加了jsx设置和include设置

2.Web环境webpack配置，新建webpack.config.js

```javascript
const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const MiniCssPlugin = require('mini-css-extract-plugin');

module.exports = {
    entry: './src/main.web', // 入口文件
    output: {
        path: path.resolve(__dirname, 'build'), // 输出目录
        filename: 'bundle.web.js' // 输出文件
    },
    module: {
        rules: [
            {
                test: /\.tsx?$/, // ts文件处理
                use: 'ts-loader'
            },
            {
                test: /\.scss$/, // scss文件处理
                use: [MiniCssPlugin.loader, 'css-loader', 'sass-loader']
            },
            {
                test: /\.css$/, // css文件处理
                use: [MiniCssPlugin.loader, 'css-loader']
            }
        ]
    },
    plugins: [
        new HtmlWebpackPlugin({
            chunks: ['main'], // chunk名称，entry是字符串类型，因此chunk为main
            filename: 'index.html', // 输出到build目录的文件名
            template: 'src/index.html' // 模板路径
        }),
        new MiniCssPlugin({
            filename: 'styles/[name].[contenthash:8].css', // 输出的CSS文件名
            chunkFilename: 'styles/[name].[contenthash:8].css'
        })
    ],
    resolve: {
        extensions: ['.ts', '.tsx', '.js', '.json'] // 添加ts和tsx后缀
    }
};
```

3.SSR环境Webpack配置，新建webpack.ssr.config.js

```javascript
const path = require('path');
const MiniCssPlugin = require('mini-css-extract-plugin');

module.exports = {
    entry: './src/main.ssr',
    target: 'node', // 必须指定为Node.js，否则会打包Node.js内置模块
    output: {
        path: path.resolve(__dirname, 'build'),
        filename: 'bundle.ssr.js',
        libraryTarget: 'commonjs2' // 打包为CommonJs模块才能被Node.js加载
    },
    module: {
        rules: [
            {
                test: /\.tsx?$/,
                use: 'ts-loader'
            },
            {
                test: /\.scss$/,
                use: [MiniCssPlugin.loader, 'css-loader', 'sass-loader']
            },
            {
                test: /\.css$/,
                use: [MiniCssPlugin.loader, 'css-loader']
            }
        ]
    },
    plugins: [
        new MiniCssPlugin({
            filename: 'styles/[name].[contenthash:8].css',
            chunkFilename: 'styles/[name].[contenthash:8].css'
        })
    ],
    resolve: {
        extensions: ['.ts', '.tsx', '.js', '.json']
    }
};
```

4.package.json添加npm命令

```json
{
    "scripts": {
    "build": "webpack",
    "start": "webpack-dev-server",
    "build-ssr": "webpack --config webpack.ssr.config.js"
  }
}
```

## 应用编码

src/home/index.tsx

```tsx
import React from 'react';
import './index.scss';

export default class Home extends React.Component {
    render() {
        return (
            <div className="main">首页</div>
        )
    }
}
```

src/home/index.scss

```scss
.main {
    color: red;
}
```

src/signin/index.tsx

```tsx
import React from 'react';
import { withRouter } from 'react-router-dom';

function SignIn(props: any) {
    return (
        <button onClick={() => props.history.replace('/')}>登录</button>
    )
}
export default withRouter(SignIn);
```

src/App.tsx

```tsx

import React from 'react';
import { Switch, Route, Link } from 'react-router-dom'; // router

// 导入页面组件
import Home from './home';
import SignIn from './signin';

// 导出路由组件配置
export default function App() {
    return (
        <Switch>
            <Route path="/signin" component={SignIn} />
            <Route path="/" component={Home} />
        </Switch>
    )
}
```

index.html

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hello World</title>
</head>
<body>
    <div id="app"></div>
</body>
</html>
```

src/main.ssr.tsx

```tsx
import React from 'react';
import { StaticRouter, Link } from 'react-router-dom';
import { renderToString } from 'react-dom/server';
import App from './App'; // 将路由组件导入进来

export function render(req: any) { // 导出一个渲染函数，根据请求链接进行分发
    const context = {};
    const html = renderToString(
        <StaticRouter location={req.url} context={context}>
            <header>
                <nav>
                    <ul>
                        <li><Link to="/">首页</Link></li>
                        <li><Link to="/signin">登录</Link></li>
                    </ul>
                </nav>
            </header>
            <App />
        </StaticRouter>
    );
    return [html, context]; // 导出context和html渲染结果
}
```

src/main.web.tsx

```tsx
import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter, Link } from 'react-router-dom';
import App from './App';

ReactDOM.render( // 渲染路由
    <BrowserRouter>
        <header>
            <nav>
                <ul>
                    <li><Link to="/">首页</Link></li>
                    <li><Link to="/signin">登录</Link></li>
                </ul>
            </nav>
        </header>
        <App />
    </BrowserRouter>, document.querySelector('#app'))
```

index.js

```javascript
const express = require('express'); // 加载express
const { render } = require('./build/bundle.ssr'); // 加载ssr

const app = express();

app.use(express.static('.')) // 静态资源配置


app.get('/*', (req, res) => { // 所有请求都走这里处理，必须加*
    const [html, context] = render(req)
    console.log(context) // context目前没发现啥用处
    res.send(`
    <html>
    <head>
        <meta charset="UTF-8">
        <title>SSR</title>
        <link href="build/styles/main.8f173ff5.css" rel="stylesheet">
    </head>
    <body>
        <div id="app">${html}</div>
        <script src="build/bundle.web.js"></script>
    </body>
    </html>
    `);
    console.log(context)
});

app.listen(8080)
```

注意：

+ 静态资源配置必须在最上面
+ app.get('/*')必须有*号
+ HTML字符串必须手动引入CSS和Web构建结果

## 执行构建

```bash
npm run build # 构建Web
npm run build-ssr #　构建SSR
node index.js # 启动Express服务器
```

## 查看结果

首页样式

![image-20200302173258430](https://static.ddhigh.com/blog/2020-03-02-093301.png)

首页代码

![image-20200302173322601](https://static.ddhigh.com/blog/2020-03-02-093323.png)

登录页样式

![image-20200302173344488](https://static.ddhigh.com/blog/2020-03-02-093346.png)

登录页代码

![image-20200302173405907](https://static.ddhigh.com/blog/2020-03-02-093408.png)

## 源码地址

Https://github.com/xialeistudio/react-ssr-example

