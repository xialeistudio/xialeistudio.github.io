---
layout: post
title: Linux删除乱码文件
date: 2014-09-13 15:19:49.000000000 +08:00
type: post
published: true
status: publish
categories:
- engineering
---
shell终端中有时候中文文件名会出现乱码，导致很多操作都不能进行，一个最简单的就是删除了。

linux中每个文件有类似于ID的东西，使用以下命令查看

```bash
ll -i
```

显示出来的第一个数字就是文件的inum

可以利用以下命令进行删除操作,假设inum为111111

```bash
find . -inum 11111 -exec rm -f {} \
```

rm -f {}可以自行替换为自己需要操作的命令。
这样的话，不管什么文件都可以操作，只要有inum!