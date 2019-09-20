---
title: NodeJs简明教程(6)
date: 2019-07-21 10:25:22
categories:
- backend
- nodejs
---
> NodeJs简明教程将从零开始学习NodeJs相关知识，助力JS开发者构建全栈开发技术栈！

关注获取更多`NodeJs精品文章`
![二维码](https://more-happy.ddhigh.com/FuFpZh9QTZVatcBtupR4MtOGPGTJ?imageView2/1/w/200)

本文是NodeJs简明教程的第六篇，将介绍NodeJs crypto模块相关的基本操作。

> crypto 模块提供了加密功能，包括对 OpenSSL 的哈希、HMAC、加密、解密、签名、以及验证功能的一整套封装。

## Hash

> Hash类是用于创建数据哈希值的工具类。

哈希算法严格来说并不属于加密算法，传统意义上的 **加密** 是与 **解密** 相配对的。哈希算法能够保证被哈希的内容不被篡改。针对任意长度的输入数据都可以产生固定位数的哈希值。

crypto模块对hash的操作是一致的，除了算法名不一致之外，本文以 **md5** 和 **sha1** 作为示例。

### MD5

```js
const crypto = require('crypto');

const hash = crypto.createHash('md5'); // 创建MD5 hash示例

hash.update('111111'); // 待计算hash的数据
console.log(hash.digest('hex'));
```

以上例程输出 `96e79218965eb72c92a549dd5a330112`

### SHA1

```js
const crypto = require('crypto');

const hash = crypto.createHash('sha1'); // 创建MD5 hash示例

hash.update('111111'); // 待计算hash的数据
console.log(hash.digest('hex'));
```

以上例程输出 `3d4f2bf07dc1be38b20cd6e46949a1071f9d0e3d`

## Base64

`Base64`并不是`crypto`模块的成员，但是跟本节内容比较相近，所以放过来了。Base64是一套编码算法，常用在二进制数据编码上。

### Base64编码

```js
const data = '111111';
const encodedData = Buffer.from(data, 'utf8').toString('base64'); // 输入编码为utf8,输出为base64
console.log(encodedData);
```

以上例程输出 `MTExMTEx`

### Base64解码

```js
const data = 'MTExMTEx';
const decodedData = Buffer.from(data, 'base64').toString('utf8'); // 输入编码为base64,输出编码为utf8
console.log(decodedData);
```

以上例程输出`111111`

## Hmac

> Hmac类是用于创建加密Hmac摘要的工具。

Hmac算法也是一种hash算法，但是它需要一个密钥，针对同样的输入，传统的hash算法输出是固定的。
但是Hmac的输出会随着密钥的不同而不同。

```js
const crypto = require('crypto');

const hmac = crypto.createHmac('sha256', 'secret-key');

hmac.update('Hello, world!');

console.log(hmac.digest('hex'));
```

以上例程输出 `f4d850b1017eb4e20e0c58443919033c90cc9f4fe889b4d6b4572a4a0ec2d08a`

## AES

> AES是一种常用的对称加密算法，加解密都用同一个密钥。

### AES加密

```js
const crypto = require('crypto');

const cipher = crypto.createCipheriv('aes192', '111111111111111111111111', '1111111111111111')
var crypted = cipher.update('1', 'utf8', 'hex'); 
crypted += cipher.final('hex');
console.log(crypted);
```

以上例程输出 `5bb3e6eb39e502b5fa74d93796087efa`

**说明：**

`createCipheriv`原型如下：

`crypto.createCipheriv（algorithm，key，iv [，options]）`

1. `iv`是初始化向量，可以 **为空** 或者 **16** 字节的字符串
2. `key`是加密密钥，根据选用的算法不同，密钥长度也不同，对应关系如下：
   1. `aes128`对应`16位`长度密钥
   2. `aes192`对应`24位`长度秘钥
   3. `aes256`对应`32位`长度密钥

### AES解密

```js
const crypto = require('crypto');

const cipher = crypto.createDecipheriv('aes192', '111111111111111111111111', '1111111111111111')
var data = cipher.update('5bb3e6eb39e502b5fa74d93796087efa', 'hex', 'utf8'); // 输入数据编码为hex(16进制)，输出为utf8
data += cipher.final('utf8');
console.log(data);
```

以上例程输出`1`

`crypto.createDecipheriv`方法原型与`crypto.createCipher`一致，这里不在赘述。

## RSA

> RSA算法是一种非对称加密算法，即由一个私钥和一个公钥构成的密钥对，通过私钥加密，公钥解密，或者通过公钥加密，私钥解密。其中，公钥可以公开，私钥必须保密。

### 生成密钥对

使用RSA算法前必须提供密钥对，本文使用`openssl`命令进行生成。

1. `openssl genrsa -out private.pem 2048 ` 生成`2048位`长度的`私钥`
2. `openssl rsa -in private.pem -pubout -out public.pem` 导出公钥

这样在当前目录我们就得到了`private.pem`和`public.pem`

### RSA加密

```js
const crypto = require('crypto');
const fs = require('fs');

const privateKey = fs.readFileSync('./private.pem', { encoding: 'utf8' });

const encodedData = crypto.privateEncrypt(privateKey, Buffer.from('111111','utf8')); // 传入utf8编码的数据
console.log(encodedData.toString('hex'));
```

以上例程输出

```text
44a1b50b9639e4cbe17d55ca57dcb041387acadae3d3721fd9803a3a33091a36d59977feaa6caad990e58b9542c26297de6014e20819f0a71eadd0793bfe0fac834f30d2a05f8b329a3b2409e9f8b7fbd7de3734ada00228b84027568be58a2a34ccf0c4a8b2d02c58eef510931423ed5f40c696361b606df11609248b271aebcd17f9a113f98a8fa86c9c45bd609256f4779ce01ea3027171fffb35e695f1c38553aecafb72a2f46a9012246fde0f2934eacba8932bca38e228f4f4294873ed75d9acf79ab854897ebaab2375384b2da682c1b2e2b49b0592929067b3d5a11971d912629a178691345f7f88137343588b5c51d60643e5c00998484727b8c4a8
```

### RSA解密

```js
const crypto = require('crypto');
const fs = require('fs');

const publicKey = fs.readFileSync('./public.pem', { encoding: 'utf8' });

const encodedData = '44a1b50b9639e4cbe17d55ca57dcb041387acadae3d3721fd9803a3a33091a36d59977feaa6caad990e58b9542c26297de6014e20819f0a71eadd0793bfe0fac834f30d2a05f8b329a3b2409e9f8b7fbd7de3734ada00228b84027568be58a2a34ccf0c4a8b2d02c58eef510931423ed5f40c696361b606df11609248b271aebcd17f9a113f98a8fa86c9c45bd609256f4779ce01ea3027171fffb35e695f1c38553aecafb72a2f46a9012246fde0f2934eacba8932bca38e228f4f4294873ed75d9acf79ab854897ebaab2375384b2da682c1b2e2b49b0592929067b3d5a11971d912629a178691345f7f88137343588b5c51d60643e5c00998484727b8c4a8';

const rawData = crypto.publicDecrypt(publicKey, Buffer.from(encodedData, 'hex')); // 传入hex(16进制)数据
console.log(rawData.toString('utf8'));
```

以上例程输出

```text
111111
```

## 结语

常用的加解密、哈希、编解码用法已经介绍完毕，读后有疑问请加微信群讨论。

![微信群](https://more-happy.ddhigh.com/FpffwgkBeSWPyHRUJJmi9J9SFX_l?imageView2/1/w/200)
