---
layout: post
title: PHP自动更新网站
date: 2014-09-20 17:26:27.000000000 +08:00
type: post
published: true
status: publish
categories:
- php
tags:
- auto updator
meta:
  _edit_last: '1'
  views: '2431'
  _wp_old_slug: php%e5%ae%9e%e7%8e%b0%e8%87%aa%e5%8a%a8%e6%9b%b4%e6%96%b0
  _thumbnail_id: '185'
---
目前软件开发主流越来越倾向于B/S模式，不同于C/S模式的软件，B/S模式下的WEB程序自动更新是个麻烦问题。

本人利用PHP下载远程文件和ZIP类，写了一个简单的自动更新DEMO，供大家参考。

## 服务端
### 目录结构

```
|data

    |--20140918.zip

|--index.php
```

其中 data 文件夹用来存放补丁包,index.php 文件用来响应版本数据给客户端。

### index.php

```php
<?php
sleep(3);
header('Content-Type:application/json;utf-8');
echo json_encode(array(
    '20140918' => array(
        'version' => 20140920,
        'desc' => 'BUG修正，缓存系统',
        'url' => 'http://' . $_SERVER['HTTP_HOST'] . $_SERVER['REQUEST_URI'] . '/data/20140918.zip'
    )
));
exit();
```

20140918 对应的是客户端版本号，20140920 对应的是服务端版本号，desc 是本次补丁的描述，url 则是补丁包下载地址
## 客户端
### 目录结构

```
|tmp

|--config.php

|--Zip.php

|--index.php
```

config.php 为配置文件，保存本地版本信息，Zip.php 为ZIP操作类（从服务端下载的补丁包均为zip格式）,index.php 为自动更新程序（只是为了方便，实际中可以写个方法出来）
### index.php

```php
<?php
ob_implicit_flush(true);
$begin = microtime(true);
//检查更新,加载本地版本号
$config = require(__DIR__ . '/config.php');
$server = 'http://localhost/version';
echo '连接更新服务器...<br/>';
ob_flush();
$versions = json_decode(file_get_contents($server), true);

if (!isset($versions[$config['version']])) {
    echo '当前已是最新版本!';
} else {
    echo '当前版本：<b>', $config['version'], '</b> 服务器版本：<b>', 
    $versions[$config['version']]['version'], '</b><br/>';
    ob_flush();
    //开始下载
    $remote_fp = fopen($versions[$config['version']]['url'], 'rb');
    if(!is_dir(__DIR__.'/tmp')) mkdir(__DIR__.'/tmp');
    $tmp = __DIR__ . '/tmp/' . date('YmdHis') . '.zip';
    $local_fp = fopen($tmp, 'wb');
    echo '开始下载...<br/>';
    ob_flush();
    while (!feof($remote_fp)) {
        fwrite($local_fp, fread($remote_fp, 128));
    }
    fclose($remote_fp);
    fclose($local_fp);
    echo '下载完成,准备解压<br/>';
    ob_flush();
    require(__DIR__ . '/Zip.php');
    $zip = new Zip();
    $zip->extra($tmp, __DIR__);
    echo '解压完成,准备删除临时文件<br/>';
    ob_flush();
    //删除补丁包
    unlink($tmp);
    echo '临时文件删除完毕<br/>';
    ob_flush();
    //更新本地版本号
    $content = file_get_contents(__DIR__.'/config.php');
    $content = str_replace($config['version'],$versions[$config['version']]['version'],$content);
    file_put_contents(__DIR__.'/config.php',$content);
    echo '更新完成!耗时',microtime(true) - $begin,'秒<br/>';
    ob_flush();
    ob_end_clean();
    exit();
}
```

## config.php

```php
<?php
return array(
    'version' => '20140918'
);
```

### Zip.php

```php
<?php

/**
 * @version 1.0
 * @date 2014-08-11
 * @author 十七号 <xialeistudio@gmail.com>
 * @license MIT
 * 压缩、解压缩类
 */
class Zip
{
    /**
     * 打包
     * @param $path
     * @param $save
     */
    public static function archive($path, $save)
    {
        $zip = new ZipArchive();
        if ($zip->open($save, ZipArchive::OVERWRITE) === true) {
            self::addZip($path, $zip);
            $zip->close();
        }
    }

    /**
     * 添加文件或文件夹到zip对象
     * @param string $path
     * @param ZipArchive $zip
     */
    private static function addZip($path, $zip)
    {
        $handler = opendir($path);
        while (($file = readdir($handler)) !== false) {
            if ($file != '.' && $file != '..') {
                if (is_dir($path . DIRECTORY_SEPARATOR . $file)) {
                    self::addZip($path . DIRECTORY_SEPARATOR . $file, $zip);
                } else {
                    $zip->addFile($path . DIRECTORY_SEPARATOR . $file);
                }
            }
        }
        closedir($handler);
    }

    /**
     * 解压文件
     * @param string $file 压缩文件路径
     * @param string $path 解压路径，为空则以文件名为路径
     */
    public static function extra($file, $path = null)
    {
        if (!isset($path)) {
            $array = explode('.', $file);
            $path = reset($array);
        }

        $zip = new ZipArchive();
        if ($zip->open($file) === true) {
            $zip->extractTo($path);
            $zip->close();
        }
    }
}
```

本文只写了一个很简单的自动更新程序，只是为了说明更新程序的基本思路。还有很多细节方面可以定制的。