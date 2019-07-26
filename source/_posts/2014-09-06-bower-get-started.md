---
layout: post
title: bower快速入门
date: 2014-09-06 20:06:58.000000000 +08:00
type: post
published: true
status: publish
categories:
- frontend
tags:
- bower
meta:
  _edit_last: '1'
  views: '5151'
  _wp_old_slug: bower%e5%bf%ab%e9%80%9f%e5%85%a5%e9%97%a8
---
## 简介
bower是twitter的又一个开源项目，使用nodejs开发，用于web包管理。如果越来越多得开源项目都托管在github上，bower只需要将github上项目加上一个配置文件既可以使用bower方式使用安装包。作为包管理，bower能提供添加新web包，更新web包，删除web包，发布web包功能，管理包依赖。web包通常认为由html+css+javascript构成。
## 安装bower

```bash
npm install bower -g
```

请确保你有Nodejs环境  

在项目目录中运行

```bash
bower install jquery
```

运行成功之后项目中会多出components文件夹，文件夹中jquery文件夹，jquery文件夹里面就有最新的jquery文件。

这还不能说明他NB的地方，试想下面的场景，jQuery升级了，是不是再down一次jQuery呢？bower可以这样做：

```bash
bower update jquery
```

就可以自动升级到最新版的jquery了。

再假设我们需要使用bootstrap，bootstrap可不是一个文件，有css,js还有图片。js还依赖于jQuery，如果使用bower：

```bash
bower install bootstrap
```

bower会自动从github上down最新的代码，而且，会自动将依赖包jquery也down一次。

如果你发布程序的时候不想把一些依赖的库发布上去（主要原因是太大了 - - ），可以在项目根目录下生成一个 bower.json 文件用来管理依赖。

在项目目录下执行

```bash
bower init
```

按照提示操作就好，这样子会生成一个bower文件

安装 jquery

```bash
bower install jquery --save
```

这样子 bower.json 文件就会写入一个 Jquery的依赖项

别人只要在项目目录下输入

```bash
bower install
```

就会自动安装了