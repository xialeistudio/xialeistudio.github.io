---
layout: post
title: 安装nodejs的shell脚本
date: 2016-05-14 18:27:29.000000000 +08:00
type: post
published: true
status: publish
categories:
- Engineering
---
## 脚本定义

```bash
#!/bin/bash
export NVM_NODEJS_ORG_MIRROR=https://npm.taobao.org/mirrors/node
git clone https://github.com/creationix/nvm.git ~/.nvm
source ~/.nvm/nvm.sh
nvm install 4.4.2
```

## 脚本执行

```bash
chmod +x ./install.sh
./install.sh
```

nodejs版本大家可以 根据实际需要进行选择