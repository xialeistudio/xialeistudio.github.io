---
slug: angularjs-empty-array
title: Angularjs处理后端空数据
date: 2014-11-15 18:04:02.000000000 +08:00
categories:
- Engineering
---
Yii1.x DAO中的queryAll方法查询，如果有结果，会返回一个数组，如果没有结果，会返回null。现在分两种情况：
## 返回空数组

```php
$array = array(
);
echo json_encode($array);
```

输出为

```json
[]
```

## 返回null

```php
$array = null;
echo json_encode($array);
```

输出为

```json
null
```

那么问题来了，JS接收这两个的结果是不同的。   
如果使用以下代码判断数据:
```javascript
if(data.length == 0){
    //当前评论为空
}else{
    //当前评论不为空
}
```

如果返回   []  ，这段代码是生效的。但是如果返回 null ,这个就有问题了。

后来，使用

```javascript
if(data == null){
    //评论为空
}else{
    //评论不为空
}
```

这个判断老是出问题，后端明明返回null了，判断还是错误的，这时候想到JS也是若类型语言，会不会是类型的问题。

```javascript
console.log(typeof data)
```

返回的是**"string"**   
那么问题就解决了，用以下代码就可以了

```javascript
if(data.length == 0 || data == "null"){
    //评论为空
}else{
    //评论不为空
}
```