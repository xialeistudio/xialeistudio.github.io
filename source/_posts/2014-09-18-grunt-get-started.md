---
layout: post
title: Grunt快速上手
date: 2014-09-18 16:49:31.000000000 +08:00
type: post
published: true
status: publish
categories:
- Engineering
---

## 为什么要使用Grunt?
一句话：自动化。对于需要反复重复的任务，例如压缩（minification）、编译、单元测试、linting等，自动化工具可以减轻你的劳动，简化你的工作。当你正确配置好了任务，任务运行器就会自动帮你或你的小组完成大部分无聊的工作。
## 怎么使用Grunt?
1.grunt是基于nodejs的，所以请先安装nodejs和npm安装grunt   
2.新版本的grunt安装需要两步，终端执行   

```bash
npm install grunt-cli -g
```

3.进入项目目录，终端执行   

```bash
npm install grunt --save-dev
```

4.安装常用插件

```bash
npm install grunt-contrib-cssmin grunt-contrib-uglify grunt-contrib-watch --save-dev
```

5.项目目录

```
--dev
    |--js
        |-- jquery.js
        |-- main.js
    |--css
        |-- library.css
        |-- main.css
```

一个很简单的JS,CSS目录，很关键的任务在于如何定义Gruntfile.js文件（请在项目根目录下创建Gruntfile.js,大小写不能错）   
6.Gruntfile.js

```javascript
module.exports = function(grunt) {
    grunt.initConfig({
        cssmin: {
            site: {
                files: {
                    'build/css/site.css': ['dev/css/library.css', 'dev/css/main.css']
                }
            },
        },
        uglify: {
            site: {
                src: ['dev/js/jquery.js', 'dev/js/main.js'],
                dest: 'build/js/site.js'
            },

        },
        watch: {
            site: {
                files: ['dev/js/**.*', 'dev/css/**.*'],
                tasks: ['uglify:site', 'cssmin:site']
            }
        }
    });
    grunt.loadNpmTasks('grunt-contrib-cssmin');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.registerTask('site', ['watch:site']);
};
```

cssmin:

site为一个子任务

build/css/site.css 为合并压缩之后的css存放路径,该参数后面的数组为原始的css文件路径

uglify:

site为一个子任务

src数组为源JS文件

dest为合并压缩之后的js文件存放路径

watch

site为一个子任务

files数组为监听哪些文件的变化

tasks数组为如果文件变化则执行什么任务

grunt.loadNpmTasks 加载模块

grunt.registerTask 注册新任务

在项目目录下打开CMD工具，输入

```bash
grunt site
```

即开始执行监听，此时修改dev/js/main.js或者dev/css/main.css都会触发相应的事件。

## 结语
从此以后再也不用进行重复的压缩合并...etc等一些重复而乏味的工作了，交给grunt吧！