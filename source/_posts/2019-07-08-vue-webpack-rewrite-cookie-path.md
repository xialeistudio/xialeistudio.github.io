---
title: vue webpack重写cookie路径
date: 2019-07-08 17:24:05
categories:
- Engineering
tags:
- webpack
---

webpack提供的反向代理服务器在开发阶段非常方便，几行简单的代码配置就可以使用反向代理功能，包括路径重写、cookie处理等。

项目开发阶段使用的API路径是 `/admin`，部署到线上是`/`，所以在开发过程中需要在`proxyTable`进行反向代理配置，将路径重写掉，路径重写代码如下(`config/index.js`):

```js
proxyTable: {
      '/admin': {
        target: 'http://127.0.0.1:8080',
        changeOrigin: true,
        pathRewrite: {
          '^/admin': '/admin2'
        },
      }
}
```

启动项目之后进行登录，此时API请求成功，但是获取登录用户信息时发现cookie没有带过去。查看请求发现登录请求的`Set-Cookie`响应头中的`Path`是`/admin2`。但是咱们请求的路径是`/admin`，cookie当然不会生效。

查阅文档发现，proxyTable支持`onProxyRes`回调函数来自定义响应，流程是通过替换后端服务器设置的`cookie-path`来进行处理，代码如下：

```js
proxyTable: {
      '/admin': {
        target: 'http://127.0.0.1:8080',
        changeOrigin: true,
        pathRewrite: {
          '^/admin': '/lesson/admin'
        },
        onProxyRes: function (proxyRes, req, res) {
          const cookies = proxyRes.headers['set-cookie']
          if (cookies) {
            const newCookies = cookies.map(cookie => {
              return cookie.replace(/Path=\/admin2/, 'Path=/')
            })
            delete proxyRes.headers['set-cookie']
            proxyRes.headers['set-cookie'] = newCookies
          }
    }
  },
},
```

重启webpack之后重新登录，发现cookie的路径已经被重写到`/`了。
