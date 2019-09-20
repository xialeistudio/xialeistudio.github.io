---
layout: post
title: 百度云推送nodejs sdk
date: 2015-12-29 18:14:24.000000000 +08:00
type: post
published: true
status: publish
categories:
- backend
- nodejs
---
## 项目地址
[bpush-nodejs](https://github.com/xialeistudio/bpush-nodejs)
## 开发背景
百度官方只有php和java的sdk，但是百度提供了rest api,好处就是开发者可以使用任何语言开发一套服务端SDK，本人开源一套基于nodejs的sdk。
## 使用

```bash
npm install bpush-nodejs --save
```

```javascript
var bpush = require('bpush-nodejs');
```

## 说明   
SDK采用Promise方式进行回调,demo代码如下(以推送单个设备为例),catch代码块中 **只捕获HTTP请求错误,如果HTTP请求成功,但是百度服务端报错,请自行在then中处理**   

```javascript
var data = {
    channel_id: '5247517738736986629',
    msg: JSON.stringify({
        aps: {
            alert: '你是呵呵SINGLE'
        }
    }),
    msg_type: bpush.constant.MSG_TYPE.NOTIFICATION,
    deploy_status: bpush.constant.DEPLOY_STATUS.DEVELOPMENT,
    device_type: bpush.constant.DEVICE_TYPE.IOS
};
bpush.sendRequest(bpush.apis.pushMsgToSingleDevice, data).then(function (data) {
            data = JSON.parse(data);
            console.log(data);
        }).catch(function(e){
            console.error(e);
        });
```

所有api调用方法均为 **bpush.sendRequest(bpush.apis.[api名称], [api需要的数据])**   
## api列表   
[百度官方文档](http://push.baidu.com/doc/restapi/restapi)   
**特别说明:** 本文档写作时,百度api返回的数据以本文档为准,与官方文档有出入的地方可能是百度升级了api忘记更新文档所致.   
+ pushSingleDevice   
功能:推送单一终端   
请求参数:

```javascript
var data = {
    channel_id: '5247517738736986629',//设备channelID
    msg: JSON.stringify({
        aps: {
        alert: '你是呵呵SINGLE'
        }
    }),
    msg_type: bpush.constant.MSG_TYPE.NOTIFICATION,
    deploy_status: bpush.constant.DEPLOY_STATUS.DEVELOPMENT,
    device_type: bpush.constant.DEVICE_TYPE.IOS
};
```

返回参数:

```javascript
{
    request_id: 900279880,
    response_params: {
        msg_id: '7960733379606623036',
        send_time: 1451380442
    }
}
```

+ pushMsgToAll   
功能:推送所有终端   
请求参数:

```javascript
var data = {
    msg: JSON.stringify({
        aps: {
            alert: '你是呵呵ALL'
        }
    }),
    msg_type: bpush.constant.MSG_TYPE.NOTIFICATION,
    deploy_status: bpush.constant.DEPLOY_STATUS.DEVELOPMENT,
    device_type: bpush.constant.DEVICE_TYPE.IOS
};
```

返回参数:

```javascript
{
    request_id: 900279880,
    response_params: {
        msg_id: '7960733379606623036',
        send_time: 1451380442
    }
}
```

+ pushMsgToTag   
功能:组播推送   
请求参数:

```javascript
var data = {
    msg: JSON.stringify({
    aps: {
            alert: '你是呵呵TAG'
        }
    }),
    type: 1,//固定为1
    tag: 'test',//标签名称
    msg_type: bpush.constant.MSG_TYPE.NOTIFICATION,
    deploy_status: bpush.constant.DEPLOY_STATUS.DEVELOPMENT,
    device_type: bpush.constant.DEVICE_TYPE.IOS
};
```

返回参数:

```javascript
{
    request_id: 900279880,
    response_params: {
        msg_id: '7960733379606623036',
        send_time: 1451380442
    }
}
```

+ queryMsgStatus   
功能:查询消息推送情况   
请求参数:

```javascript
var data = {
    msg_id: '3129074535657443828'
};
```

返回结果:

```json
{
    "request_id": 1221365722,
    "response_params": {
        "total_num": 1,
        "result": [
            {
                "send_time": 1451381279,
                "success": -1,
                "total_num": 4,
                "status": 0,
                "msg_id": "3129074535657443828"
            }
        ]
    }
}
```

+ queryTags   
功能:查询标签组列表   
请求参数:

```javascript
var data = {
};
```

返回参数:

```json
{
    "request_id": 896177143,
    "response_params": {
        "total_num": 4,
        "result": [
            {
                "tid": "1933949969962682514",
                "tag": "default",
                "info": "default",
                "type": 0,
                "create_time": 1447315802
            },
            {
                "tid": "73579040",
                "tag": "test20151112",
                "info": "test201511127237210",
                "type": 2,
                "create_time": 1447321138
            },
            {
                "tid": "77983912",
                "tag": "test",
                "info": "test7237210",
                "type": 2,
                "create_time": 1451376995
            },
            {
                "tid": "77986112",
                "tag": "testtag",
                "info": "testtag7237210",
                "type": 2,
                "create_time": 1451379084
            }
        ]
    }
}
```

+ createTag   
功能:创建标签组   
请求参数:

```javascript
var data = {
    tag: 'testtag'
};
```

返回参数:

```json
{
    "request_id": 1221802330,
    "response_params": {
        "tag": "testtag",
        "result": 0
    }
}
```

+ deleteTag   
功能:删除标签组   
请求参数:

```javascript
var data = {
    tag: 'testtag'
};
```

返回参数:

```json
{
    "request_id": 897517834,
    "response_params": {
        "tag": "testtag",
        "result": 0
    }
}
```

+ addDevicesToTag   
功能:添加设备到标签组   
请求参数:

```javascript
var data = {
    tag: 'testtag',
    channel_ids: JSON.stringify([5247517738736986629])
};
```

返回参数:

```json
{
    "request_id": 881162061,
    "response_params": {
        "result": [
            {
                "channel_id": "5247517738736987000",
                "result": 1
            }
        ]
    }
}
```

+ removeDevicesFromTag   
功能:将设备从标签组中移除   
请求参数:

```javascript
var data = {
    tag: 'testtag',
    channel_ids: JSON.stringify([5247517738736986629])
};
```

返回参数:

```json
{
    "request_id": 881521481,
    "response_params": {
        "result": [
            {
                "channel_id": "5247517738736987000",
                "result": 1
            }
        ]
    }
}
```

+ deviceNumInTag   
功能:查询标签组设备数量   
请求参数:

```javascript
var data = {
    tag: 'testtag'
};
```

返回参数:

```json
{
    "request_id": 882409689,
    "response_params": {
        "device_num": -1
    }
}
```

+ reportStaticDevice   
功能:当前应用的设备统计信息   
请求参数:

```javascript
var data = {
};
```

返回参数:

```json
{
    "request_id": 883742690,
    "response_params": {
        "result": {
            "1450713600": {
                "total_term": 2,
                "total_term_detail": {
                    "1450774800": 2
                },
                "new_term": 1,
                "new_term_detail": {
                    "1450774800": 1
                },
                "del_term": 0,
                "del_term_detail": []
            },
            "1450800000": {
                "total_term": 3,
                "total_term_detail": {
                    "1450868400": 3
                },
                "new_term": 1,
                "new_term_detail": {
                    "1450868400": 1
                },
                "del_term": 0,
                "del_term_detail": []
            },
            "1451232000": {
                "total_term": 4,
                "total_term_detail": {
                    "1451293200": 4
                },
                "new_term": 1,
                "new_term_detail": {
                    "1451293200": 1
                },
                "del_term": 0,
                "del_term_detail": []
            }
        },
        "total_num": 3
    }
}
```
