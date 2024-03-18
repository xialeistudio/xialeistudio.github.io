---
slug: wechat-media-platform-nodejs-sdk
title: 微信公众平台开发NodeJs SDK
date: 2016-08-09 16:07:22.000000000 +08:00
categories:
- Engineering
---
*本SDK要求NodeJs >= 4.x，欢迎大家在issues提问。*

## 项目地址
[wechat-nodejs](https://github.com/xialeistudio/wechat-nodejs/)
## 安装

```bash
npm install wechat-nodejs ---save
```

## 说明
使用所有sdk功能前需要初始化wechat句柄，初始化代码如下：

```javascript
const Wechat = require('wechat-nodejs').Wechat;
const wechat = new Wechat(appId,appSecret);
```

SDK扩展了JS原始错误类，包含message,code属性，SDK中Promise抛出的错误code为微信返回的errcode，抛出一个自定义错误代码如下：

```javascript
const AppError = require('wechat-nodejs').AppError;
throw new AppError('参数错误',1);
```

## 功能列表
### 分组
+ 初始化Group

```javascript
const Group = require('wechat-nodejs').Group;
const group = new Group(wechat.getInstance());
```

+ 创建分组

```javascript
group.create('测试分组').then((data)=>{
  console.log(data);
}).catch((e)=>{
  console.error(e.message,e.code);
});
```

+ 获取所有分组

```javascript
group.getAll().then((data)=>{
  console.log(data);
}).catch((e)=>{
  console.error(e.message,e.code);
});
```

+ 获取用户所在分组

```javascript
group.getIdByOpenid(openid).then((groupId)=>{
  console.log(groupId);
}).catch((e)=>{
  console.error(e.message,e.code);
});
```

+ 修改分组名称

```javascript
group.update(100,'测试分组01').then((data)=>{
  console.log(data);
}).catch((e)=>{
  console.error(e.message,e.code);
});
```

+ 移动用户分组

```javascript
group.moveUserToGroup('oA-yljrYgywqN3SCXS_3jZnIP6Yw',100).then((data)=>{
  console.log(data);
}).catch((e)=>{
  console.error(e.message,e.code);
});
```

+ 批量移动用户分组

```javascript
group.moveUsersToGroup(['oA-yljrYgywqN3SCXS_3jZnIP6Yw'],100).then((data)=>{
  console.log(data);
}).catch((e)=>{
  console.error(e.message,e.code);
});
```

+ 删除分组

```javascript
group.remove(100).then((data)=>{
  console.log(data);
}).catch((e)=>{
  console.error(e.message,e.code);
});
```

### JSSDK
+ 初始化JSSDK

```javascript
const JSSDK = require('wechat-nodejs').JSSDK;
const jssdk = new JSSDK(wechat.getInstance());
```

+ 获取jsticket

```javascript
jssdk.getTicket().then((ticket)=>{
  console.log(ticket);
}).catch((e)=>{
  console.error(e.message,e.code);
});
```

+ 获取jssdk配置参数

```javascript
jssdk.getConfig('http://www.baidu.com',['onMenuShareTimeline'],false).then((config)=>{
  console.log(config);
}).catch((e)=>{
  console.error(e.message,e.code);
});
```
### 自定义菜单
+ 初始化Menu

```javascript
const Menu = require('wechat-nodejs').Menu;
const menu = new Menu(wechat.getInstance());
```

+ 创建自定义菜单

```javascript
const button = [
{
  "type": "click",
  "name": "今日歌曲",
  "key": "V1001_TODAY_MUSIC"
},
{
  "name": "菜单",
  "sub_button": 
  [
    {
    "type": "view",
    "name": "搜索",
    "url": "http://www.soso.com/"
    },
    {
    "type": "view",
    "name": "视频",
    "url": "http://v.qq.com/"
    },
    {
    "type": "click",
    "name": "赞一下我们",
    "key": "V1001_GOOD"
    }
  ]
}];
menu.create(button).then((data)=>{
  console.log(data);
}).catch((e)=>{
  console.error(e.message,e.code);
});
```
+ 查询自定义菜单

```javascript
menu.get().then((data)=>{
  console.log(data);
}).catch((e)=>{
  console.error(e.message,e.code);
});
```

+ 删除自定义菜单

```javascript
menu.remove().then((data)=>{
  console.log(data);
}).catch((e)=>{
  console.error(e.message,e.code);
});
```

+ 获取公众平台后台设置的自定义菜单

```javascript
menu.getByWeb().then((data)=>{
  console.log(data);
}).catch((e)=>{
  console.error(e.message,e.code);
});
```

### 消息
+ 初始化Message

```javascript
const Message = require('wechat-nodejs').Message;
const message = new Message(wechat.getInstance());
```

+ 发送模板消息

```javascript
const data = {
  orderId: {
    value: '20160101'
  },
  status: {
    value: '已发货'
  }
};
const openid = 'oA-yljj5cBGSvnwFodHT1iqis7X8';
const templateId = 'G4C9rNCejbhyYzh7xsOh46pieLelrmj_bLQtRhdOqkY';
const url = 'https://github.com';
message.sendTemplate(openid,templateId,url,data).then((data)=> {
  data.should.have.property('errcode', 0);
}).catch((e)=>{
  console.error(e.message,e.code);
});
```

### 用户
+ 初始化User

```javascript
const User = require('wechat-nodejs').User;
const user = new User(wechat.getInstance());
```

+ 设置用户备注名

```javascript
user.setRemark('oA-yljj5cBGSvnwFodHT1iqis7X8','重要客户').then((data)=>{
  console.log(data);
}).catch((e)=>{
  console.error(e.message,e.code);
});
```

+ 获取用户信息

```javascript
user.getInfo('oA-yljj5cBGSvnwFodHT1iqis7X8').then((data)=>{
  console.log(data);
}).catch((e)=>{
  console.error(e.message,e.code);
});
```

+ 批量获取用户信息

```javascript
user.batchGetInfo(['oA-yljj5cBGSvnwFodHT1iqis7X8']).then((data)=>{
  console.log(data);
}).catch((e)=>{
  console.error(e.message,e.code);
});
```

+ 检测关注

```javascript
user.isSubscribe('oA-yljj5cBGSvnwFodHT1iqis7X8').then((isSubscribe)=>{
  console.log(isSubscribe);
}).catch((e)=>{
  console.error(e.message,e.code);
});
```

+ 获取关注用户openid列表

```javascript
user.getList('oA-yljj5cBGSvnwFodHT1iqis7X8').then((data)=>{
  console.log(data);
}).catch((e)=>{
  console.error(e.message,e.code);
});
```

## 单元测试
终端执行：

```bash
npm install mocha --save-dev
```

在本sdk根目录新建**config.json**，内容如下：

```json
{
  "wechat": {
    "appId": "微信公众号appId",
    "appSecret": "微信公众号appSecret"
  }
}
```

终端执行：

```bash
npm run test
```

## 授权协议
MIT License