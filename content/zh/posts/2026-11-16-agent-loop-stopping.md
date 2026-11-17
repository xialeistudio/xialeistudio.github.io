---
title: "Agent 循环里，真正难的是停下来"
date: 2026-11-16T10:00:00+08:00
slug: agent-loop-stopping
categories:
- ai
series:
- agent-engineering
tags:
- AI Agent
- Harness Engineering
- Agent Loop
- Go
featured: true
---

Agent 的主循环是整个系统里最短的代码：调用模型，执行工具，再调用模型，十几行就能写完。但上线之后出的问题，很大一部分都出在这十几行里，而且几乎都是同一类问题：它该停的时候没停，或者停了却没人知道为什么停。

本文是「Agent 工程笔记」系列的第一篇，以 Go 实现一个排查线上故障的 Agent 为例，把 Agent 循环的每一条退出路径拆开来讲。

<!--more-->

## 十几行的循环

几乎所有教程里的 Agent 循环都长这样：

```go
for {
    resp, err := model.Generate(ctx, msgs, tools)
    if err != nil {
        return "", err
    }
    msgs = append(msgs, resp.Message)
    if len(resp.Message.ToolCalls) == 0 {
        return resp.Message.Content, nil // 模型不再调工具，就算完成
    }
    for _, call := range resp.Message.ToolCalls {
        out, _ := tools[call.Name].Call(ctx, call.Args)
        msgs = append(msgs, toolResult(call.ID, out))
    }
}
```

演示时它运行良好。放到真实环境，会遇到这些情况：

- 日志查询返回空，模型换个措辞又查一次，还是空，再查一次……直到 token 耗尽。
- 日志服务挂了，工具返回 `connection refused`，模型每轮都重试同一个调用。
- 模型输出被 `max_tokens` 截断，工具参数只有半个 JSON，循环照样去执行。
- 用户点了"停止"，但循环要等当前工具跑完、模型再回一轮才发现。
- 循环最终退出了，调用方只拿到一段文本，分不清这是"排查完成"还是"预算耗尽时的半成品"。

这几个问题的共同点是：循环只有一个出口（模型不再调用工具），而现实中至少有八个。

## 先区分两种"停止"

第一步是把两个经常被混为一谈的概念分开：

- **FinishReason**：模型这一轮为什么停止生成。由模型 API 返回，取值通常是 `end_turn`、`tool_use`、`max_tokens`。
- **StopReason**：Agent 这次任务为什么结束。由 Harness 决定，是循环的输出。

前者是输入信号之一，后者才是调用方真正关心的。教程版循环的问题在于，它只用了 FinishReason 的一个取值，就直接决定了 StopReason。

在实现里，StopReason 应该是一个显式的枚举，而不是藏在 error 或返回的文本里：

```go
type StopReason string

const (
	StopCompleted    StopReason = "completed"     // 模型主动结束
	StopMaxTurns     StopReason = "max_turns"     // 轮数耗尽
	StopTokenBudget  StopReason = "token_budget"  // token 预算耗尽
	StopRepeatedCall StopReason = "repeated_call" // 连续重复同一调用
	StopToolFailures StopReason = "tool_failures" // 工具连续失败
	StopTruncated    StopReason = "truncated"     // 模型输出被截断
	StopCanceled     StopReason = "canceled"      // 外部取消或超时
	StopModelError   StopReason = "model_error"   // 模型调用本身失败
)
```

设计循环时，先把这张表写出来，再写 `for`。每一个枚举值都对应循环里一个明确的检查点。

## 退出路径逐一拆解

下面的代码基于一组最小的类型定义：`Model` 接口只有一个 `Generate` 方法，`Tool` 接口有 `Spec` 和 `Call`。具体对接哪家模型 SDK 不影响循环本身的设计，这里不展开。

### 模型说"完成了"

```go
case FinishEndTurn:
    return done(StopCompleted, turn, nil)
```

这是唯一的"正常"出口，但要注意它的含义：**模型认为自己完成了**，不代表任务真的完成了。模型可能查了一条日志就下结论，也可能直接回复"我无法访问日志系统"。

Harness 层面能做的是如实标注：StopCompleted 只表示"模型主动结束"。任务是否真的完成，要由调用方或者评估体系来判断，这是本系列第 5 篇的内容。

### 输出被截断

```go
case FinishMaxTokens:
    // 截断的输出里，工具参数可能只有半个 JSON，绝不能执行
    return done(StopTruncated, turn, nil)
```

