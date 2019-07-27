---
title: 手把手从零开始小程序单元测试(附避坑指南以及源码跟踪)
date: 2019-07-27 18:35:49
categories:
- frontend
tags:
- test
- miniprogram
---

单元测试是一个老生常谈的话题，基于Web/NodeJs环境的测试框架、测试教程数不胜数，也趋于成熟了。但是对于微信小程序的单元测试，目前还是处于起步状态，这两天在研究微信小程序的测试，也遇到了一些坑，在这里记录一下，希望给看到本文的小伙伴带来一点帮助，少走一些弯路。

本文内容有点多，但是干货满满，不明白的小伙伴可以关注公众号给我留言
![二维码](https://more-happy.ddhigh.com/FuFpZh9QTZVatcBtupR4MtOGPGTJ?imageView2/1/w/200)

## demo地址
[https://github.com/xialeistudio/miniprogram-unit-test-demo](https://github.com/xialeistudio/miniprogram-unit-test-demo)

## 关键依赖版本

本文写作时相关依赖版本如下(版本不同，源码行数可能不同)：

1. miniprogram-simulate: 1.0.7
2. j-component: 1.1.6
3. miniprogram-exparser: 0.0.6

## 测试流程

1. 初始化小程序项目，编写待测试组件
2. 安装jest,miniprogram-simulate测试环境
3. 编写测试用例
4. 执行测试

## 初始化小程序项目

1. 使用小程序开发者工具初始化新项目，APPID选择`测试号`即可，语言选择`Javascript`。
2. 使用小程序开发者工具新建`/components/user`组件
3. `components/user.js`
    ```js
    // components/user.js
    Component({
        data: {
            nickname: ''
        },
        methods: {
            handleUserInfo: function(e) {
                this.setData({ nickname: e.detail.userInfo.nickName })
            }
        }
    })
    ```
4. `components/user.wxml`
   ```xml
    <text class="nickname">{{nickname}}</text>
    <button class="button" open-type="getUserInfo" bindgetuserinfo="handleUserInfo">Oauth</button>
   ```
5. `pages/index/index.js`
   ```js
   Page({
       data:{}
   })
   ```
6. `pages/index/index.wxml`
    ```xml
    <view class="container">
        <user></user>
    </view>
    ```
7. 打开小程序开发者工具，可以看到有一个`Oauth`按钮，点击之后会在上面显示昵称。
8. 由此可以得到测试用例`点击授权按钮时上方显示为授权用户的昵称`
   
## 安装jest/miniprogram-simulate测试环境

1. 由于JS项目的小程序根目录没有`package.json`，需要手动生成一下
2. 打开终端，在项目根目录执行`npm init -y`生成`package.json`
3. 安装测试工具集`npm install jest miniprogram-simulate --save-dev`
4. 编辑`package.json`，在`scripts`新建`test`命令
    ```json
    {
        "name": "unit-test-demo",
        "version": "1.0.0",
        "description": "",
        "main": "app.js",
        "scripts": {
            "test": "jest"
        },
        "keywords": [],
        "author": "",
        "license": "ISC",
        "devDependencies": {
            "jest": "^24.8.0",
            "miniprogram-simulate": "^1.0.7"
        }
    }
    ```

## 编写测试用例

1. 在项目根目录新建`tests/components/user.spec.js`文件(目录需要手动创建)
2. 代码如下(参考微信官方单元测试文档编写):
    ```js
    const simulate = require('miniprogram-simulate');
    const path = require('path');

    test('components/user', (done) => { // 定义测试名称,传入done表示当前测试是异步测试，需要回调函数来告诉jest，我测试执行完毕
    const id = simulate.load(path.join(__dirname, '../../components/user')); // 加载组件
    const component = simulate.render(id); // 渲染组件

    const text = component.querySelector('.nickname'); // 获取nickname节点
    const button = component.querySelector('.button'); // 获取button节点
    button.dispatchEvent('getuserinfo', { // 模拟触发事件
        detail: {   // 传递事件参数
            userInfo: {
                nickName: 'hello',
            },
        },
    });
    setTimeout(() => { // 异步断言
        expect(text.dom.innerHTML).toBe('hello'); // 检测text节点的innerHTML等于模拟授权获取的昵称
        done();
    }, 1000);
    });
    ```

## 执行测试

1. `npm run test`，等待一秒后发现，`不出意外的话，测试肯定过不去`
2. 部分出错日志：
   ```text
   Expected: "hello"
   Received: ""
        at toBe (/Users/xialeistudio/WeChatProjects/unit-test-demo/tests/components/user.spec.js:18:32)
        at Timeout.callback [as _onTimeout] (/Users/xialeistudio/WeChatProjects/unit-test-demo/node_modules/jsdom/lib/jsdom/browser/Window.js:678:19)
        at listOnTimeout (internal/timers.js:535:17)
        at processTimers (internal/timers.js:479:7)
   ```
3. 可以推测一下原因：
   1. dispatchEvent的事件触发有问题，导致handleUserInfo未触发[1]
   2. dispatchEvent的事件触发成功，但是触发参数有问题[2]

## 错误分析(源码跟踪过程)

1. 针对第1点原因，可以写一下测试代码(`components/user.js`)
   ```js
    Component({
        data: {
            nickname: ''
        },
        methods: {
            handleUserInfo: function(e) {
                console.log(e);
            }
        }
    })
   ```
2. `npm run test`，可以看到事件还是成功触发了，不过`detail`是`{}`
   ```text
     console.log components/user.js:21
    { type: 'getuserinfo',
      timeStamp: 948,
      target: { id: '', offsetLeft: 0, offsetTop: 0, dataset: {} },
      currentTarget: { id: '', offsetLeft: 0, offsetTop: 0, dataset: {} },
      detail: {},
      touches: {},
      changedTouches: {} }
   ```
3. 原因1排除，查原因2
4. `dispatchEvent`方法是`被测试组件的子组件`，`被测试组件`由`simulate.render`函数返回
5. 浏览`node_modules/miniprogram-simulate/src/index.js`，看到`render函数(152行)`，可以看到返回的组件由`jComponent.create`提供
6. 浏览`node_modules/j-component/src/index.js`的`create`函数，可以看到其返回了`RootComponent`实例，而`RootComponent`是由`./render/component.js`提供
7. 浏览`node_modules/j-component/src/render/component.js`的`dispatchEvent`函数，在这里可以打下日志测试(本文就不打了，结果是这里的options就是`user.spec.js` `dispatchEvent`函数的`第二个参数`，`detail`是有值的)
8. 继续跟踪源码，由于咱们的是`自定义事件`，所以会走到`91行`的代码，该代码块如下：
    ```js
    // 自定义事件
      const customEvent = new CustomEvent(eventName, options);

      // 模拟异步情况
      setTimeout(() => {
        dom.dispatchEvent(customEvent);

        exparser.Event.dispatchEvent(customEvent.target, exparser.Event.create(eventName, {}, {
          originalEvent: customEvent,
          bubbles: true,
          capturePhase: true,
          composed: true,
          extraFields: {
            touches: options.touches || {},
            changedTouches: options.changedTouches || {},
          },
        }));
      }, 0);
    ```
9. 可以看到调用了`exparser.Event.dispatchEvent`函数，该函数的`第二个参数`调用了`exparser.Event.create`对自定义事件进行了包装，这里还没到最底层，需要继续跟踪
10. `exparser`对象是`miniprogram-exparser模块`提供的，浏览`node_modules/miniprogram-exparser/exparser.min.js`，发现该文件被混淆了，不过没关系`混淆后的代码逻辑是不变的，只不过变量名变得无意义，可读性变差`
11. 使用webstorm格式化该文件，这里我传了一份格式化好的到github [wxparser.js，可在线观看](https://github.com/xialeistudio/miniprogram-unit-test-demo/blob/master/extra/wxparser.js)
12. 需要在源码中搜索`三个参数`的`create`函数(`Object.create不算`)，需要有耐心，经过排查后发现[168行](https://github.com/xialeistudio/miniprogram-unit-test-demo/blob/master/extra/wxparser.js#L168)代码应该是目标代码
    ```js
    i.create = function(e, t, r) {
        r = r || {};
        var n = r.originalEvent, o = r.extraFields || {}, a = Date.now() - l, s = new i;
        s.currentTarget = null, s.type = e, s.timeStamp = a, s.mark = null, s.detail = t, s.bubbles = !!r.bubbles, s.composed = !!r.composed, s.__originalEvent = n, s.__hasCapture = !!r.capturePhase, s.__stopped = !1, s.__dispatched = !1;
        for (var u in o) s[u] = o[u];
        return s;
    }
    ```
13. 可以看到`s.detail = t`这个赋值，`t`是`create`的`第二个参数`，由`node_modules/j-component/render/component.js`的`wxparser.Event.create`传入，但是传入的`第二个参数写死了{}`，所以咱们的组件获取`detail`的时候`永远为{}`，将其修改为`options.detail||{}`即可，修改后代码如下：
    ```js
    exparser.Event.dispatchEvent(customEvent.target, exparser.Event.create(eventName, options.detail||{}, xxxxxx
    ```
14. 重新测试
    ```text
     PASS  tests/components/user.spec.js
  ✓ components/user (1099ms)

    Test Suites: 1 passed, 1 total
    Tests:       1 passed, 1 total
    Snapshots:   0 total
    Time:        3.622s
    Ran all test suites.
    ```

## 避坑指南

1. `querySelector`用法同HTML，但是需要在`组件`执行，而不是`组件.dom`，HTML中实在`DOMNode`执行的
2. `dispatchEvent`是触发事件，需要在`组件`执行，上述代码中是触发`button组件`的`自定义事件`
3. `dispatchEvent`事件名规范: `去掉前导bind剩余的字符串为事件名`，示例代码中`bindgetuserinfo`，触发时就是`getuserinfo`，如果是`bindtap`，那触发时就是`tap`
4. `dispatchEvent`底层是`j-component`这个`npm模块实现`的，跟踪源码发现执行是异步的(代码文件`node_modules/j-component/src/render/component.js`，函数名`dispatchEvent`)
    ```js
    // 自定义事件
      const customEvent = new CustomEvent(eventName, options);

      // 模拟异步情况
      setTimeout(() => {
        dom.dispatchEvent(customEvent);

        exparser.Event.dispatchEvent(customEvent.target, exparser.Event.create(eventName, {}, {
          originalEvent: customEvent,
          bubbles: true,
          capturePhase: true,
          composed: true,
          extraFields: {
            touches: options.touches || {},
            changedTouches: options.changedTouches || {},
          },
        }));
      }, 0);
      ```
5. 由于`setTimeout`的存在，触发事件为异步，所以写断言时需要加定时器

## 结语

小程序单元测试基本是没什么经验扩借鉴，但是基于官网提供的工具，以及`开源`，咱们遇到问题时细心排查然后修改一下，还是可以解决问题的。对单元测试有疑问的小伙伴可以扫码加我进行交流
![微信](https://more-happy.ddhigh.com/Fg5UE615NzZ0dXo6_gUe6qpCJILG?imageView2/1/w/200)