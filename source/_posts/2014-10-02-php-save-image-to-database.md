---
layout: post
title: PHP二进制方法存储图片
date: 2014-10-02 14:13:42.000000000 +08:00
type: post
published: true
status: publish
categories:
- backend
- php
---
大部分人的图片上传都是保存一个路径到数据库，这样在插入时确实快，也符合web的特点，但是在删除时就很麻烦，需要找到文件并删除，该代码能够把代码直接存入数据库，删除时一并删除。   
请注意：这样的话数据库大小会激增，请酌情使用,且RDBMS对于二进制数据的处理并不是很理想。
## 表结构（只做简单演示，故字段有限）

```sql
CREATE TABLE `upload` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `type` varchar(20) NOT NULL,
  `data` mediumblob NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
```

## 上传表单

```html
<!doctype html>
    <html>
<head>
    <title>
        Post-Image
    </title>
</head>
<body>
<form action="post.php" method="post" enctype="multipart/form-data">
    <input type="file" name="file" id="file"/>
    <input type="submit" value="OK"/>
</form>
</body>
</html>
```

## 处理程序

```php
<?php
if ($_FILES["file"]["error"] > 0)
{
    echo "Error: " . $_FILES["file"]["error"] . "<br />";
}
else
{
    $type = $_FILES["file"]["type"];
    $size = $_FILES['file']['size'];
    $tmp=$_FILES["file"]["tmp_name"];
    $fp = fopen($tmp,'rb');
    $data = bin2hex(fread($fp,$size));
    $dsn='mysql:host=localhost;dbname=test';
    echo '<pre>';
    try{
        $pdo = new PDO($dsn,'root','root');
        $pdo->exec("INSERT INTO `upload`(`type`,`data`) values ('$type',0x$data)");
        $id = $pdo->lastInsertId();
        echo 'upload success!<a href="view.php?id='.$id.'">View</a>';
        $pdo = null;
    }catch (PDOException $e){
        echo $e->getMessage();
    }
    echo '</pre>';
    fclose($fp);
}
```

## 显示页面

```php
<?php
$id = $_GET['id'];
if(is_numeric($id)){
    $dsn='mysql:host=localhost;dbname=test';
    try{
        $pdo = new PDO($dsn,'root','root');
        $rs = $pdo->query('select * from `upload`  where `id`='.$id);
        $row = $rs->fetchAll();
        $data = $row[0];
        header("Content-Type:${data['type']}");
        echo $data['data'];
        $pdo = null;
    }catch (PDOException $e){
        echo $e->getMessage();
    }
}else{
    exit();
}
```

经过测试可行，请大家在必要的时候才使用~