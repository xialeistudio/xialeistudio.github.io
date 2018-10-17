---
title: io.Reader游标引发的血案
date: 2018-10-17 21:32:03
categories:
- golang
tags:
- golang
- io.Reader
---

#背景
线上运行了一个图片合成程序，默认的小程序二维码中奖是小程序LOGO，不满足需求，所以将微信小程序二维码和用户头像合成在一张图片。
由于微信图片有时候返回的Content-Type不对应（比如内容是PNG的，头确是image/jpeg）所以使用jpeg/png/gif的顺序进行图片数据解析，哪个成功就返回解析结果。
#问题
总是出现诸如`invalid JPEG format: missing SOI marker`
#解决过程
我去查看jpeg.Decode的源码，如下：
```golang
func (d *decoder) decode(r io.Reader, configOnly bool) (image.Image, error) {
	d.r = r

	// Check for the Start Of Image marker.
	if err := d.readFull(d.tmp[:2]); err != nil {
		return nil, err
	}
	if d.tmp[0] != 0xff || d.tmp[1] != soiMarker {
		return nil, FormatError("missing SOI marker")
	}
...
```
soiMarker常量
```
	soiMarker  = 0xd8 // Start Of Image.
```
可以看到判断了第1个字节如果不是`0xff`或者第2个字节不是`0xd8`就报错。打印图片的bytes前几个字节如下：
```
[]byte{0xff, 0xd8, 0xff, 0xe0, 0x0, 0x10}
```
可以看到第1个字节和第2个字节满足要求，按理说不会出现这个问题，无奈只能求助于Google,搜索了
`invalid JPEG format: missing SOI marker`关键字出现一篇[Covert base64 string to JPG](https://stackoverflow.com/questions/46022262/covert-base64-string-to-jpg)引起了我的注意。
打开看到答案
>You need to create a new reader for each decoder:
```
pngI, errPng := png.Decode(bytes.NewReader(unbased))

// ...

jpgI, errJpg := jpeg.Decode(bytes.NewReader(unbased))
```
原来需要重新创建读取器，重新创建读取器后问题解决。
#后续
抱着打破砂锅问到底的心态，查看了一下`bytes.Reader`的源码，发现游标读取完后并未重置
```
// Read implements the io.Reader interface.
func (r *Reader) Read(b []byte) (n int, err error) {
	if r.i >= int64(len(r.s)) {
		return 0, io.EOF
	}
	r.prevRune = -1
	n = copy(b, r.s[r.i:])
	r.i += int64(n)
	return
}
```
Reader定义
```
type Reader struct {
	s        []byte
	i        int64 // current reading index
	prevRune int   // index of previous rune; or < 0
}
```
可以看到`r.i`就是游标了。问题圆满解决