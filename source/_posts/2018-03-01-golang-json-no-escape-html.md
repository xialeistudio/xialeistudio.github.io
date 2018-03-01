---
title: golang JSON编码时保留HTML标签
date: 2018-03-01 11:40:51
categories:
- golang
tags:
- json
---

golang默认编码JSON时会将HTML标签中的尖括号编码为`\u003c`这种unicode字符。而最近在开发的微信客服消息推送就会出现以下结果

```text
\u003ca href='https://www.example.com'\u003e点击进入\u003c/a\u003e
```

查看golang的json包发现json编码器有个方法`SetEscapeHTML`方法，接收一个bool值来设置是否保留HTML标签。

## 问题

json的Encoder只能编码到实现了`io.Writer`接口的对象中去，而本例中需要编码到一个`[]byte`切片中。

## 解决

查找资料发现`bytes.Buffer`对象实现了`io.Writer`接口。所以最终代码如下：

```golang
func BuildJson(data map[string]interface{}) ([]byte, error) {
    buf := bytes.NewBufferString("")
    encoder := json.NewEncoder(buf)
	encoder.SetEscapeHTML(false)
	if err := encoder.Encode(&data); err != nil {
		return nil, err
	} else {
		return buf.Bytes(), nil
	}
}
```

经过测试，输出接口符合要求。