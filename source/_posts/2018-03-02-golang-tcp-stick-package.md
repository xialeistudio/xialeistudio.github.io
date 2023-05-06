---
title: golang解决TCP粘包问题
date: 2018-03-02 17:50:31
categories:
- Engineering
tags:
- protocol
---

什么是TCP粘包问题以及为什么会产生TCP粘包，本文不加讨论。本文使用golang的`bufio.Scanner`来实现自定义协议解包。

## 协议数据包定义

本文模拟一个日志服务器，该服务器接收客户端传到的数据包并显示出来

```go
type Package struct {
	Version        [2]byte // 协议版本，暂定V1
	Length         int16   // 数据部分长度
	Timestamp      int64   // 时间戳
	HostnameLength int16   // 主机名长度
	Hostname       []byte  // 主机名
	TagLength      int16   // 标签长度
	Tag            []byte  // 标签
	Msg            []byte  // 日志数据
}
```

协议定义部分没有什么好讲的，根据具体的业务逻辑定义即可。

## 数据打包

由于TCP协议是语言无关的协议，所以直接把协议数据包结构体发送到TCP连接中也是不可能的，只能发送字节流数据，所以需要自己实现数据编码。所幸golang提供了`binary`来帮助我们实现网络字节编码。

```go
func (p *Package) Pack(writer io.Writer) error {
	var err error
	err = binary.Write(writer, binary.BigEndian, &p.Version)
	err = binary.Write(writer, binary.BigEndian, &p.Length)
	err = binary.Write(writer, binary.BigEndian, &p.Timestamp)
	err = binary.Write(writer, binary.BigEndian, &p.HostnameLength)
	err = binary.Write(writer, binary.BigEndian, &p.Hostname)
	err = binary.Write(writer, binary.BigEndian, &p.TagLength)
	err = binary.Write(writer, binary.BigEndian, &p.Tag)
	err = binary.Write(writer, binary.BigEndian, &p.Msg)
	return err
}
```

Pack方法的输出目标为`io.Writer`，有利于接口扩展，只要实现了该接口即可编码数据写入。`binary.BigEndian`是字节序，本文暂时不讨论，有需要的读者可以自行查找资料研究。

## 数据解包

解包需要将TCP数据包解析到结构体中，接下来会讲为什么需要添加几个`数据无关`的长度字段。

```go
func (p *Package) Unpack(reader io.Reader) error {
	var err error
	err = binary.Read(reader, binary.BigEndian, &p.Version)
	err = binary.Read(reader, binary.BigEndian, &p.Length)
	err = binary.Read(reader, binary.BigEndian, &p.Timestamp)
	err = binary.Read(reader, binary.BigEndian, &p.HostnameLength)
	p.Hostname = make([]byte, p.HostnameLength)
	err = binary.Read(reader, binary.BigEndian, &p.Hostname)
	err = binary.Read(reader, binary.BigEndian, &p.TagLength)
	p.Tag = make([]byte, p.TagLength)
	err = binary.Read(reader, binary.BigEndian, &p.Tag)
	p.Msg = make([]byte, p.Length-8-2-p.HostnameLength-2-p.TagLength)
	err = binary.Read(reader, binary.BigEndian, &p.Msg)
	return err
}
```

由于主机名、标签这种数据是不固定长度的，所以需要两个字节来标识数据长度，否则读取的时候只知道一个总的数据长度是无法区分主机名、标签名、日志数据的。

## 数据包的粘包问题解决

上文只是解决了`编码/解码`问题，前提是收到的数据包没有产生粘包问题，解决粘包就是要正确分割字节流中的数据。一般有以下做法：
1. 定长分隔(每个数据包最大为该长度) 缺点是数据不足时会浪费传输资源
2. 特定字符分隔(如\r\n) 缺点是如果正文中有\r\n就会导致问题
3. 在数据包中添加长度字段(本文采用的)

golang提供了`bufio.Scanner`来解决粘包问题。

```go
scanner := bufio.NewScanner(reader) // reader为实现了io.Reader接口的对象，如net.Conn
scanner.Split(func(data []byte, atEOF bool) (advance int, token []byte, err error) {
	if !atEOF && data[0] == 'V' { // 由于我们定义的数据包头最开始为两个字节的版本号，所以只有以V开头的数据包才处理
		if len(data) > 4 { // 如果收到的数据>4个字节(2字节版本号+2字节数据包长度)
			length := int16(0)
			binary.Read(bytes.NewReader(data[2:4]), binary.BigEndian, &length) // 读取数据包第3-4字节(int16)=>数据部分长度
			if int(length)+4 <= len(data) { // 如果读取到的数据正文长度+2字节版本号+2字节数据长度不超过读到的数据(实际上就是成功完整的解析出了一个包)
				return int(length) + 4, data[:int(length)+4], nil
			}
		}
	}
	return
})
// 打印接收到的数据包
for scanner.Scan() {
	scannedPack := new(Package)
	scannedPack.Unpack(bytes.NewReader(scanner.Bytes()))
	log.Println(scannedPack)
}
```

