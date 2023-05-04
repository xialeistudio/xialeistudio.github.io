---
title: excel-stream Unknown Encoding错误问题
date: 2017-10-15 21:28:45
categories:
- engineering
---
项目上线有半年多了，一直没有出过问题，但是前几天升级过一次NodeJs到8.x的时候就出现过这个问题了。因为采用了消息队列，但是一到这里就挂，导致进程重复启动几百次。

# 报错信息

```
excel-stream/csv-stream/index.js 59 Buffer unknow encoding
```

# 问题排查
google了一下无果，后面发现反正源码反正自己有，倒不如自己改改，直接定位到相关代码即可。

```javascript
CSVStream.prototype.write = function(buffer,encoding){
	this._encoding = encoding || this._encoding;
	if(this._ended) throw new Error('Cannot write after end has been called.');
	if(buffer) this._buffer = Buffer.concat([this._buffer, buffer], this._buffer.length + buffer.length);
	if(this._paused) return false;
	this._parser.parse(this._buffer.toString(this._encoding));
	this._buffer = new Buffer(0);
	return !this._paused;
}
```

报错具体行数是**this._parser.parse(this._buffer.toString(this._encoding));**，错误很明显了，提示encoding错误。

那直接往上面找，发现**this._encoding = encoding || this._encoding**，这里就有可能传入的encoding导致了错误。

# 问题解决
这个项目已经3年没维护了，所以要修正问题的话，只能手动改了。

修改办法如下

```javascript
	this._parser.parse(this._buffer.toString(this._encoding));
```
改为

```javascript
	this._parser.parse(this._buffer.toString());
```

重新运行之后没有发现问题。