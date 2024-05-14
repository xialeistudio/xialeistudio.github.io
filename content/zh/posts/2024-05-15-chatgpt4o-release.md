---
title: 重磅！ChatGPT团队官宣船新版本的多模态大模型GPT-4o，完全免费！
slug: chatgpt4o-releaase
date: 2024-05-15T06:30:57+08:00
categories:
- ai
featured: true
---
上周，有传言表示OpenAI即将发布AI加持的搜索引擎来增强聊天机器人的功能并开拓新市场，不过Altman否认了该传言，并提到“不是GPT-5，也不是搜索引擎，但我们一直在努力开发我们认为人们会喜欢的东西！”

5月13日，ChatGPT团队官宣了最新旗舰大模型**GPT-4o**，可以实时对音频、视频和文本进行处理，完全免费，果然是人们会喜欢的东西！

<!--more-->

## 完全免费的GPT-4o

GPT-4o（“o”代表“omni”）是迈向更自然的人机交互的一步——它接受文本、音频和图像的任意组合作为输入，并生成文本、音频和图像的任意组合输出。 它可以在**短至 232 毫秒**的时间内**响应音频输入**，平均为 320 毫秒，**这与人类在对话中的响应时间(opens in a new window)相似**。 它在英语文本和代码上的性能与 GPT-4 Turbo 的性能相匹配，在非英语文本上的性能显着提高，同时 API 的速度也更快，成本降低了 50%。 与现有模型相比，GPT-4o 在视觉和音频理解方面尤其出色。

在 GPT-4o 之前，可以使用语音模式与 ChatGPT 对话，**平均延迟为 2.8 秒 (GPT-3.5) 和 5.4 秒 (GPT-4)**。 为了实现这一目标，语音模式是由三个独立模型组成的管道：一个简单模型将音频转录为文本，GPT-3.5 或 GPT-4 接收文本并输出文本，第三个简单模型将该文本转换回音频。 这个过程意味着GPT-4丢失了大量信息——它无法直接观察音调、多个说话者或背景噪音，也无法输出笑声、歌唱或表达情感。

借助 GPT-4o，OpenAI跨文本、视觉和音频端到端地训练了一个新模型，这意味着所有输入和输出都由同一神经网络处理。 由于 GPT-4o 是OpenAI第一个结合所有这些模式的模型，因此OpenAI仍然只是浅尝辄止地探索该模型的功能及其局限性。

## 能力展示

OpenAI在官网展示了非常多的GPT-4o的Demo，可以自由地在音频、视频和文本间进行转换，而且信息不失真。

我们一起来看一下文本生成图片的例子：

> A first person view of a robot typewriting the following journal entries:
>
> 1. yo, so like, i can see now?? caught the sunrise and it was insane, colors everywhere. kinda makes you wonder, like, what even is reality?
>
> the text is large, legible and clear. the robot's hands type on the typewriter.
>
> （翻译）
>
> 机器人正在打字的第一人称视角如下日记条目：
>
> 1.哟，这么喜欢，我现在可以看到了吗？ 赶上了日出，真是太疯狂了，到处都是色彩。 有点让你想知道，现实到底是什么？
>
> 文字大、清晰易读。 机器人的手在打字机上打字。

