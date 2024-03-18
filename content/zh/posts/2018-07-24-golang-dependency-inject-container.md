---
slug: golang-dependency-inject-container
title: golang不到30行代码实现依赖注入
date: 2018-07-24 18:32:51
categories:
- Engineering
---

## 项目地址

[go-di-demo](https://github.com/xialeistudio/di-demo)

## 本项目依赖

使用标准库实现，无额外依赖

## 依赖注入的优势

用java的人对于spring框架一定不会陌生，spring核心就是一个IoC(控制反转/依赖注入)容器，带来一个很大的优势是解耦。一般只依赖容器，而不依赖具体的类，当你的类有修改时，最多需要改动一下容器相关代码，业务代码并不受影响。

## golang的依赖注入原理

总的来说和java的差不多，步骤如下：(golang不支持动态创建对象，所以需要先手动创建对象然后注入，java可以直接动态创建对象)

1. 通过反射读取对象的依赖(golang是通过tag实现)
2. 在容器中查找有无该对象实例
3. 如果有该对象实例或者创建对象的工厂方法，则注入对象或使用工厂创建对象并注入
4. 如果无该对象实例，则报错

## 代码实现

一个典型的容器实现如下，依赖类型参考了spring的singleton/prototype，分别对象单例对象和实例对象:

```golang
package di

import (
	"sync"
	"reflect"
	"fmt"
	"strings"
	"errors"
)

var (
	ErrFactoryNotFound = errors.New("factory not found")
)

type factory = func() (interface{}, error)
// 容器
type Container struct {
	sync.Mutex
	singletons map[string]interface{}
	factories  map[string]factory
}
// 容器实例化
func NewContainer() *Container {
	return &Container{
		singletons: make(map[string]interface{}),
		factories:  make(map[string]factory),
	}
}

// 注册单例对象
func (p *Container) SetSingleton(name string, singleton interface{}) {
	p.Lock()
	p.singletons[name] = singleton
	p.Unlock()
}

// 获取单例对象
func (p *Container) GetSingleton(name string) interface{} {
	return p.singletons[name]
}

// 获取实例对象
func (p *Container) GetPrototype(name string) (interface{}, error) {
	factory, ok := p.factories[name]
	if !ok {
		return nil, ErrFactoryNotFound
	}
	return factory()
}

// 设置实例对象工厂
func (p *Container) SetPrototype(name string, factory factory) {
	p.Lock()
	p.factories[name] = factory
	p.Unlock()
}

// 注入依赖
func (p *Container) Ensure(instance interface{}) error {
	elemType := reflect.TypeOf(instance).Elem()
	ele := reflect.ValueOf(instance).Elem()
	for i := 0; i < elemType.NumField(); i++ { // 遍历字段
		fieldType := elemType.Field(i)
		tag := fieldType.Tag.Get("di") // 获取tag
		diName := p.injectName(tag)
		if diName == "" {
			continue
		}
		var (
			diInstance interface{}
			err        error
		)
		if p.isSingleton(tag) {
			diInstance = p.GetSingleton(diName)
		}
		if p.isPrototype(tag) {
			diInstance, err = p.GetPrototype(diName)
		}
		if err != nil {
			return err
		}
		if diInstance == nil {
			return errors.New(diName + " dependency not found")
		}
		ele.Field(i).Set(reflect.ValueOf(diInstance))
	}
	return nil
}

// 获取需要注入的依赖名称
func (p *Container) injectName(tag string) string {
	tags := strings.Split(tag, ",")
	if len(tags) == 0 {
		return ""
	}
	return tags[0]
}

// 检测是否单例依赖
func (p *Container) isSingleton(tag string) bool {
	tags := strings.Split(tag, ",")
	for _, name := range tags {
		if name == "prototype" {
			return false
		}
	}
	return true
}

// 检测是否实例依赖
func (p *Container) isPrototype(tag string) bool {
	tags := strings.Split(tag, ",")
	for _, name := range tags {
		if name == "prototype" {
			return true
		}
	}
	return false
}

// 打印容器内部实例
func (p *Container) String() string {
	lines := make([]string, 0, len(p.singletons)+len(p.factories)+2)
	lines = append(lines, "singletons:")
	for name, item := range p.singletons {
		line := fmt.Sprintf("  %s: %x %s", name, &item, reflect.TypeOf(item).String())
		lines = append(lines, line)
	}
	lines = append(lines, "factories:")
	for name, item := range p.factories {
		line := fmt.Sprintf("  %s: %x %s", name, &item, reflect.TypeOf(item).String())
		lines = append(lines, line)
	}
	return strings.Join(lines, "\n")
}
```

1. 最重要的是`Ensure`方法，该方法扫描实例的所有export字段，并读取di标签，如果有该标签则启动注入。
2. 判断di标签的类型来确定注入singleton或者prototype对象

## 测试

1. 单例对象在整个容器中只有一个实例，所以不管在何处注入，获取到的指针一定是一样的。
2. 实例对象是通过同一个工厂方法创建的，所以每个实例的指针不可以相同。

下面是测试入口代码，完整代码在github仓库，有兴趣的可以翻阅：

```golang
package main

import (
	"di"
	"database/sql"
	"fmt"
	"os"
	_ "github.com/go-sql-driver/mysql"
	"demo"
)

func main() {
	container := di.NewContainer()
	db, err := sql.Open("mysql", "root:root@tcp(localhost)/sampledb")
	if err != nil {
		fmt.Printf("error: %s\n", err.Error())
		os.Exit(1)
	}
	container.SetSingleton("db", db)
	container.SetPrototype("b", func() (interface{}, error) {
		return demo.NewB(), nil
	})

	a := demo.NewA()
	if err := container.Ensure(a); err != nil {
		fmt.Println(err)
		return
	}
	// 打印指针，确保单例和实例的指针地址
	fmt.Printf("db: %p\ndb1: %p\nb: %p\nb1: %p\n", a.Db, a.Db1, &a.B, &a.B1)
}
```

执行之后打印出来的结果为：

```
db: 0xc4200b6140
db1: 0xc4200b6140
b: 0xc4200a0330
b1: 0xc4200a0338
```

可以看到两个db实例的指针一样，说明是同一个实例，而两个b的指针不同，说明不是一个实例。

## 写在最后

通过依赖注入可以很好的管理多个对象之间的实例化以及依赖关系，配合配置文件在应用初始化阶段将需要注入的实例注册到容器中，在应用的任何地方只需要在实例化时注入容器即可。没有额外依赖。