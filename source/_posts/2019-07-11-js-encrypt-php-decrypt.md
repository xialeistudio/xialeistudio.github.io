---
title: PHP和JS加解密
date: 2019-07-11 15:00:43
categories:
- backend
- php
---

最近遇到的几个网站在提交密码时提交的已经是密文，也就是说在网络上传输的密码是密文，这样提升了密码在网络传输中的安全性。

后端语言加解密已经有很成熟的方案了，前端的话Google之前出过一个[crypto-js](https://www.npmjs.com/package/crypto-js)，为浏览器的js提供了加解密方案。今天一起来了解一下基于AES的前后端加解密流程。

## Javascript

1. 安装npm包 `npm install crypto-js`
2. 加密代码

    ```javascript
    const CryptoJS = require("crypto-js");
    const key = CryptoJS.enc.Latin1.parse('1234567812345678');
    const iv = CryptoJS.enc.Latin1.parse('1234567812345678');
    const encoded = CryptoJS.AES.encrypt('hahaha', key, {
        iv: iv,
        mode: CryptoJS.mode.CBC,
        adding: CryptoJS.pad.ZeroPadding
    }).toString()
    console.log('encoded', encoded)
    ```

3. 解密代码

    ```javascript
    const key = CryptoJS.enc.Latin1.parse('123456781234567812345678');
    const iv = CryptoJS.enc.Latin1.parse('1234567812345678');
    const decoded = CryptoJS.AES.decrypt(encoded, key, {
        iv: iv,
        mode: CryptoJS.mode.CBC,
        adding: CryptoJS.pad.ZeroPadding
    }).toString(CryptoJS.enc.Utf8)
    console.log('decoded', decoded);
    ```

4. 输出如下

    ```text
    encoded 6bcgYd4f4ZgNOQH/3tqMpg==
    decoded hahaha
    ```

## PHP

直接使用openssl解密即可，代码如下：

```php
$encoded = '6bcgYd4f4ZgNOQH/3tqMpg==';
$key  = '123456781234567812345678';
$iv = '1234567812345678';
var_dump(openssl_decrypt($encoded, 'AES-192-CBC', $key, 0,$iv));
```

输出结果：

```text
string(6) "hahaha"
```

注意事项

1. AES加密位数跟密钥`key`有关, 以下是密钥位数和加密对应关系
   1. 16 => AES-128
   2. 24 => AES-192
   3. 32 => AES-256
2. `iv`是初始化向量. 超过16字节或者不足16字节都会被补足16字节或者截断到16字节。由于AES是块加密，铭文被分割成固定长度的块（一般是16字节长度），所以`iv`也是`16`字节。
3. CBC是加密模式