截断很容易被忽略，因为它在大部分时候不出现。可一旦出现，后果往往很严重：参数 `{"svc":"ap` 能否解析取决于工具的实现，最坏的情况是被宽松的解析器补全成一个错误的调用。

这里的处理是直接终止。另一种做法是提高 `max_tokens` 让模型重新生成。不管选哪种，原则都是：**截断的工具调用不执行**。

### 预算耗尽

```go
if turn > a.Limits.MaxTurns {
    return done(StopMaxTurns, turn-1, nil)
}
if a.Limits.TokenBudget > 0 && usage.Total() >= a.Limits.TokenBudget {
    return done(StopTokenBudget, turn-1, nil)
}
```

这两项检查放在**调用模型之前**。放在之后的话，最后一次调用已经花了钱，结果却被丢掉。

轮数和 token 要同时限制。只限轮数，长上下文的任务可能在 10 轮内烧掉几十万 token；只限 token，廉价的短调用可以无限循环下去。

上限设多少，不应该靠拍脑袋。正确的做法是先放宽上限，统计正常任务实际用了多少轮、多少 token，再取一个比 P99 略高的值。这需要可观测性的支撑，第 4 篇会讲到。

### 模型原地打转

这是最常见、也最浪费的情况：模型拿到一个不满意的结果，用同样的参数再调一次，期望得到不同的答案。

```go
key := callsKey(resp.Message.ToolCalls)
if key == lastKey {
    repeats++
} else {
    lastKey, repeats = key, 1
}
if a.Limits.MaxRepeats > 0 && repeats > a.Limits.MaxRepeats {
    return done(StopRepeatedCall, turn, nil)
}
```

`callsKey` 把一轮里所有工具调用的名字和参数拼成一个字符串。有一个细节：参数要先做 `json.Compact`，否则 `{"svc":"api"}` 和 `{"svc": "api"}` 会被当成两个不同的调用。模型改的往往只是空格，语义完全一样。

```go
func callsKey(calls []ToolCall) string {
	var b bytes.Buffer
	for _, c := range calls {
		b.WriteString(c.Name)
		b.WriteByte('(')
		if err := json.Compact(&b, c.Args); err != nil {
			b.Write(c.Args)
		}
		b.WriteString(");")
	}
	return b.String()
}
```

这里检测的是**连续**重复，而不是历史上出现过。原因是有些调用本来就应该重复，比如部署后轮询服务状态：中间夹着别的调用，重复就是合理的。连续三次参数完全一样的调用，才基本可以确定是在打转。

这种检测只能拦住"完全相同"的重复。模型把查询词从 `timeout` 换成 `time out` 再换成 `timed out`，在语义上也是打转，但字符串不同。这种情况靠的是上一节的预算兜底，不必在循环里做语义判断。

### 工具失败

工具失败和前面几种情况不同：**单次失败不应该终止循环**。

```go
results, allFailed := a.execute(ctx, resp.Message.ToolCalls)
msgs = append(msgs, Message{Role: RoleTool, ToolResults: results})
if allFailed {
	failures++
} else {
	failures = 0
}
if a.Limits.MaxToolFailures > 0 && failures >= a.Limits.MaxToolFailures {
	return done(StopToolFailures, turn, nil)
}
```

错误信息要作为工具结果返回给模型（`IsError: true`），而不是在 Harness 里吞掉或直接 panic。模型看到"参数 `since` 格式错误，应为 RFC3339"之后，通常下一轮就能改对。这是 Agent 比传统程序更有韧性的地方，不该被循环的错误处理抵消。

只有**连续多轮全部失败**才终止，这通常意味着依赖本身不可用，继续重试只是浪费。

还有两个容易遗漏的失败来源：

```go
func (a *Agent) callTool(ctx context.Context, c ToolCall) (string, error) {
	t, ok := a.Tools[c.Name]
	if !ok {
		// 模型幻觉出不存在的工具：告诉它有哪些可用，而不是直接崩掉
		return "", fmt.Errorf("unknown tool %q, available: %v", c.Name, a.toolNames())
	}
	if a.Limits.ToolTimeout > 0 {
		var cancel context.CancelFunc
		ctx, cancel = context.WithTimeout(ctx, a.Limits.ToolTimeout)
		defer cancel()
	}
	out, err := t.Call(ctx, c.Args)
	if errors.Is(err, context.DeadlineExceeded) {
		return "", fmt.Errorf("tool %s timed out after %s", c.Name, a.Limits.ToolTimeout)
	}
	return out, err
}
```

