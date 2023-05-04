---
title: 微信H5点击跳转到关注页
date: 2017-11-25 15:19:59
categories:
- engineering
---
# 背景
微信诱导关注接口在早两年已经被微信关停，但是一般的H5目的都是要关注公众号。
目前用的多的方法是用公众号发表一篇文章，文章里面一般是一个GIF的箭头图片指向公众号关注。
这种方法有点取巧。

今天要介绍的是另一种方法，感觉应该不会被微信封号。
# 起因
有个朋友在segmentfault上发了一个链接出来，微信打开可以直接到关注页
```
https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MzUzMDM3MjMyNQ==#wechat_redirect
```
条件反射发现`MzUzMDM3MjMyNQ==`是Base64编码后的参数，解码后是一段数字，然后我改了下数字，重新编码，再发送到微信，发现可以打开另外一个公众号的关注页
```
https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MzUzMDM3MjMyNA==#wechat_redirect
```
所以只要知道那个公众号数字就可以构造链接进行关注，想着这种ID一般在公众平台有，果然被我找到了。

# 步骤
1. 登录公众平台后台
2. 点击右上角的公众号，来到公众号信息页面
3. 查看公众号信息页面的源代码，在顶上找到以下代码
    ```javascript
    window.wx={
    uin:"xxxx"||"0"
    };
    ```
4. `xxxx` 就是你的公众号数字ID
5. 将第4步找到的ID进行base64编码
6. 构造如下链接
    ```
    https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=第5步的结果#wechat_redirect
    ```
7. 发送到微信之后即可。

# 反思
从打开的链接看页面还是蛮正式的，可能不是私有接口，但是微信文档中没说过这种方式，故使用本方式带来的后果请自行负责！