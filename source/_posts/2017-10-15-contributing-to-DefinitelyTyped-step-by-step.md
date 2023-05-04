---
title: 从零开始向DefinitelyTyped贡献代码
layout: post
categories:
- engineering
---

# 什么是DefinitelyTyped?
讲到DefinitelyTyped，我想做typescript开的人应该不会陌生，DefinitelyTyped是一个由typescript的发明者Microsoft维护的一个项目。
# 为什么会有DefinitelyTyped?
typescript是基于declation的一门语言，declation这个东西有点像C语言的头文件，就是变量、函数等等需要事先声明才能通过typescript编辑。为了方便开发者，也为了快速推广typescript，官方维护的这个项目给npm常用的一些包都定义了declations文件。   
既然是托管在github的OpenSource Project，那么只要是github的会员就可以提交PR（当然Merge与否还得看项目组成员）,由于社区的活跃使得该仓库越来越丰富。   
很荣幸，我也提交了几个npm包的declations在上面。
# 如何提交PR到DefinitelyTyped?
很多时候会遇到自己使用的npm包比较冷门，而DefinitelyTyped上面又没有，这时候虽然可以在本地定义，但是能够发布到DefinitelyTyped方便大家也是极好的，毕竟要拥抱开源嘛！   
官方的ReadMe中有`How can I contribute?`来告知开发者如何提交PR，但是需要英语基础，哈哈。
# Step By Step
## 环境搭建
### fork 项目
要提交PR的第一步是必须fork到自己的仓库，别人不会随便给你直接改，万一改挂了他们还得背锅.   
登录github,打开项目地址[DefinitelyTyped](https://github.com/DefinitelyTyped/DefinitelyTyped)
![fork](https://og5r5kasb.qnssl.com/upload/QQ20171015-024655.png)
fork完毕后，你会拥有一个自己的仓库地址，本文中我的地址是[https://github.com/xialeistudio/DefinitelyTyped](https://github.com/xialeistudio/DefinitelyTyped)
### clone 到本地
我本地的项目地址是**~/WebstormProjects/DefinitelyTyped**   
终端执行 `git clone https://github.com/xialeistudio/DefinitelyTyped`
### 安装npm依赖
终端执行 `cd ~/WebstormProjects/DefinitelyTyped && yarn`

## SourceTree
本文使用SourceTree配合git flow来进行项目管理。
1. 下载soucetree [下载地址](https://www.sourcetreeapp.com)
2. 安装sourcetree，期间需要登录。
3. 用sourcetree打开刚才克隆的项目。
![p1](https://og5r5kasb.qnssl.com/upload/QQ20171015-030606.png)
4. 点击菜单栏【仓库】->【git-flow或hg flow】->【初始化仓库】

## 开始开发
本文将以[koa2-cors](https://www.npmjs.com/package/types/koa2-cors)为例提交PR。
1. 使用sourcetree的git-flow创建feature
![p2](https://og5r5kasb.qnssl.com/upload/QQ20171015-030911.png)
2. 分支名称填写**koa2-cors**   
![p3](https://og5r5kasb.qnssl.com/upload/QQ20171015-031005.png)
3. 这时候已经可以编码了。我用的vscode，轻量，建议大家也用这个，webstorm打开这个项目就卡死了。
4. 安装定义文件生成工具，终端执行**npm install -g dts-gen**
5. 生成项目文件，终端执行**dts-gen --dt --name koa2-cors --template module**
6. 这个时候在**types/koa2-cors**目录下就是我们需要编辑的文件了。如果编写定义文件不在本文范畴，有需要的朋友可以去tslang官网看看手册。
7. 开始编辑**index.d.ts**，完整定义如下，记得改自己的个人信息:   
    ```typescript
    // Type definitions for koa2-cors 2.0
    // Project: https://github.com/zadzbw/koa2-cors#readme
    // Definitions by: xialeistudio <https://github.com/xialeistudio>
    // Definitions: https://github.com/DefinitelyTyped/DefinitelyTyped

    import * as Koa from 'koa';

    declare namespace cors {
        interface Options {
            origin?: any;
            exposeHeaders?: string[];
            maxAge?: number;
            credentials?: boolean;
            allowMethods?: string[];
            allowHeaders?: string[];
        }
    }

    declare function cors(options?: cors.Options): Koa.Middleware;

    export = cors;
    ```
8. 编写单元测试文件**koa2-cors-tests.ts**，测试就是写上样板代码即可，只要能通过编译就行。   
    ```typescript
    import * as Koa from 'koa';
    import * as cors from 'koa2-cors';

    const app = new Koa();
    app.use(cors({
        origin: function (ctx: Koa.Context) {
            if (ctx.url === '/test') {
                return false;
            }
            return '*';
        },
        exposeHeaders: ['WWW-Authenticate', 'Server-Authorization'],
        maxAge: 5,
        credentials: true,
        allowMethods: ['GET', 'POST', 'DELETE'],
        allowHeaders: ['Content-Type', 'Authorization', 'Accept'],
    }));
    app.listen(3000);
    ```
9. 启动单元测试，终端执行**npm run test**，如果没有报错，即可进行提交流程，否则要修好错误才能提交。很幸运，单元测试通过：   
![p4](https://og5r5kasb.qnssl.com/upload/QQ20171015-032934.png)
10. commit，终端执行**git add . && git commit -m "add koa2-cors definition"**
11. 使用sourcetree创建PR   
![p4](https://og5r5kasb.qnssl.com/upload/QQ20171015-033135.png)
12. 点击**在网上创建拉取请求**   
![p5](https://og5r5kasb.qnssl.com/upload/QQ20171015-033252.png)
13. 此时会自动打开github网页进行PR操作   
14. 编辑PR提交模板，这个根据实际情况编写即可，注意下方的**If xxx**，这个是不同提交类型需要填写的。本文是新增，所以选择**add**   
![p6](https://og5r5kasb.qnssl.com/upload/QQ20171015-033524.png)
15. 点击**Create Pull Request**，此时会进行**travis**自动化测试流程，如果有错误需要点进去看到错误信息之后修正，很不幸。我们的第一次提交失败：   
![p7](https://og5r5kasb.qnssl.com/upload/QQ20171015-034009.png)
16. 点击**Details**进行详细错误页面，找到**=== Error ===**   
![p8](https://og5r5kasb.qnssl.com/upload/QQ20171015-034114.png)
17. 可以发现我们错误是**" Expected `"strictFunctionTypes": true` or `"strictFunctionTypes": false`**,这个是**tsconfig.json**导致的问题，感觉是个历史遗留问题，因为使用的是默认创建的模板，不过为了提交PR，还是要手动修复。   
编辑**types/koa2-cors/tsconfig.json**，在**compilerOptions**下添加，代码如下：   
    ```json
    {
        "compilerOptions": {
            "module": "commonjs",
            "lib": [
                "es6"
            ],
            "noImplicitAny": true,
            "noImplicitThis": true,
            "strictNullChecks": true,
            "baseUrl": "../",
            "strictFunctionTypes": false,
            "typeRoots": [
                "../"
            ],
            "types": [],
            "noEmit": true,
            "forceConsistentCasingInFileNames": true
        },
        "files": [
            "index.d.ts",
            "koa2-cors-tests.ts"
        ]
    }
    ```
18. commit，终端执行**git add . && git commit -m "strictFunctionTypes" && git push**，不需要再创建PR了，当你在该分支PUSH的时候，远端会自动触发自动化测试任务。
19. 成功通过测试后，就可以等待官方人员过来review了。一般来说都会通过并且合并到master中去。