---
title: PlanUML指南
date: 2021-06-04 15:17:06
categories:
- engineering
---

## 简介

> **统一建模语言**（英语：Unified Modeling Language，缩写 UML）是非专利的第三代[建模](https://zh.wikipedia.org/w/index.php?title=对象建模语言&action=edit&redlink=1)和[规约语言](https://zh.wikipedia.org/wiki/规约语言)。UML是一种开放的方法，用于说明、可视化、构建和编写一个正在开发的、面向对象的、软件密集系统的制品的开放方法

编写UML的软件很多，但是基本是可视化的，需要手动编写，本文主要介绍基于文本的UML编写工具——PlantUML。

## 安装

PlantUML有以下依赖：

1. graphviz
2. jdk
3. Jetbrains IDE插件(可选，本文推荐)

### 安装graphviz

本文使用`Homebrew`安装`graphviz`，终端执行以下命令安装`graphviz`。

```bash
brew install graphviz
```

安装完毕后查看版本信息。

```bash
dot -v
```

输出如下：

```
dot - graphviz version 2.47.0 (20210316.0004)
libdir = "/usr/local/Cellar/graphviz/2.47.0/lib/graphviz"
Activated plugin library: libgvplugin_dot_layout.6.dylib
Using layout: dot:dot_layout
Activated plugin library: libgvplugin_core.6.dylib
Using render: dot:core
Using device: dot:dot:core
The plugin configuration file:
	/usr/local/Cellar/graphviz/2.47.0/lib/graphviz/config6
		was successfully loaded.
 render	:  cairo dot dot_json fig gd json json0 map mp pic pov ps quartz svg tk visio vml vrml xdot xdot_json
 layout	:  circo dot fdp neato nop nop1 nop2 osage patchwork sfdp twopi
 textlayout	:  textlayout
 device	:  bmp canon cgimage cmap cmapx cmapx_np dot dot_json eps exr fig gd gd2 gif gv icns ico imap imap_np ismap jp2 jpe jpeg jpg json json0 mp pct pdf pic pict plain plain-ext png pov ps ps2 psd sgi svg svgz tga tif tiff tk vdx vml vmlz vrml wbmp webp xdot xdot1.2 xdot1.4 xdot_json
 loadimage	:  (lib) bmp eps gd gd2 gif jpe jpeg jpg pdf png ps svg webp xbm
```

### jdk

本文使用`Homebrew`安装`openjdk`即可，终端执行以下命令安装`openjdk`。

```bash
brew install openjdk
```

安装完毕后查看版本信息。

```bash
java -version
```

输出如下：

```
openjdk version "11.0.10" 2021-01-19
OpenJDK Runtime Environment (build 11.0.10+9)
OpenJDK 64-Bit Server VM (build 11.0.10+9, mixed mode)
```

### Jetbrains IDE插件安装

本文以`Goland`为例。

1. 打开IDE设置，打开`Plugins`窗口，搜索`PlantUML integration`

2. 安装完毕后重启IDE

3. 打开IDE设置，搜索`plantuml`，确保`Remote rendering`已关闭

![image-20210604154007098](https://static.ddhigh.com/blog//2021/06/04/1622792407142095000.png)

## PlantUML语法

以最常用的时序图、类图、流程图、组件图举例。

### 时序图

#### Get Started

1. IDE新建一个空项目，打开项目之后，右键新建文件

![image-20210604152912197](https://static.ddhigh.com/blog//2021/06/04/1622791752260150000.png)

2. 选择`Sequence`

![image-20210604152935751](https://static.ddhigh.com/blog//2021/06/04/1622791775795758000.png)

3. PlantUML菜单项说明

![image-20210604155009752](https://static.ddhigh.com/blog//2021/06/04/1622793009802684000.png)

4. 以微信网页授权为例编写时序图。

```
@startuml
'https://plantuml.com/sequence-diagram

'启用自动编号
autonumber
'生命线自动激活
autoactivate on

actor 用户

用户 -> 应用服务器: 获取用户信息
应用服务器 -> 微信服务器: 跳转授权链接:(appid,scope,callback)
微信服务器 -> 用户: 请求用户授权
return 允许授权
return 返回授权code
应用服务器 -> 微信服务器: 获取用户access_token(appid,secret,code)
return 返回access_token+openid
应用服务器 -> 微信服务器: 获取用户信息(openid,access_token)
return 用户信息
return 用户信息

@enduml
```

5. 渲染效果

![image-20210604153910674](https://static.ddhigh.com/blog//2021/06/04/1622792350734661000.png)

#### 语法说明

##### 标记声明

```
@startuml和@enduml是PlantUML的开始结束标记，无需更改。
autonumber 打开启动编号，也就是每个步骤之前都有数字编号，打开之后整个流程更加清晰
autoactivate on 打开生命线自动激活，需要配合`return`使用
actor 用户 声明`用户`的类型是actor(行为人)
```

##### 时序声明

+ 使用`->`来声明一个时序操作，`:`后面可以附加消息
+ 使用`return`来返回消息给调用者

##### 声明参与者

默认情况下参与者为矩形，无法看出实际类型。实际应用中，会有数据库、消息队列等等参与者，使用以下关键字来改变参与者的图例。

```
actor 用户
database 数据库
queue 消息队列
```

![image-20210604154840162](https://static.ddhigh.com/blog//2021/06/04/1622792920216896000.png)

### 类图

类图是UML中非常重要的一种类型，能够在实际编码之前为我们提供OOP的详细设计。

#### Get Started

1. IDE新建一个空项目，打开项目之后，右键新建文件

![image-20210604152912197](https://static.ddhigh.com/blog//2021/06/04/1622791752260150000.png)

2. 选择`Class`

![image-20210604155301322](https://static.ddhigh.com/blog/2021/06/04/1622793181374871000.png)

3. 以一个上传类为例编写类图

```
@startuml
'https://plantuml.com/class-diagram

namespace com.ddhigh.uploader {
 interface Uploader {
  + String Upload(String filename) Throws IOException
 }

 namespace qiniu {
  class QiniuUploader implements Uploader {
- client: qiniu.Client
--
+ String Upload(String filename) Throws IOException
  }
  QiniuUploader *-- qiniu.Client
 }

 package aliyun {
  class AliyunUploader implements Uploader {
- client: aliyun.Client
--
+ String Upload(String filename) Throws IOException
  }
  AliyunUploader *-- aliyun.Client
 }

 class UploaderFacade {
  - uploaders: List<Uploader>
  --
  + List<String> Upload(String filename) Throws IOException
 }
 UploaderFacade o-- Uploader
}

@enduml
```

4. 渲染效果

![image-20210604155821009](https://static.ddhigh.com/blog/2021/06/04/1622793501066543000.png)

##### 语法说明

##### 包

建议使用`namespace`关键字声明包，`package`声明的包内的类名必须全局唯一(无视package)，而`namespace`只要求该`namespace`内唯一即可。

##### class/interface

与实际编程语言几乎无差别，比如上面例子中采用的是java语法。

##### 可见性

PlantUML支持3种可见性：

+ `-` 私有级别 `private`
+ `#` 保护级别 `protected`
+ `+` 公有级别 `public`

##### 元素关系

PlantUML主要有以下3种关系：

1. 扩展: 包含`implements`和`extends`
2. 聚合: 使用`o--`，`左边`的包含`右边`的
3. 组合: 使用`*--`,`左边`的依赖`右边`的

> 组合和聚合的区别：(以上面的图为例)
>
> 1. 组合：QiniuUploader必须依赖Client才能提供上传功能，组合一般是1对1的。
> 2. 聚合：UploadFacade可以依赖多个Uploader实例，也可以依赖0个实例(只是这时候不会有文件上传了)，聚合一般是1对多的。

### 流程图

在梳理复杂业务逻辑时，善用流程图能帮我们更加清晰地梳理清楚，也方便我们和其他人员进行沟通（非开发人员基本看不懂代码）。

#### Get Started

1. IDE新建一个空项目，打开项目之后，右键新建文件

![image-20210604152912197](https://static.ddhigh.com/blog//2021/06/04/1622791752260150000.png)

2. 新建`Activity`类型文件

![image-20210604160929588](https://static.ddhigh.com/blog/2021/06/04/1622794169645334000.png)

3. 下面以一个`授权获取用户openid并插入数据库，然后查询用户好友进行消息推送`的场景编写流程图

```
@startuml
'https://plantuml.com/activity-diagram-beta

start
:使用code,appid,secret请求微信服务器获取access_token和openid;
:使用access_token和openid请求微信服务器获取用户信息;
:查询数据库openid是否存在;
if (数据库查询失败?) then (是)
stop
elseif (用户已存在?) then (是)
:更新用户信息;
else (否)
:新建用户并绑定openid;
endif

:获取用户好友列表;
while(好友列表遍历完成?) is (否)
:推送消息给好友;
endwhile(是)
stop

@enduml
```

4. 渲染效果

![image-20210604161522881](https://static.ddhigh.com/blog/2021/06/04/1622794522917043000.png)

#### 语法说明

+ 开始和结束: 使用`start`和`stop`

+ 处理语句: 使用`:`和`;`包裹该流程
+ 条件判断: 使用`if`,`elseif`,`else`,`endif`,`then`
+ 循环语句: 使用`while`,`is`,`endwhile`编写

### 组件图

现阶段组件化MVVM框架大行其道，具有代表性的有`Vue`,`React`和`Angular`。我们可以使用组件图来绘制组件关系，简单易懂。

##### Get Started

1. IDE新建一个空项目，打开项目之后，右键新建文件

![image-20210604152912197](https://static.ddhigh.com/blog//2021/06/04/1622791752260150000.png)

2. 选择`Component`

![image-20210604162020830](https://static.ddhigh.com/blog/2021/06/04/1622794820895677000.png)

3. 以微信首页聊天列表为例绘制组件关系图

```
@startuml
'https://plantuml.com/component-diagram

package widgets {
 [SearchBar] --> [Text]
 [SearchBar] --> [Icon]
 [NavigationBar] --> [Text]
 [NavigationBar] --> [Icon]
 
 [ListView] --> [ListItem]
 [ListItem] --> [Image]
 [ListItem] --> [Text]
}

package routes {
 [Home] --> [NavigationBar]
 [Home] --> [SearchBar]
 [Home] --> [ListView]
}


@enduml
```

4. 渲染效果

![image-20210604162521451](https://static.ddhigh.com/blog/2021/06/04/1622795518286015000.png)

> 依赖关系如下：
>
> + 首页: 导航栏, 搜索框，列表
> + 导航栏: 文本，图标
> + 搜索框: 文本，图标
> + 列表: 列表项
> + 列表项: 文本，图片

##### 语法说明

+ package 声明包，同一个包内的组件是类似地位
+ `[组件名]`声明组件，`组件名`在单个文件内是唯一的
+ `-->` 声明依赖关系，`左边`依赖`右边`

(完)