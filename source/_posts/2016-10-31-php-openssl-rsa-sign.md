---
layout: post
title: PHP利用openssl实现RSA非对称加密签名
date: 2016-10-31 18:18:09.000000000 +08:00
type: post
published: true
status: publish
categories:
- php
tags:
- openssl
- php
meta:
  _edit_last: '1'
  _wp_old_slug: php%e5%88%a9%e7%94%a8openssl%e5%ae%9e%e7%8e%b0rsa%e9%9d%9e%e5%af%b9%e7%a7%b0%e5%8a%a0%e5%af%86%e7%ad%be%e5%90%8d
  views: '151'
---
**阅读本文前请确认启用了php_openssl扩展**
### 生成密钥

```php
$res = openssl_pkey_new();
openssl_pkey_export_to_file($res,__DIR__.'/private.key');
$d = openssl_pkey_get_details($res);
file_put_contents(__DIR__.'/public.key',$d['key']);
```

程序运行后会在当前目录生成 private.key 以及 public.key文件，你可以将你的public.key公开出去，请勿公开private.key
### 加密数据

```php
$data = 'xialei';
$res = openssl_pkey_get_private(file_get_contents(__DIR__ . '/private.key'));
if (openssl_sign($data, $out, $res)) {
    $data = base64_encode($out);
    echo $data;
}
```

加密数据需要使用**private.key**
### 验证数据

```php
$sig = base64_decode($data);
$res = openssl_pkey_get_public(file_get_contents(__DIR__ . '/public.key'));
var_dump(openssl_verify('xialei', $sig, $res));
```

解密数据需要使用**public.key**，如果输出"int(1)"证明解密成功，可以确认该数据由第1步中的private.key加密而来。
