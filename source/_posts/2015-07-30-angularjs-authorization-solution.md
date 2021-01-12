---
layout: post
title: angularjs 用户认证解决方案
date: 2015-07-30 00:42:58.000000000 +08:00
type: post
published: true
status: publish
categories:
- frontend
- angularjs
---
作为一个全栈ajax的mvvm框架，angularjs可谓如火如荼，可真正做到全栈ajax，首要面对的问题就是用户身份验证。   
本文的身份验证不采用cookie,而采用基于http Authorize 请求头的方式验证用户，此方式能做到永远只有一个用户同时在线（服务端同一时间只会接受一个合法的token请求，其他的请求返回401）。   

## Service

```javascript
app.factory('Authorize', function() {
  return {
    uid: '',
    token: '',
    logout: function() {
      this.uid = '';
      this.token = '';
      localStorage.removeItem('authorize.uid');
      localStorage.removeItem('authorize.token');
    }
  }
});
```

由于service是单例的。保存在service很合适，再看登录检测。

## 验证流程
1. app运行时主动读取localStorage中的authorize.uid和authorize.token字段，将这两个字段发送至后端接口验证，如果验证成功返回用户信息，验证失败返回http 401错误（未授权）。   

2. 如果localStorage没有上述两个字段，则检测url中是否有，如果有则写入本地localStorage之后发送至后端验证，如果没有，跳转至后端服务器的oauth接口进行授权拿之后，将openid和token写入queryString并回调到app页面，代码如下：

```javascript
Authorize.uid = $location.search().uid || localStorage.getItem('authorize.uid');
Authorize.token = $location.search().token || localStorage.getItem('authorize.token');
if (!Authorize.uid || !Authorize.token) {
  if (!Platform.isWechat) {
    Authorize.uid = 1001;
    Authorize.token = '2ddha3nry8';
  }
  else {
    location.href = CONFIG.api + '/auth/oauth?callback=' + encodeURIComponent($location.protocol() + "://" + $location.host() + ":" + $location.port() + "/#" + $location.path());
    return;
  }
}
//写入本地
localStorage.setItem('authorize.uid', Authorize.uid);
localStorage.setItem('authorize.token', Authorize.token);
//读取用户数据
var user = User.get({uid: Authorize.uid}, function() {
  $rootScope.user = user;
});
```

读取用户数据这边，采用的$resource服务封装，这里就不说了。

## 请求过程中的授权处理
接下来是比较重要的一点，如何在登陆后在每次请求头中注入Authorize信息，方法是**采用拦截器**。   
有一个问题，如果由于刷新过快，检测用户回调还没执行完，这时候访问所有接口都是401，这里就需要在$httpProvider上注入拦截器进行请求恢复了。代码如下：

```javascript
app.factory('AuthInjector', function($q, Authorize, $injector, CONFIG) {
  return {
    request: function(config) {
      if (Authorize.token) {
        config.headers.Authorization = 'Bearer ' + Authorize.token;
      }
      return config;
    },
    response: function(response) {
      var defer = $q.defer();
      defer.resolve(response);
      return defer.promise;
    },
    responseError: function(error) {
      //如果401且本地存在uid，则刷新accessToken
      if (error.status == 401) {
        //刷新请求
        var $http = $injector.get("$http");
        $http({
          method: 'GET',
          url: CONFIG.api + '/auth/token',
          params: {
            uid: Authorize.uid
          }
        }).success(function(data) {
          Authorize.token = data.token;
          //写入本地
          localStorage.setItem('authorize.token', data.token);
          return $http(error.config);
        });
      }
      else if (error.status == 422) {
        var resp;
        angular.forEach(error.data, function(item) {
          if (resp == undefined) {
            resp = item;
          }
        });
        return $q.reject(resp);
      }
      return $q.reject({
      message: '请求失败'
      });
    }
  }
});
```

原理就是所有的http请求一旦返回401就进行重新登录请求，最后一句

```javascript
return $http(error.config);
```

会将之前报401错误的请求恢复并重新执行一遍。

大体就是这么多，总结一下就是：
1. app.run中检测登录。
2. Authorize服务保存用户信息。
3. httpProvider中注入拦截器实现Authorize头的自动添加和401结果的请求恢复。