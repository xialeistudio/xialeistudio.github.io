---
title: 微信小程序数据字段大小写问题
date: 2019-07-16 11:17:38
categories:
- Engineering
---

这两天在开发微信小程序登录以及加解密的时候，因为数据大小写的问题被坑了一把。

## 场景

1. 小程序调用`wx.login`时会获得`code`，传输给服务端可以得到`openid`,`unionid(绑定了开放平台)`,`session_key`
2. 小程序调用`getUserInfo`会获得`encrypted_data`,`iv`,解密后得到`unionId`,`openId`
3. `unionid`和`openid`这两个场景`键名大小写是不同的`

## 例子

1. 服务端根据`code获取session_key`返回结果如下：

    ```json
    {
        "session_key": "我是session_key",
        "openid": "我是openid",
        "unionid": "我是unionid"
    }
    ```

2. 服务端根据`session_key解密encrypted_data和iv`返回结果如下：

    ```json
    {
        "openId": "OPENID",
        "nickName": "NICKNAME",
        "gender": GENDER,
        "city": "CITY",
        "province": "PROVINCE",
        "country": "COUNTRY",
        "avatarUrl": "AVATARURL",
        "unionId": "UNIONID",
        "watermark":
        {
            "appid":"APPID",
            "timestamp":TIMESTAMP
        }
    }
    ```

可以看到两次同样的字段`openid`和`unionid`大小写是不同的，此处容易踩坑。

## 结论

1. 服务端根据`code换session_key/openid/unionid`是`小写`
2. 服务端根据`encrypted_data和iv`解密得到的`openId/unionId`是`大写`

最后，祝大家在开发过程中少踩坑。