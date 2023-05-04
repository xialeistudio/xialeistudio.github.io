---
title: golang使用CSV导出大量数据
date: 2018-02-28 16:43:13
categories:
- engineering
---

最近在做一个导出功能，最初是使用[https://github.com/tealeg/xlsx](https://github.com/tealeg/xlsx)做的，但是发现导出有个30W行的excel时，这玩意内存彪到700M+，后来发现只是导出数据为表格，并没有其他东西，于是打算使用CSV导出。

## CSV格式简介

CSV本质上是个文本文件，该文件有以下要求：

1. 列之间用逗号分隔，行之间用换行分隔
2. 单元格如果有逗号，引号之类的字符，该单元格需要使用双引号括起来
3. 如果包含中文，需要使用GBK编码，否则会乱码

## golang实现

1. UTF8转GBK函数(需要 `go get golang.org/x/text/`)

    ```go
    func UTF82GBK(src string) (string, error) {
	    reader := transform.NewReader(strings.NewReader(src), simplifiedchinese.GBK.NewEncoder())
	    if buf, err := ioutil.ReadAll(reader); err != nil {
		    return "", err
	    } else {
		    return string(buf), nil
	    }
    }
    ```

2. 导出代码

    ```go
    filename := "test.csv"
    fp, err := os.Create(filename) // 创建文件句柄
    if err != nil {
        return nil, err
    }
    defer fp.Close()
    columns := []string{"姓名", "电话", "公司", "职位", "加入时间"}
    if line, err := util.UTF82GBK(strings.Join(columns, ",")); err == nil { // 写入一行
        fp.WriteString(line + "\n")
    }
    ```

其他语言也可以使用类似方法导出数据，只要满足CSV的几个条件即可。