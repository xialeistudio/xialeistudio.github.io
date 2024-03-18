---
slug: gulp-workflow
title: 使用gulp来构建你的前端自动化工作流
date: 2015-03-16 17:43:07.000000000 +08:00
categories:
- Engineering
---
之前用的Grunt，不过有时候Grunt确实用起来不爽，进来找到一款叫gulp.js的前端构建工具，当然，也是基于node.js的。
## 安装

```bash
npm install gulp --save-dev
npm install del gulp-concat gulp-cssmin gulp-uglify --save-dev
```

## 配置
配置gulpfile.js，如果工作目录下没有该文件，请新建gulpfile.js，以下为一个常用的参考代码:

```javascript
/**
 * @author xialei <xialeistudio@gmail.com>
 */
(function () {
    "use strict";
    /**
     * 加载插件
     * @type {exports}
     */
    var gulp = require('gulp');
    var del = require('del');
    var cssmin = require('gulp-cssmin');
    var concat = require('gulp-concat');
    var uglify = require('gulp-uglify');

    /**
     * 清空目录的命令
     */
    gulp.task('clean', function () {
        del(['build']);
    });
    gulp.task('css', function () {
        /**
         * 加载源代码
         */
        return gulp.src([
            'bower_components/bootstrap/dist/css/bootstrap.min.css',
            'bower_components/font-awesome/css/font-awesome.min.css',
            'css/style.css'
        ])
        /**
         * 压缩css
         */
            .pipe(cssmin())
        /**
         * 连接压缩后的css
         */
            .pipe(concat('style.css'))
        /**
         * 输出到目标目录
         */
            .pipe(gulp.dest('build/css'))
    });
    gulp.task('js', function () {
        return gulp.src([
        /**
         * 加载源代码
         */
            'bower_components/angular/angular.min.js',
            'bower_components/angular-sanitize/angular-sanitize.min.js',
            'js/main.js'])
        /**
         * 压缩Js
         */
            .pipe(uglify())
        /**
         * 合并js
         */
            .pipe(concat('main.js'))
        /**
         * 输出到目标目录
         */
            .pipe(gulp.dest('build/js'))
    });
    gulp.task('img', function () {
        /**
         * 加载源文件
         */
        return gulp.src([
            'img/*.*'
        ])
        /**
         * 输出到目标目录
         */
            .pipe(gulp.dest('build/img'));
    });

    /**
     * 定义默认任务，此任务依赖于 clean,img,css,js，所以在执行
     * 本任务时会按顺序先执行依赖任务
     */
    gulp.task('default', ['clean', 'img', 'css', 'js']);
})();
```

## 执行编译

```bash
gulp
```