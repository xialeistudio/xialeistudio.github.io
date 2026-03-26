---
title: "解决 OpenCode 通过第三方代理使用 GPT 时无法命中 Prompt Cache 的问题"
date: 2026-03-26T21:30:00+08:00
slug: fix-opencode-prompt-caching-with-third-party-proxy
categories:
- AI
tags:
- OpenCode
- GPT
- Prompt Caching
---

最近在使用 OpenCode + GPT 5.3 Codex 进行日常开发时，发现 token 消耗异常高，每次请求的 input tokens 高达 69K，而 cached tokens 几乎为零。同样的模型和代理，用 Codex CLI 却能正常命中 cache。本文记录了排查和解决这个问题的完整过程。

<!--more-->

## 问题现象

通过中转 API 后台观察到的请求日志如下：

| Input Tokens | Output Tokens | Cached Tokens | 费用 |
|---|---|---|---|
| 69,449 | 273 | 0 | $0.125 |
| 69,303 | 117 | 0 | $0.123 |
| 55,480 | 70 | 13,100 | $0.100 |
| 68,106 | 217 | 0 | $0.122 |

几个关键特征：

1. **Input tokens 极高**：每次请求约 69K tokens，这是 OpenCode 的 system prompt + 工具定义 + 对话上下文的总量。
2. **几乎没有 cache 命中**：只有 1 条请求偶尔命中了 13.1K cached tokens，其余全部 miss。
3. **单次费用高**：由于没有 cache，每次请求按全量 input 计费，单次约 $0.12。

对比之下，同一个第三方代理，使用 Codex CLI 直连时 cache 工作正常。这说明代理本身支持 OpenAI 的 prompt caching 机制，问题出在 OpenCode 这一层。

## 原因分析

OpenAI 的 prompt caching 是服务端自动行为——当请求的 prompt prefix 超过 1024 tokens 且与之前的请求前缀一致时，会自动缓存并复用。缓存的关键在于**请求需要被路由到相同的后端节点**。

OpenCode 使用 Vercel AI SDK (`@ai-sdk/openai`) 作为底层 provider。AI SDK 支持一个 `promptCacheKey` 参数，用于告知 OpenAI 将具有相同 cache key 的请求路由到同一后端，从而提高 cache 命中率。

但 OpenCode 默认不会设置这个参数。当请求通过第三方代理转发时，由于缺少 cache key，代理无法保证将请求路由到相同的后端节点，导致每次请求都打到不同的节点上，cache 自然无法命中。

这个问题在 OpenCode 的 GitHub 仓库中也有记录：[anomalyco/opencode#17610 - Cache Not Utilized When Using Third-Party Relay with Codex Model](https://github.com/anomalyco/opencode/issues/17610)。

## 解决方案

在 OpenCode 配置文件中为对应的 provider 添加 `"setCacheKey": true` 选项。

配置文件路径：`~/.config/opencode/opencode.json`

```json
{
  "provider": {
    "codex": {
      "npm": "@ai-sdk/openai",
      "options": {
        "apiKey": "your-api-key",
        "baseURL": "https://your-proxy.com/v1",
        "setCacheKey": true
      }
    }
  }
}
```

关键改动就是在 `options` 中加入 `"setCacheKey": true`。这会让 OpenCode 在每次请求中携带 `promptCacheKey`，确保具有相同上下文的请求被路由到同一后端节点。

## 效果验证

修改配置并重启 OpenCode 后，再次观察中转 API 后台的日志：

| Input Tokens | Output Tokens | Cached Tokens | 费用 |
|---|---|---|---|
| 16,384 | 162 | 21,000 | $0.035 |
| 6,325 | 79 | 37,400 | $0.019 |
| 8,086 | 250 | 43,600 | $0.025 |
| 303 | 486 | 51,800 | $0.016 |

效果非常明显：

- **Cached tokens 持续上升**：从 21K 逐步增长到 51.8K，说明 cache 正常工作且不断积累。
- **Input tokens 大幅下降**：从之前的 69K 降至数百到数千，因为大部分 prompt 已从 cache 读取。
- **费用降低约 87%**：单次请求从 $0.12 降至 $0.016。

## 总结

如果你在使用 OpenCode 通过第三方代理调用 GPT 系列模型，发现 token 消耗异常高且没有 cache 命中，大概率是缺少 `setCacheKey` 配置。一行配置改动即可解决问题，效果立竿见影。

需要注意的几个前提条件：
- OpenCode 版本 >= 1.3.0（该版本修复了相关问题）
- 第三方代理本身需要支持 OpenAI 的 prompt caching 机制
- 使用 `@ai-sdk/openai` 作为 npm provider
