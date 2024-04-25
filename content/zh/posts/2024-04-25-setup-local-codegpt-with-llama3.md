---
title: 拥有你自己的Copilot!基于Llama3和CodeGPT部署本地Copilot，断网也能使用！
slug: setup-local-codegpt-with-llama3
date: 2024-04-25T08:30:57+08:00
tags: 
- llama3
categories:
- ai
featured: true
---

当谈到代码自动补全和辅助编程工具时，GitHub Copilot是一个备受推崇的选择。然而，有时我们可能希望在本地环境中构建一个类似的解决方案，以便更好地控制数据和隐私，更重要的是Llama3是免费，而Github Copilot是收费的。本文将分享如何基于Llama3和CodeGPT这两个强大的开源项目，搭建自己的本地Copilot。

<!--more-->

## 部署Llama3模型

在[超越GPT-3.5!Llama3个人电脑本地部署教程](https://www.ddhigh.com/2024/04/20/%E8%B6%85%E8%B6%8Agpt-3.5llama3%E4%B8%AA%E4%BA%BA%E7%94%B5%E8%84%91%E6%9C%AC%E5%9C%B0%E9%83%A8%E7%BD%B2%E6%95%99%E7%A8%8B/)中我已经分享过如何使用Ollama在本地部署Llama3模型，本文不再赘述。

## 安装CodeGPT扩展

打开Visual Studio Code，转到扩展标签页。搜索“CodeGPT”并安装这个扩展。CodeGPT是一个可以使用多种大语言模型辅助代码编程的插件。

> 注意：要认证发布者是`CodeGPT`，不要安装CSDN发布的！

![image-20240425204658304](https://raw.githubusercontent.com/xialeistudio/picture-bucket/main/blog/image-20240425204658304.png)

## 设置Llama3为CodeGPT默认模型

安装完CodeGPT之后，VSCode左侧会出现CodeGPT的产品图标，按照下图设置Llama3为CodeGPT使用的模型。

![image-20240425205154839](https://raw.githubusercontent.com/xialeistudio/picture-bucket/main/blog/image-20240425205154839.png)

## 测试

下面是笔者的测试截图，可以看到模型工作正常，提供了一个Echo Server例子：

![image-20240425210425337](https://raw.githubusercontent.com/xialeistudio/picture-bucket/main/blog/image-20240425210425337.png)

在日常开发中，我们可以在任意源码处点击右键让CodeGPT对代码进行解释或者优化。

![image-20240425210538668](https://raw.githubusercontent.com/xialeistudio/picture-bucket/main/blog/image-20240425210538668.png)

与收费的GitHub Copilot不同，Llama3提供了免费的解决方案，并且我们可以更好地控制数据和隐私。通过安装Llama3模型和CodeGPT扩展，我们能够在本地环境中享受到强大的代码辅助功能。无论是解释代码还是进行优化，CodeGPT都能为我们提供准确而实用的建议。

希望本文对你构建自己的本地Copilot有所帮助，让你在编程过程中更高效、更愉快！

> 在搭建本地Copilot的过程中有任何疑问都可以关注公众号加群进行交流。