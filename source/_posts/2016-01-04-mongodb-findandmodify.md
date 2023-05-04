---
layout: post
title: mongodb更新指定条件的子文档
date: 2016-01-04 11:35:05.000000000 +08:00
type: post
published: true
status: publish
categories:
- engineering
---
## 文档内容

```json
{
    "_id": ObjectId("5689db252d162c9881532986"),
    "openid": "xialei",
    "channels": [
        {
            "channel_id": "c1"
        },
        {
            "channel_id": "c2"
        },
        {
            "channel_id": "c2"
        },
        {
            "channel_id": "c2"
        }
    ]
}
```

## 需求
把该文档的channels中channel_id为c2的删除，但是主记录要保留。
这时候就不能用remove方法了，该方法会删除整条文档，查询[官方文档](https://docs.mongodb.org/manual/reference/method/db.collection.findAndModify/#db.collection.findAndModify)发现有个findAndModify方法。
## 函数原型

```javascript
db.collection.findAndModify({
    query: <document>,
    sort: <document>,
    remove: <boolean>,
    update: <document>,
    new: <boolean>,
    fields: <document>,
    upsert: <boolean>
    bypassDocumentValidation: <boolean>
});
```

## 调用代码

```bash
db.collection.findAndModify({
    query: {"openid":"xialei"},
    update: {"$pull":{"channels":{"channel_id":"c2"}}},
    new: true
});
```

## 执行结果

```json
{
    "_id" : ObjectId("5689db252d162c9881532986"),
    "openid" : "xialei",
    "channels" : [ 
        {
            "channel_id" : "c1"
        }
    ]
}
```

**$pull**是数组操作符，明白update中的操作之后，相信大家可以举一反三，比如要插入一个文档就肯定会想到用**$push**了。