本文的核心就在于`scanner.Split`方法，该方法用来解析TCP数据包

## 完整源码

```go
package main

import (
	"bufio"
	"bytes"
	"encoding/binary"
	"fmt"
	"io"
	"log"
	"os"
	"time"
)

type Package struct {
	Version        [2]byte // 协议版本
	Length         int16   // 数据部分长度
	Timestamp      int64   // 时间戳
	HostnameLength int16   // 主机名长度
	Hostname       []byte  // 主机名
	TagLength      int16   // Tag长度
	Tag            []byte  // Tag
	Msg            []byte  // 数据部分长度
}

func (p *Package) Pack(writer io.Writer) error {
	var err error
	err = binary.Write(writer, binary.BigEndian, &p.Version)
	err = binary.Write(writer, binary.BigEndian, &p.Length)
	err = binary.Write(writer, binary.BigEndian, &p.Timestamp)
	err = binary.Write(writer, binary.BigEndian, &p.HostnameLength)
	err = binary.Write(writer, binary.BigEndian, &p.Hostname)
	err = binary.Write(writer, binary.BigEndian, &p.TagLength)
	err = binary.Write(writer, binary.BigEndian, &p.Tag)
	err = binary.Write(writer, binary.BigEndian, &p.Msg)
	return err
}
func (p *Package) Unpack(reader io.Reader) error {
	var err error
	err = binary.Read(reader, binary.BigEndian, &p.Version)
	err = binary.Read(reader, binary.BigEndian, &p.Length)
	err = binary.Read(reader, binary.BigEndian, &p.Timestamp)
	err = binary.Read(reader, binary.BigEndian, &p.HostnameLength)
	p.Hostname = make([]byte, p.HostnameLength)
	err = binary.Read(reader, binary.BigEndian, &p.Hostname)
	err = binary.Read(reader, binary.BigEndian, &p.TagLength)
	p.Tag = make([]byte, p.TagLength)
	err = binary.Read(reader, binary.BigEndian, &p.Tag)
	p.Msg = make([]byte, p.Length-8-2-p.HostnameLength-2-p.TagLength)
	err = binary.Read(reader, binary.BigEndian, &p.Msg)
	return err
}

func (p *Package) String() string {
	return fmt.Sprintf("version:%s length:%d timestamp:%d hostname:%s tag:%s msg:%s",
		p.Version,
		p.Length,
		p.Timestamp,
		p.Hostname,
		p.Tag,
		p.Msg,
	)
}

func main() {
	hostname, err := os.Hostname()
	if err != nil {
		log.Fatal(err)
	}

	pack := &Package{
		Version:        [2]byte{'V', '1'},
		Timestamp:      time.Now().Unix(),
		HostnameLength: int16(len(hostname)),
		Hostname:       []byte(hostname),
		TagLength:      4,
		Tag:            []byte("demo"),
		Msg:            []byte(("现在时间是:" + time.Now().Format("2006-01-02 15:04:05"))),
	}
	pack.Length = 8 + 2 + pack.HostnameLength + 2 + pack.TagLength + int16(len(pack.Msg))

	buf := new(bytes.Buffer)
	// 写入四次，模拟TCP粘包效果
	pack.Pack(buf)
	pack.Pack(buf)
	pack.Pack(buf)
	pack.Pack(buf)
	// scanner
	scanner := bufio.NewScanner(buf)
	scanner.Split(func(data []byte, atEOF bool) (advance int, token []byte, err error) {
		if !atEOF && data[0] == 'V' {
			if len(data) > 4 {
				length := int16(0)
				binary.Read(bytes.NewReader(data[2:4]), binary.BigEndian, &length)
				if int(length)+4 <= len(data) {
					return int(length) + 4, data[:int(length)+4], nil
				}
			}
		}
		return
	})
	for scanner.Scan() {
		scannedPack := new(Package)
		scannedPack.Unpack(bytes.NewReader(scanner.Bytes()))
		log.Println(scannedPack)
	}
	if err := scanner.Err(); err != nil {
		log.Fatal("无效数据包")
	}
}
```

## 写在最后

golang作为一门强大的网络编程语言，实现自定义协议是非常重要的，实际上实现自定义协议也不是很难，以下几个步骤：
1. 数据包编码
2. 数据包解码
3. 处理TCP粘包问题
4. 断线重连(可以使用心跳实现)(非必须)