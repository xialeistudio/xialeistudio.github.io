---
layout: post
title: PHP遍历文件
date: 2014-09-27 09:28:30.000000000 +08:00
type: post
published: true
status: publish
categories:
- engineering
---
遍历文件夹主要用到 opendir readdir closedir 三个函数，有两个要注意的地方

要排除 '.' 和 '..' 两个目录

需要用到递归

```php
<?php
/**
 * 遍历文件夹
 * @param string $path
 * @return array
 */
function listFiles($path)
{
    $files = array();
    $handler = opendir($path);//打开目录
    while (($file = readdir($handler)) !== false) {
        if($file != '.' && $file != '..'){ //当前目录和上级目录
            if(is_dir($path.DIRECTORY_SEPARATOR.$file)){
                $files[$file] = listFiles($path.DIRECTORY_SEPARATOR.$file);
            }else{
                $files[] = $file;
            }
        }
    }
    closedir($handler);
    return $files;
}

$array = listFiles(__DIR__);
print_r($array);
```