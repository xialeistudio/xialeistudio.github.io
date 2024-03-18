---
slug: golang-travis-ci
title: golang使用travis进行持续集成
date: 2018-04-08 17:40:37
categories:
- Engineering
tags:
- ci
---

虽然golang的工程工具已经非常完善了，比如测试、代码格式化等等。但是如果开发library开源到github的话，这些东西是可以使用自动化工具完成的，那就是 [travis](https://www.travis-ci.org/)

## 使用步骤

1. 开发好需要集成的library以及测试用例
1. 在项目根目录新建`.travis.yml`文件
    ```yaml
    language: go
    go:
    - 1.x
    - '1.8'
    - '1.9'
    - 1.10.x
    script:
    - go test -v ./...
    ```
1. 提交到github
1. 打开[https://www.travis-ci.org/](https://www.travis-ci.org/)并使用github账号登录
1. 登录之后点击左边 **"My Repositories"** 旁边的 **"+"** 号添加项目（点击项目前面的滑块即可）
1. 更改项目文件，push一次到github，此时travis会自动运行测试脚本

## 敏感数据加密

如果你的测试用例需要使用到敏感数据（如一些密钥等等），那需要用travis将你的敏感数据加密(以Mac为例)

1. 终端执行`sudo gem install travis`
1. 在项目根目录打开终端执行`travis encrypt AMAP_KEY="xxxx" --add` **AMAP_KEY**是环境变量名称，程序读取环境变量可以得到真实的key，**xxxx**是敏感数据
1. 执行完毕后，**.travis.yml** 会发生更改, 会添加如下内容(secure可能不一致)
    ```yaml
    env:
    global:
        secure: kr5JHNTYsh/jezvk88qP91arb+UD/op/5CyOFY7uNYpJ6ZSsJY5fDKyZHjf0VSFmaYqJFMPl6uCASE9baiepeGvBFcy8aI9CNsbLzj2uBNjqqYPmvYGnBjpzp8yknVJKRTitF/kkWtzZcWImHnpvNGHuzXxp/EIBeJtNwjcCRoP/qfGhlZKbLsYFvlWkmRYb0dr8RM5mlmGXPZi8q7m+soVRO8Zjr4QQccybgmhonxlcUrHr6ro+yjjQefoJXRufqoRX0sGyecGYucC4nUpWl5hkDPkQE+Mekhz+rF657SwNsn8nXOFnnUuwsPXE26ak5xF1roEcFk2CpwGZuT7smJZPtw1inXFdIaW+4qllbyxMJkylvFZa5IcvLT3+/eKaQc8Fg6PoxJH0PF3RdtoQVB31cQiPWNm1SecQ6wC64WA/5qN4T5OoRfpt60BFDAITdS62dQGu5LSepcXMWXhxCdQPeDm5Qce6wjJXURubJMpBm0mPWwCNZhJyRw1G5TTyO25NckXQRlObrjltvwAd+7OEUcsYXqhdPtUTIVy6w3XOwT2eC/hP0Yi7qqUMMlJTHUW7Lb9zsEc4UB5BVwgeZ5Y9bVbknJfpt3ygcXAJeeDYxwV9g16KoS7HMFPzwrqlHbiBytIahqarBd4enwqR5RYQPEyetiIDLaJA4SyQ0cE=
    ```
1. 上传到github

## 接收测试结果通知

如果你需要获取travis执行结果通知的话，可以添加邮箱配置，travis执行完毕后会通知到该邮箱。

1. 打开 **.travis.yml**
1. 添加以下内容：
```yaml
notifications:
  email:
    recipients:
        - 邮箱地址
    on_success: change
    on_failure: always
```
1. 提交到github
