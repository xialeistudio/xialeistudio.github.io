---
title: 使用RSA在PHP和NodeJs中进行加密数据通信
layout: post
categories:
- backend
- php
tags:
- openssl
---
RSA算法是目前用的最多的非对称加密算法，文本将基于openssl在nodejs和php中进行加密数据通信。

## 生成密钥对
```bash
openssl
genrsa -out private.key 2048
rsa -in private.key -pubout -out public.key
```
执行完命令后，可以在当前目录看到:
+ public.key 公钥
+ private.key 私钥

## NodeJs服务器
本文使用koa2来构建一个基于openssl加密方案的http服务器。
源码使用typescript进行开发。
### 安装依赖
```bash
npm init -y
npm install typescript koa koa-router @types/node @types/koa @types/koa-router --save
```
最终的*package.json*内容如下：

```json
{
  "name": "openssl-demo",
  "version": "1.0.0",
  "description": "",
  "main": "index.js",
  "scripts": {
    "build": "tsc -w",
    "start": "node index.js"
  },
  "keywords": [],
  "author": "",
  "license": "ISC",
  "dependencies": {
    "@types/koa": "^2.0.39",
    "@types/koa-router": "^7.0.22",
    "@types/node": "^8.0.2",
    "koa": "^2.3.0",
    "koa-router": "^7.2.1",
    "typescript": "^2.3.4"
  }
}
```
### 开始编码*index.ts*:

```typescript
import * as crypto from 'crypto';
import * as constants from 'constants';
import * as Koa from 'koa';
import * as KoaRouter from 'koa-router';
import * as fs from 'fs';

class Server {
    app: Koa;

    static bootstrap() {
        return new Server();
    }

    constructor() {
        this.app = new Koa();
        this.route();
        this.app.listen(8081, () => {
            console.info('listen on 8081');
        });
    }

    parsePostData(ctx): Promise<Buffer> {
        return new Promise((resolve, reject) => {
            try {
                let postdata = Buffer.alloc(0);
                ctx.req.addListener('data', (data) => {
                    postdata = Buffer.concat([data]);
                });
                ctx.req.addListener("end", function () {
                    resolve(postdata);
                })
            } catch (err) {
                reject(err)
            }
        })
    }

    private readFile(path): Promise<Buffer> {
        return new Promise((resolve, reject) => fs.readFile(path, (e, data) => e ? reject(e) : resolve(data)));
    }

    private route() {
        const router = new KoaRouter();
        router.post('/', async (ctx: Koa.Context, next) => {
            const encrypted = await this.parsePostData(ctx); // 接收到的经过base64编码后的加密数据
            const key = await this.readFile(__dirname + '/private.key');//读取私钥
            const pkey = key.toString();// 字符串形式的私钥
            const data = crypto.privateDecrypt({key: pkey, padding: constants.RSA_PKCS1_PADDING}, new Buffer(encrypted.toString(), 'base64')); // 使用私钥解密Buffer
            const json = JSON.parse(data.toString()); // 将解密后的信息解码为json对象
            const msg = JSON.stringify({errcode: json.name === 'demo' ? 0 : 1, errmsg: json.name === 'demo' ? 'ok' : 'error'}); // 需要返回的明文数据
            const e = crypto.privateEncrypt({key: pkey, padding: constants.RSA_PKCS1_PADDING}, new Buffer(msg)); // 使用私钥加密返回数据
            ctx.body = e.toString('base64'); // 将buffer编码为base64字符串后返回
        });
        this.app
            .use(router.routes())
            .use(router.allowedMethods());
    }
}

Server.bootstrap();
```
### 编译typescript
```bash
npm run build
```
### 启动服务器
```bash
npm run start
```
此时我们的服务器已经启动完成。

## PHP客户端
将2中的*公钥*复制到php项目下。
本文使用`rmccue/requests`作为`http客户端`发起请求。
index.php关键代码如下:

```php
<?php
$pubKey = openssl_pkey_get_public(file_get_contents(__DIR__ . '/public.key')); // 读取公钥
$data = Json::encode(['name' => 'demo']); // 需要提交的明文数据
openssl_public_encrypt($data, $encryped, $pubKey); // 使用公钥加密明文数据
$data = base64_encode($encryped); // 将加密后的数据进行base64编码
$res = Requests::post('http://localhost:8081', [], $data); // 将base64数据提交到NodeJs
$data = base64_decode($res->body);// 接收NodeJs私钥加密后的响应并进行base64解码
openssl_public_decrypt($data, $dd, $pubKey); // 使用公钥将密文解密
echo $dd; // 打印数据
```

## 执行正常请求
```bash
php index.php
```
输出如下
```json
{"errcode":0,"errmsg":"ok"}
```

## 执行不正常请求
将php中
```php
$data = Json::encode(['name' => 'demo']);
```
改为
```php
$data = Json::encode(['name' => 'demo1']);
```
发现收到的响应为
```json
{"errcode":1,"errmsg":"error"}
```
证明提交的数据不能被nodejs接受。

## 后记
本文简单使用了一下openssl相关功能函数，旨在起到一个抛砖引玉的作用，基于rsa算法可以开发出很多安全性很高的应用。