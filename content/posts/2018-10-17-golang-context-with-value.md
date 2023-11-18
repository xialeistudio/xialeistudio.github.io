---
slug: golang-context-with-value
title: 一起学context（一）——上下文值传递
date: 2018-10-17 21:50:20
categories:
- Engineering
tags:
- context
---

# 系列开篇
本文开始将针对context的用法进行系统化讨论，在这里你将能够在工作中合理使用context解决一些比较棘手的问题。

context处理超时处理之外还可以用来保存数据，当你需要在多个上下文传递时传递数据，那么本文提到的知识可以排上用场。

# 示例代码

示例代码为一个简单的http服务，流程是登录之后会跳转首页，首页通过guard中间件进行鉴权。当然，示例代码未做其他诸如连接数据库之类的处理，这不是本文的重点。
守卫函数读取cookie之后将cookie值写入context并向下传递，在整个请求中可以说是“透明”的。当访问到需要保护的接口时检测到没有提供cookie，则直接终端请求，否则通过r.WithContext将username的值存入cookie，避免的业务接口直接读取cookie的弊端。因为如果后期更改鉴权算法的话，业务代码可以不用更改，直接更改中间件即可。

```golang
package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"time"
)

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("/", guard(home))
	mux.HandleFunc("/login", login)
	log.Fatal(http.ListenAndServe(":8080", mux))
}

// 登录
func login(w http.ResponseWriter, r *http.Request) {
	if r.URL.Query().Get("username") != "root" {
		http.Error(w, http.StatusText(401), 401)
		return
	}
	cookie := &http.Cookie{Name: "username", Value: "root", Expires: time.Now().Add(time.Hour)}
	http.SetCookie(w, cookie)
	http.Redirect(w, r, "/", 302)
}

func home(w http.ResponseWriter, r *http.Request) {
	username := r.Context().Value("username")
	fmt.Fprintf(w, "welcome login: %s", username.(string))
}

// 守卫
func guard(handleFunc http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		// check username
		log.Printf("%s - %s\n", r.Method, r.RequestURI)
		cookie, err := r.Cookie("username")
		if err != nil || cookie == nil { // 如果username为空直接拦截
			http.Error(w, http.StatusText(401), 401)
			return
		}
		handleFunc(w, r.WithContext(context.WithValue(r.Context(), "username", cookie.Value)))
	}
}
```

本文的代码就这么多，内容也很少，希望大家能好好用上这个利器。
关于context与协程超时控制将在下一篇文章中讲到。