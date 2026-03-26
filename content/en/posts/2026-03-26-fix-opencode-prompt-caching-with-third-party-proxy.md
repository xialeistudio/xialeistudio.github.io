---
title: "Fixing OpenCode Prompt Cache Misses When Using GPT via Third-Party Proxy"
date: 2026-03-26T21:30:00+08:00
slug: fix-opencode-prompt-caching-with-third-party-proxy
categories:
- AI
tags:
- OpenCode
- GPT
- Prompt Caching
---

While using OpenCode with GPT 5.3 Codex for daily development, I noticed abnormally high token consumption — around 69K input tokens per request with virtually zero cache hits. The same model and proxy worked fine with Codex CLI, where caching functioned as expected. This post documents the full debugging and resolution process.

<!--more-->

## The Problem

Request logs from the API proxy dashboard showed:

| Input Tokens | Output Tokens | Cached Tokens | Cost |
|---|---|---|---|
| 69,449 | 273 | 0 | $0.125 |
| 69,303 | 117 | 0 | $0.123 |
| 55,480 | 70 | 13,100 | $0.100 |
| 68,106 | 217 | 0 | $0.122 |

Key observations:

1. **Extremely high input tokens**: ~69K per request, consisting of OpenCode's system prompt, tool definitions, and conversation context.
2. **Nearly zero cache hits**: Only 1 out of 4 requests had any cached tokens (13.1K), the rest were complete misses.
3. **High per-request cost**: Without caching, each request was billed at full input rate — roughly $0.12 per call.

Meanwhile, Codex CLI hitting the same proxy had normal cache behavior. This confirmed that the proxy itself supports OpenAI's prompt caching — the issue was in the OpenCode layer.

## Root Cause

OpenAI's prompt caching works automatically on the server side. When a request's prompt prefix exceeds 1024 tokens and matches a previous request's prefix, the server reuses the cached version. The key requirement is that **requests must be routed to the same backend node** for cache hits to occur.

OpenCode uses the Vercel AI SDK (`@ai-sdk/openai`) as its underlying provider. The AI SDK supports a `promptCacheKey` parameter that instructs OpenAI to route requests with the same cache key to the same backend, improving cache hit rates.

However, OpenCode does not set this parameter by default. When requests go through a third-party proxy without a cache key, the proxy cannot guarantee routing to the same backend node. Each request may land on a different node, making cache hits impossible.

This issue was tracked in OpenCode's GitHub repository: [anomalyco/opencode#17610 - Cache Not Utilized When Using Third-Party Relay with Codex Model](https://github.com/anomalyco/opencode/issues/17610).

## The Fix

Add `"setCacheKey": true` to the provider options in OpenCode's configuration file.

Config file location: `~/.config/opencode/opencode.json`

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

The only change is adding `"setCacheKey": true` to `options`. This makes OpenCode include a `promptCacheKey` in every request, ensuring requests with the same context are routed to the same backend node.

## Results

After updating the config and restarting OpenCode, the proxy dashboard showed:

| Input Tokens | Output Tokens | Cached Tokens | Cost |
|---|---|---|---|
| 16,384 | 162 | 21,000 | $0.035 |
| 6,325 | 79 | 37,400 | $0.019 |
| 8,086 | 250 | 43,600 | $0.025 |
| 303 | 486 | 51,800 | $0.016 |

The improvement was dramatic:

- **Cached tokens climbed steadily**: From 21K to 51.8K, showing the cache warming up and working correctly.
- **Input tokens dropped significantly**: From 69K down to a few hundred or thousand, as most of the prompt was served from cache.
- **Cost reduced by ~87%**: Per-request cost went from $0.12 to $0.016.

## Summary

If you're using OpenCode with GPT models through a third-party proxy and seeing high token usage with no cache hits, the fix is almost certainly adding `setCacheKey` to your provider config. A one-line change that delivers immediate results.

Prerequisites:
- OpenCode version >= 1.3.0 (which includes the relevant fix)
- Your third-party proxy must support OpenAI's prompt caching mechanism
- Using `@ai-sdk/openai` as the npm provider
