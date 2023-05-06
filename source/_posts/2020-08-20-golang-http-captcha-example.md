---
title: Golang Http 验证码示例
date: 2020-08-20 17:18:38
categories:
- Engineering
---

> 验证码（CAPTCHA）是“Completely Automated Public Turing test to tell Computers and Humans Apart”（全自动区分[计算机](https://baike.baidu.com/item/计算机)和人类的[图灵测试](https://baike.baidu.com/item/图灵测试)）的缩写，是一种区分用户是计算机还是人的公共全自动[程序](https://baike.baidu.com/item/程序/71525)。可以防止：恶意破解密码、[刷票](https://baike.baidu.com/item/刷票/6540942)、论坛灌水，有效防止某个黑客对某一个特定注册用户用特定程序暴力破解方式进行不断的登陆尝试，实际上用验证码是现在很多网站通行的方式，我们利用比较简易的方式实现了这个功能。这个问题可以由计算机生成并评判，但是必须只有人类才能解答。由于计算机无法解答CAPTCHA的问题，所以回答出问题的用户就可以被认为是人类。

## 传统网站验证码工作机制

1. 客户端请求服务器获取验证码图片
2. 服务器生成随机串(验证码值)写入Session，并将验证码值写入到图片中返回给客户端
3. 客户端输入图片上的字符串提交给服务器验证
4. 服务器比对客户端提交的字符串值和 Session 中是否匹配，如果匹配则通过验证

由于服务器生成的验证码值从始至终均未返回给客户端，因此，客户端只能从图片中识别验证码字符串，从而保证人机校验逻辑。

## Go的HTTP验证码

### 思路

Go 语言的 HTTP 服务器默认不支持 Session，因此验证码值需要换个思路存储，以下是不使用 Session 的逻辑

1. 客户端请求服务器获取验证码ID
2. 服务器生成验证码 ID，并生成验证码值，将 ID 和值的映射关系记录到内存或缓存，并将 ID 返回给客户端
3. 客户端根据返回的 ID 请求服务器获取验证码图片
4. 服务器获取到验证码 ID，从内存或缓存中取出验证码值，将该值写入图片并将图片返回给客户端
5. 客户端提交验证码 ID（第1步获得）和验证码值给服务器验证
6. 服务器获取验证码 ID，从内存或缓存中取出验证码值与客户端提交的验证码值比对

### 示例

1. 安装验证码依赖

   ```
   github.com/dchest/captcha
   ```

2. 代码实现

   ```go
   package main
   
   import (
   	"fmt"
   	"github.com/dchest/captcha"
   	"log"
   	"net/http"
   )
   
   func main() {
   	// 获取验证码 ID
   	http.HandleFunc("/captcha/generate", func(w http.ResponseWriter, r *http.Request) {
   		id := captcha.NewLen(6)
   		if _, err := fmt.Fprint(w, id); err != nil {
   			log.Println("generate captcha error", err)
   		}
   	})
   	// 获取验证码图片
   	http.HandleFunc("/captcha/image", func(w http.ResponseWriter, r *http.Request) {
   		id := r.URL.Query().Get("id")
   		if id == "" {
   			http.Error(w, "Bad Request", http.StatusBadRequest)
   			return
   		}
   		w.Header().Set("Content-Type", "image/png")
   		if err := captcha.WriteImage(w, id, 120, 80); err != nil {
   			log.Println("show captcha error", err)
   		}
   	})
   	// 业务处理
   	http.HandleFunc("/login", func(w http.ResponseWriter, r *http.Request) {
   		if err := r.ParseForm(); err != nil {
   			log.Println("parseForm error", err)
   			http.Error(w, "Internal Error", http.StatusInternalServerError)
   			return
   		}
   		// 获取验证码 ID 和验证码值
   		id := r.FormValue("id")
   		value := r.FormValue("value")
   		// 比对提交的验证码值和内存中的验证码值
   		if captcha.VerifyString(id, value) {
   			fmt.Fprint(w, "ok")
   		} else {
   			fmt.Fprint(w, "mismatch")
   		}
   	})
   	log.Fatal(http.ListenAndServe(":8080", nil))
   }
   ```

3. 运行

   1. 访问/captcha/generate获得验证码 ID
   2. 访问/captcha/image?id=验证码 ID
   3. 访问/login，并输入第一步的验证码 ID 和第二步的验证码值即可查看验证结果

## 项目地址

[https://github.com/xialeistudio/go-http-captcha-example](https://github.com/xialeistudio/go-http-captcha-example)