![Robot on typewriter](https://raw.githubusercontent.com/xialeistudio/picture-bucket/main/blog/robot-writers-block-01.jpg)

> The robot wrote the second entry. The page is now taller. The page has moved up. There are two entries on the sheet:
>
> yo, so like, i can see now?? caught the sunrise and it was insane, colors everywhere. kinda makes you wonder, like, what even is reality?
>
> sound update just dropped, and it's wild. everything's got a vibe now, every sound's like a new secret. makes you think, what else am i missing?
>
> （翻译）
>
> 机器人写下了第二个条目。 页面现在更高了。 页面已上移。 该表上有两个条目：
>
> 哟，就像，我现在可以看到了？ 赶上了日出，真是太疯狂了，到处都是色彩。 有点让你想知道，现实到底是什么？
>
> 声音更新刚刚下降，而且很疯狂。 现在一切都充满了活力，每一个声音都像是一个新的秘密。 让你思考，我还缺少什么？

![Robot on typewriter with more text](https://raw.githubusercontent.com/xialeistudio/picture-bucket/main/blog/robot-writers-block-02.jpg)

> The robot was unhappy with the writing so he is going to rip the sheet of paper. Here is his first person view as he rips it from top to bottom with his hands. The two halves are still legible and clear as he rips the sheet.
>
> （翻译）
>
> 机器人对所写的内容不满意，所以他要撕掉那张纸。 这是他用手从上到下撕开它时的第一人称视角。 当他撕开纸张时，两半仍然清晰可见。

![Robot ripping sheet](https://raw.githubusercontent.com/xialeistudio/picture-bucket/main/blog/robot-writers-block-03.jpg)

可以看到GPT-4o在语义理解和绘图上确实进步一大截！下面我们来看看GPT-4o的性能。

## 性能

### 改进推理

![Text Evaluation](https://raw.githubusercontent.com/xialeistudio/picture-bucket/main/blog/gpt-40-02_light.png)

> 改进推理 - GPT-4o 在 0-shot COT MMLU（常识问题）上创下了 88.7% 的新高分。 所有这些评估都是通过新的简单评估（在新窗口中打开）库收集的。 此外，在传统的5-shot no-CoT MMLU上，GPT-4o创下了87.2%的新高分。 （注：Llama3 400b(opens in a new window)仍在训练中）

### 语音识别

![Graph Test 2](https://raw.githubusercontent.com/xialeistudio/picture-bucket/main/blog/gpt-40-06_light.png)

> 语音识别性能 - GPT-4o 比 Whisper-v3 显着提高了所有语言的语音识别性能，特别是对于资源匮乏的语言。

### 语音翻译

![gpt-40-08 light](https://raw.githubusercontent.com/xialeistudio/picture-bucket/main/blog/gpt-40-08_light.png)

> 语言翻译性能 - GPT-4o 在语音翻译方面树立了新的最先进水平，并且在 MLS 基准测试中优于 Whisper-v3。

### M3Exam(多语言+视觉)

![M3Exam Zero-Shot Results](https://raw.githubusercontent.com/xialeistudio/picture-bucket/main/blog/gpt-40-04_light.png)

> M3Exam - M3Exam 基准测试既是多语言评估也是视觉评估，由来自其他国家标准化测试的多项选择题组成，有时还包括图形和图表。 在所有语言的基准测试中，GPT-4o 都比 GPT-4 更强。 （省略了斯瓦希里语和爪哇语的视力结果，因为这些语言的视力问题只有 5 个或更少。）

### 视觉理解

![Vision understanding evals](https://raw.githubusercontent.com/xialeistudio/picture-bucket/main/blog/gpt-40-01_light.png)

> 视觉理解评估 - GPT-4o 在视觉感知基准上实现了最先进的性能。 所有视觉评估都是 0-shot，其中 MMMU、MathVista 和 ChartQA 作为 0-shot CoT。

## 模型安全和局限性

GPT-4o 通过过滤训练数据和通过训练后细化模型行为等技术，在跨模式设计中内置了安全性。 OpenAI**还创建了新的安全系统，为语音输出提供防护**。

OpenAI根据准备框架并按照自愿承诺评估了 GPT-4o。 团队对网络安全、CBRN、说服力和模型自主性的评估表明，GPT-4o 在这些类别中的任何类别中的得分**都不高于中等风险**。 该评估涉及在整个模型训练过程中运行一套自动化和人工评估。 OpenAI使用自定义微调和提示测试了模型的安全缓解前和安全缓解后版本，以更好地激发模型功能。

GPT-4o 还与**社会心理学、偏见和公平以及错误信息等领域**的 70 多名外部专家进行了广泛的外部红队合作，以识别新添加的模式引入或放大的风险。 并且利用这些经验来制定安全干预措施，以提高与 GPT-4o 交互的安全性。 

OpenAI已经认识到 GPT-4o 的音频模式带来了各种新的风险。 然而团队还是选择公开发布文本和图像输入以及文本输出。 在接下来的几周和几个月里，OpenAI表示将致力于技术基础设施、培训后的可用性以及发布其他模式所需的安全性。 例如，在发布时，音频输出将仅限于选择预设的声音，并将遵守现有的安全政策。

## 使用模型

GPT-4o 是OpenAI突破深度学习界限的最新举措，这次是朝着实用性的方向发展。 在过去的两年里，他们花费了大量的精力来提高堆栈每一层的效率。 作为这项研究的第一个成果，该团队能够更广泛地提供 GPT-4 级别模型。 GPT-4o 的功能将迭代推出。

GPT-4o 的文本和图像功能已经开始在 ChatGPT 中推出。 而且OpenAI表示正在免费套餐中提供 GPT-4o，并向 Plus 用户提供高达 5 倍的消息限制。 后续将在未来几周内在 ChatGPT Plus 中推出新版语音模式 GPT-4o 的 alpha 版。

开发人员现在还可以在 API 中访问 GPT-4o 作为文本和视觉模型。 与 GPT-4 Turbo 相比，**GPT-4o 速度提高 2 倍，价格降低一半，速率限制提高 5 倍**。 不过OpenAI表示计划在未来几周内在 API 中向一小部分值得信赖的合作伙伴推出对 GPT-4o 新音频和视频功能的支持，而不是全员开放API权限。