- **模型调用了不存在的工具**：教程版代码在这里会 nil pointer panic。正确的做法是把可用工具列表作为错误返回。
- **工具卡住**：每次工具调用都要有独立的超时。一个查询卡死，不应该拖住整个 Agent。超时的错误信息要写清楚，模型才能判断是"换个参数"还是"换个工具"。

### 外部取消

```go
if err := ctx.Err(); err != nil {
	return done(StopCanceled, turn-1, err)
}
```

取消信号要从入口一路传下去：每轮开始检查一次，`Generate` 和 `Tool.Call` 都接收同一个 `ctx`。这样无论用户在模型生成中还是工具执行中点了停止，循环都能在当前操作返回后立即退出，不会再多跑一轮。

这里有一个本文不展开的问题：取消发生时，工具可能已经产生了副作用，比如重启了一个服务。"能停下来"和"停下来后状态是一致的"是两回事，后者取决于工具本身是否幂等，留到第 2 篇讨论工具设计时再说。

## 完整的循环

把上面的检查点组合起来：

```go
func (a *Agent) Run(ctx context.Context, history []Message) Result {
	msgs := append([]Message(nil), history...)
	specs := a.specs()

	var (
		usage    Usage
		lastKey  string
		repeats  int
		failures int
	)
	done := func(stop StopReason, turns int, err error) Result {
		return Result{Stop: stop, Final: lastText(msgs), Messages: msgs, Turns: turns, Usage: usage, Err: err}
	}

	for turn := 1; ; turn++ {
		// 1. 外部取消
		if err := ctx.Err(); err != nil {
			return done(StopCanceled, turn-1, err)
		}
		// 2. 预算检查，放在调用模型之前
		if turn > a.Limits.MaxTurns {
			return done(StopMaxTurns, turn-1, nil)
		}
		if a.Limits.TokenBudget > 0 && usage.Total() >= a.Limits.TokenBudget {
			return done(StopTokenBudget, turn-1, nil)
		}

		resp, err := a.Model.Generate(ctx, msgs, specs)
		if err != nil {
			if ctx.Err() != nil {
				return done(StopCanceled, turn-1, err)
			}
			return done(StopModelError, turn-1, err)
		}
		usage.InputTokens += resp.Usage.InputTokens
		usage.OutputTokens += resp.Usage.OutputTokens
		msgs = append(msgs, resp.Message)

		switch resp.Finish {
		case FinishMaxTokens:
			return done(StopTruncated, turn, nil)
		case FinishEndTurn:
			return done(StopCompleted, turn, nil)
		}

		// 3. 重复调用检测
		key := callsKey(resp.Message.ToolCalls)
		if key == lastKey {
			repeats++
		} else {
			lastKey, repeats = key, 1
		}
		if a.Limits.MaxRepeats > 0 && repeats > a.Limits.MaxRepeats {
			return done(StopRepeatedCall, turn, nil)
		}

		// 4. 执行工具，错误交给模型，只有连续失败才终止
		results, allFailed := a.execute(ctx, resp.Message.ToolCalls)
		msgs = append(msgs, Message{Role: RoleTool, ToolResults: results})
		if allFailed {
			failures++
		} else {
			failures = 0
		}
		if a.Limits.MaxToolFailures > 0 && failures >= a.Limits.MaxToolFailures {
			return done(StopToolFailures, turn, nil)
		}
	}
}
```

循环体里真正"做事"的只有两行：`Generate` 和 `execute`。其余都在回答同一个问题：现在该不该停。

## 停下来之后

循环结束时返回的不是一个字符串，而是一个结构：

```go
type Result struct {
	Stop     StopReason
	Final    string    // 最后一条 assistant 文本，可能为空
	Messages []Message // 完整历史，用于审计、恢复或续跑
	Turns    int
	Usage    Usage
	Err      error
}
```

调用方根据 `Stop` 决定下一步该做什么，不同的停止原因需要完全不同的处理：

| StopReason | 含义 | 调用方的典型处理 |
|---|---|---|
| completed | 模型主动结束 | 展示结论，交由评估判断质量 |
| max_turns / token_budget | 任务比预期复杂 | 展示已有进展，询问用户是否追加预算续跑 |
| repeated_call | 模型陷入循环 | 记录为失败样本，进入评估集 |
| tool_failures | 依赖不可用 | 告警，提示用户检查依赖服务 |
| truncated | 输出过长 | 调整 `max_tokens` 或拆分任务 |
| canceled | 用户主动停止 | 不报错，保留历史 |
| model_error | 模型服务异常 | 按普通的下游故障处理，重试或切换模型 |

