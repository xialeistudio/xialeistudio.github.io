---
title: 不到20行代码实现golang路由调度
date: 2018-07-23 21:44:05
categories:
- engineering
---

## 项目地址

[go-dispatcher](https://github.com/xialeistudio/go-dispatcher)

## 本项目依赖

使用标准库实现，无额外依赖

## 为什么需要路由调度层

> golang http标准库只能精确匹配请求的URI，然后执行handler。现在一般web项目都至少有个Controller层，以struct实现，根据不同的请求路径派发到不同的方法中去。

## 路由调度器定义

由于golang暂时还不可以动态创建对象(比如java的`Class.forName("xxx").newInstance()`,xxx是任意存在的class名称)。所以需要手动注册一下controller关系。

1. 定义`routes`保存controller指针
2. 解析请求过来的URL查询参数，暂定`a`为`action名称`,`c`为`controller名称`，本文偷了下懒，没对PATH_INFO做处理，也没有对actionName的首字母自动大写，这个不影响本文要传达的核心内容，有兴趣的读者可以自行实现。
3. 根据URL中的`controllerName`找到对应的controller
4. 使用反射将当前请求对象的`*http.Request`和`http.ResponseWriter`设置到该Controller
5. 使用反射以及actionName对应该controller的方法

> 由于golang的继承不是一般的OOP，所以也没有父子类这种说法，路由注册那里只能使用interface{}

## 代码实现

### app/app.go

该文件为核心调度文件

```golang
package app

import (
	"net/http"
	"reflect"
	"fmt"
)

type application struct {
	routes map[string]interface{}
}

func New() *application {
	return &application{
		routes: make(map[string]interface{}),
	}
}

func (p *application) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	controllerName := r.URL.Query().Get("c")
	actionName := r.URL.Query().Get("a")
	if controllerName == "" || actionName == "" {
		http.Error(w, http.StatusText(http.StatusBadRequest), http.StatusBadRequest)
		return
	}
	route, ok := p.routes[controllerName]
	if !ok {
		http.Error(w, "Controller Not Found", http.StatusNotFound)
		return
	}
	ele := reflect.ValueOf(route).Elem()
	ele.FieldByName("Request").Set(reflect.ValueOf(r))
	ele.FieldByName("Response").Set(reflect.ValueOf(w))
	ele.MethodByName(actionName).Call([]reflect.Value{})
}

func (p *application) printRoutes() {
	for route, controller := range p.routes {
		ele := reflect.ValueOf(controller).Type().String()
		fmt.Printf("%s %s\n", route, ele)
	}
}

func (p *application) Get(route string, controller interface{}) {
	p.routes[route] = controller
}

func (p *application) Run(addr string) error {
	p.printRoutes()
	fmt.Printf("listen on %s\n", addr)
	return http.ListenAndServe(addr, p)
}
```

### app/controller.go

控制器"基类"

```golang
package app

import "net/http"

type Controller struct {
	Response http.ResponseWriter
	Request  *http.Request
}
```

### controller/site.go

具体业务逻辑类

```golang
package controllers

import (
	"fmt"
	"app"
)

type SiteController struct {
	app.Controller
}

func (p SiteController) Index() {
	fmt.Fprint(p.Response, p.Request.RequestURI)
}
```

### main.go

入口文件

```golang
package main

import (
	_ "github.com/go-sql-driver/mysql"
	"app"
	"controllers"
)

func main() {
	application := app.New()
	application.Get("site", &controllers.SiteController{})
	application.Run(":8080")
}
```

## 运行项目

1. 启动进程
2. 访问`http://localhost:8080?c=site&a=Index`会输出`/?c=site&a=Index`

## 写在最后

希望这个小小的项目能启发到各位读者，早日开发出适合自己的Web框架!