这张表就是 Agent 和它的调用方之间的契约。没有它，调用方只能从文本里猜。

有两个值得补充的做法：

**收尾轮。** 预算耗尽时直接返回，`Final` 可能是第 6 轮的一句"让我再查一下数据库"，对用户毫无意义。更好的做法是在预算终止前，**禁用所有工具**再调一次模型，让它总结目前的发现和未完成的部分。这一轮要单独预留预算，不能算在主预算里，否则它会和主预算抢资源。

**从历史恢复。** `Messages` 是 Agent 的全部状态。每轮结束时把它持久化，进程崩溃后就能从最后一轮继续，对用户来说就是"追加预算续跑"。唯一需要小心的是最后一轮：如果崩溃发生在工具执行之后、结果写入之前，恢复时这个工具会被再执行一次。这又回到了幂等的问题。

## 测试每一条退出路径

退出路径在线上很难复现：你没法让真实模型"恰好"连续重复三次同一个调用。所以 Model 被设计成接口，测试时用一个按脚本返回的假模型：

```go
type scriptedModel struct {
	script []Response
	i      int
}

func (m *scriptedModel) Generate(ctx context.Context, _ []Message, _ []ToolSpec) (Response, error) {
	if err := ctx.Err(); err != nil {
		return Response{}, err
	}
	r := m.script[min(m.i, len(m.script)-1)] // 脚本用完后一直重复最后一步
	m.i++
	return r, nil
}
```

每条退出路径一个测试。比如重复调用的检测，要确认只差一个空格的参数也会被识别：

```go
func TestRepeatedCall(t *testing.T) {
	a := newAgent(&scriptedModel{script: []Response{
		toolUse("query_logs", `{"svc":"api"}`),
		toolUse("query_logs", `{"svc": "api"}`),
	}}, okTool)
	r := a.Run(context.Background(), nil)
	if r.Stop != StopRepeatedCall || r.Turns != 4 {
		t.Fatalf("got %s after %d turns", r.Stop, r.Turns)
	}
}
```

截断时工具绝不能被执行：

```go
func TestTruncated(t *testing.T) {
	cut := toolUse("query_logs", `{"svc":"ap`)
	cut.Finish = FinishMaxTokens
	called := false
	spy := funcTool{"query_logs", func(context.Context, json.RawMessage) (string, error) {
		called = true
		return "", nil
	}}
	r := newAgent(&scriptedModel{script: []Response{cut}}, spy).Run(context.Background(), nil)
	if r.Stop != StopTruncated || called {
		t.Fatalf("got %s, called=%v", r.Stop, called)
	}
}
```

工具执行期间被取消，循环不能再多跑一轮：

```go
func TestCanceledDuringTool(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	tool := funcTool{"query_logs", func(context.Context, json.RawMessage) (string, error) {
		cancel() // 模拟用户在工具执行期间点了停止
		return "partial", nil
	}}
	r := newAgent(&scriptedModel{script: []Response{toolUse("query_logs", `{}`), answer("x")}}, tool).Run(ctx, nil)
	if r.Stop != StopCanceled || r.Turns != 1 {
		t.Fatalf("got %s after %d turns", r.Stop, r.Turns)
	}
}
```

完整实现中的 8 个测试分别对应正常完成、重复调用、轮数耗尽、token 耗尽、工具连续失败、工具超时、输出截断、执行中取消。这类测试不调用真实模型，毫秒级就能跑完，可以放进每次提交的 CI。

## 小结

Agent 循环的代码量，主要不在"做事"，而在"决定何时不再做事"。

教程版循环只有一个出口，它默认模型总会在合适的时候主动停下。生产环境的循环至少要有八个出口，每个出口都对应一种具体的失败方式，并且要把停止原因显式交给调用方。

设计 Agent 循环时，建议的顺序是：

1. 先列出 StopReason 枚举，每一项写清楚触发条件和调用方的处理方式；
2. 再写循环，确保每个枚举值在循环里都有对应的检查点；
3. 最后用脚本化的模型，为每一条退出路径写一个测试。

本文的循环有意保持简单：工具串行执行、没有收尾轮、没有持久化。这些都会在后续文章中逐步补上。下一篇讨论工具层：既然工具的错误信息要交给模型去读，那么工具接口应该怎样为模型而不是为人来设计。
