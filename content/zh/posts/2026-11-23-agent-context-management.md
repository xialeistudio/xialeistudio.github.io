---
title: "Agent 的上下文是历史的视图，不是历史本身"
date: 2026-11-23T08:00:00+08:00
slug: agent-context-management
categories:
- ai
series:
- agent-engineering
tags:
- AI Agent
- Harness Engineering
- Context Engineering
- Go
featured: true
---

前两篇的 Agent 每一轮都把完整的消息历史发给模型。一次排查调用十几次工具，结果在历史里越积越多，最早的那些对当前判断已经没有用，却每一轮都要重新发一遍。

常见的做法是"历史太长就截掉前面的"，或者"太长就让模型总结一下"。两种做法都把历史和发给模型的上下文当成了同一个东西，所以压缩时总要在"省 token"和"丢信息"之间二选一。本文是「Agent 工程笔记」系列的第三篇，继续以 Go 实现的线上故障排查 Agent 为例，先把这两样东西分开，再讨论什么时候压缩、怎么压缩、哪些信息不能交给摘要，最后补上第一篇欠下的收尾轮。

<!--more-->

## 历史越长，问题越多

先算一笔账。假设系统提示和工具定义共 3000 token，每轮模型输出加工具结果约 1700 token（第二篇已经把单个工具结果压到了几百到一两千 token）。第 n 轮的输入大约是：

```
3000 + 1700 × (n − 1)
```

15 轮的排查，最后一轮输入约 2.7 万 token，15 轮累计约 22 万 token。真正有信息量的内容只有两万多，其余都是同样的内容被重复发送。**总消耗随轮数平方增长**，第一篇设的 token 预算，大部分花在了重复发送旧内容上。

钱只是一个方面，还有另外两个问题：

- **上下文窗口是硬上限。** 超过之后模型 API 直接报错，循环以 `model_error` 结束，前面所有的工作都白做了。
- **旧信息会误导模型。** 排查开始时 `inspect_service` 显示 api 有 3 个 pod 在 CrashLoop，后来重启了，现在一切正常。但那条旧结果还在上下文里，模型在第 12 轮可能仍然引用它。

所以上下文管理要解决的问题是：在不丢掉关键信息的前提下，让每一轮发给模型的内容保持在一个稳定的大小。

## 先分开历史和上下文

前两篇的循环里只有一个 `msgs`，它同时承担了两个职责：

- **历史（transcript）**：发生过的全部事情。用于审计、持久化、续跑，以及第 5 篇要讲的评估。它必须完整，而且只能追加。
- **上下文（context）**：这一轮发给模型的内容。它应该尽可能小，只包含对接下来的决策有用的信息。

把两者混在一起，压缩就意味着修改历史：截掉的内容永远找不回来，审计时也看不到模型当时到底看到了什么。分开之后，**历史保持不变，上下文是每一轮从历史派生出来的一个视图**。

一次压缩过的排查，历史和视图的对应关系是这样的：

| 历史中的部分 | 发给模型的形式 |
|---|---|
| 任务（用户的原始请求） | 原样保留 |
| 较早的轮次（比如第 1–5 轮） | 一段摘要 + 写操作记录 |
| 中间的轮次（第 6–8 轮） | 保留工具调用，清除工具结果 |
| 最近的轮次（第 9–10 轮） | 原样保留 |

越旧的内容压缩得越狠，只有任务本身例外。本文后面的几节，就是在解释这张表的每一行。

代码里，视图由几个下标和两段文本描述：

```go
// contextState 描述"发给模型的上下文"如何从完整历史中派生出来。
// 完整历史只追加、不修改；压缩只改变这个视图。
type contextState struct {
	head      int    // transcript[:head] 是任务本身，永远原样保留
	from      int    // transcript[head:from] 已被摘要取代
	clearedTo int    // transcript[from:clearedTo] 中的工具结果已被清除
	summary   string // 模型写的进展摘要
	ledger    string // Harness 记录的写操作，不经过模型
}

func (s *contextState) view(transcript []Message) []Message {
	v := append([]Message(nil), transcript[:s.head]...)
	if s.summary != "" || s.ledger != "" {
		v = append(v, Message{Role: RoleUser, Content: s.handoff()})
	}
	for i := s.from; i < len(transcript); i++ {
		m := transcript[i]
		if i < s.clearedTo && m.Role == RoleTool {
			m = clearResults(m)
		}
		v = append(v, m)
	}
	return v
}
```

三个下标正好对应表格的前三行，`from` 之后、`clearedTo` 之后的部分原样输出，就是最后一行。

循环里，追加消息时写入 `msgs`，调用模型时传入 `st.view(msgs)`。`Result.Messages` 仍然返回完整历史，第一篇说的"用于审计、恢复或续跑"不受影响。

## 什么时候压缩

### 用 API 返回的数字

判断上下文有多大，最准确的数据来自模型 API 本身：每次调用返回的 `InputTokens` 就是这一轮上下文的真实大小。加上本轮的输出和新的工具结果，就是下一轮的大小：

```go
usage.Add(resp.Usage)
msgs = append(msgs, resp.Message)
// API 返回的输入 token 是这一轮上下文的真实大小，加上本轮输出就是下一轮的起点
ctxTokens = resp.Usage.InputTokens + resp.Usage.OutputTokens
// ... 执行工具
ctxTokens += estimate([]Message{toolMsg})
```

新的工具结果还没有真实数字，`estimate` 按字节数粗略估算。它只用来决定"要不要压缩"，宁可高估：提前压缩比撞上窗口上限好。

### 检查放在调用模型之前

和第一篇的预算检查一样，上下文检查也放在 `Generate` 之前：

```go
// 上下文检查，同样放在调用模型之前
if a.Context.CompactAt > 0 && ctxTokens > a.Context.CompactAt {
	u, err := a.compact(ctx, msgs, &st)
	usage.Add(u)
	if err != nil {
		return finish(stopFor(ctx, err), turn-1, err) // 超窗口、取消或模型错误
	}
}
resp, err := a.Model.Generate(ctx, st.view(msgs), specs)
```

压缩本身可能调用模型，花掉的 token 同样计入 `usage`，受总预算约束。

### 两条水位线，而不是滑动窗口

最直观的方案是滑动窗口：每轮只保留最近 N 轮。它的问题在于每一轮的上下文开头都不一样。

模型 API 的提示缓存（prompt caching）按前缀匹配：这一轮的上下文如果和上一轮有相同的前缀，这部分可以命中缓存，费用和延迟都大幅降低。滑动窗口每轮都把开头的消息挪走，前缀每轮都变，缓存永远不命中。

所以压缩用两条水位线：

```go
type ContextPolicy struct {
	Window     int // 模型的上下文上限（token），压缩后仍超过就只能停下
	CompactAt  int // 上下文超过这个值时开始压缩
	CompactTo  int // 压缩的目标：清除工具结果后仍高于此值，就做摘要
	KeepTurns  int // 最近几轮保持原样，不清除也不摘要
	MaxResult  int // 单个工具结果的字节上限，超出截断
	Summarizer Model
}
```

上下文涨到 `CompactAt` 时压缩一次，一直压到 `CompactTo` 以下，然后不再动它，直到它再涨到 `CompactAt`。两次压缩之间，上下文只在末尾追加，前缀不变，缓存可以一直命中。

比如窗口 200k，`CompactAt` 设为 100k，`CompactTo` 设为 40k，每次压缩之后可以跑好几十轮才需要下一次。具体数值和缓存的收益在第 9 篇讨论成本时再展开，这里只需要记住：**压缩要成批做，不要每轮做**。

## 第一级：清除旧的工具结果

压缩分两级，先做便宜的。

上下文里体积最大的是工具结果，而且旧的工具结果大多已经没有用了：模型看过它，在后面的回复里写下了结论（"错误从 14:02 开始，主要是 db-2 超时"），并据此决定了下一步。几轮之后，原始结果的价值已经转移到了模型自己的文字里。

第一级压缩就是把这些旧结果替换成一行占位：

```go
func clearResults(m Message) Message {
	rs := make([]ToolResult, len(m.ToolResults))
	for i, r := range m.ToolResults {
		r.Content = fmt.Sprintf("[结果已清除以节省上下文，原文 %d 字节。如仍需要，请重新调用]", len(r.Content))
		rs[i] = r
	}
	m.ToolResults = rs
	return m
}
```

注意三点：

- **只清除结果，保留调用。** assistant 消息里的 `search_logs({"service":"api"})` 原样保留，模型仍然知道自己查过什么，只是看不到结果了。
- **占位符告诉模型可以重新调用。** 这和第二篇"截断必须明说"是同一条规则：模型需要知道这里本来有东西，而不是以为那次调用什么也没返回。
- **它不调用模型。** 纯粹的字符串替换，几乎没有成本，结果也完全确定。

清除的范围是最近 `KeepTurns` 轮之前的所有工具结果。切点的选择有一个约束：模型 API 要求每个工具结果前面都有对应的工具调用。如果切点落在 assistant 消息和它的工具结果之间，后面做摘要时就会留下一个找不到调用的结果，API 会直接拒绝。所以切点总是选在 assistant 消息上：

```go
// boundary 返回倒数第 keep 条 assistant 消息的下标：从这里开始的消息保持原样。
// 切点总在 assistant 消息上，所以工具调用和它的结果不会被拆开。
func boundary(transcript []Message, from, keep int) int {
	seen := 0
	for i := len(transcript) - 1; i >= from; i-- {
		if transcript[i].Role == RoleAssistant {
			seen++
			if seen == keep {
				return i
			}
		}
	}
	return from
}
```

在多数排查任务里，只做这一级就能把上下文压回 `CompactTo` 以下。

## 第二级：摘要

如果清除工具结果之后仍然超过 `CompactTo`，说明占地方的已经不是工具结果，而是轮数本身：几十轮的调用记录和模型的分析文字。这时才需要第二级：把较早的若干轮交给模型写成摘要，替换掉原文。

```go
// compact 把上下文压到 CompactTo 以下：先清除旧的工具结果，不够再做摘要。
func (a *Agent) compact(ctx context.Context, transcript []Message, st *contextState) (Usage, error) {
	p := a.Context
	b := boundary(transcript, st.from, p.KeepTurns)

	// 第一级：清除旧的工具结果。不调用模型，几乎没有成本。
	st.clearedTo = max(st.clearedTo, b)
	tokens := estimate(st.view(transcript))
	if tokens <= p.CompactTo {
		return Usage{}, nil
	}

	// 第二级：把 [from, b) 摘要掉。
	if b <= st.from { // 除了最近几轮已经没有可摘要的内容
		if tokens > p.Window {
			return Usage{}, errContextOverflow
		}
		return Usage{}, nil
	}
	summary, u, err := a.summarizeHistory(ctx, st.summary, transcript[st.from:b])
	if err != nil {
		return u, err
	}
	st.summary, st.from = summary, b
	st.ledger = a.ledger(transcript[st.head:b])
	if estimate(st.view(transcript)) > p.Window {
		return u, errContextOverflow
	}
	return u, nil
}
```

### 摘要写给谁看

摘要和普通的"总结一下"不同：它的读者是之后的模型自己，而且读者**再也看不到原文**。"排查了日志，发现数据库有问题"这样的摘要，对人来说是个不错的概括，对之后的模型几乎没用：它不知道是哪台数据库、什么错误、从几点开始，只能重新查一遍。

所以摘要的提示词要先告诉模型它的处境，再规定摘要的结构：

```go
const handoffSections = `1. 已确认的事实：附上原始证据（时间、主机名、数值、错误原文），不要概括成"数据库有问题"
2. 已排除的方向：排除的依据是什么
3. 已执行的写操作：做了什么、结果如何
4. 尚未解决的问题和下一步计划
没有查到的内容不要写，不确定的要标明不确定。`

prompt := "下面是一个排查任务的较早部分。你之后只能看到你写的摘要，看不到原文。" +
	"请按以下结构写摘要：\n" + handoffSections + "\n\n" + history
```

"你之后只能看到你写的摘要"这句话，比"请详细总结"有效得多。

四项里最容易被省略的是第 2 项。摘要通常只记录"发现了什么"，不记录"排除了什么"。可是对排查来说，"payment 服务的日志正常，已排除"和"db-2 超时"同样重要：丢了前者，模型会在压缩之后把 payment 再查一遍。第一篇的重复检测只能拦住**连续**的相同调用，压缩前后隔了好几轮的重复，它拦不住。

第二篇里 `host=db-<N>` 抹掉了具体主机的例子在这里同样适用：摘要也是一种聚合，聚合会丢失细节。"附上原始证据"就是要求模型在概括的同时保留下钻的线索。

还有几个细节：

- **摘要读的是原文。** 摘要的输入取自完整历史而不是视图，所以第一级清掉的工具结果，写摘要时仍然能读到。这是分开历史和上下文的另一个好处。
- **摘要是滚动的。** 第二次压缩时，上一次的摘要和新的一段历史一起交给模型，生成新的摘要。`summary` 永远只有一份，不会越积越多。
- **摘要可以用便宜的模型。** `ContextPolicy.Summarizer` 可以单独配置，写摘要不需要排查推理的能力。代价是摘要质量可能下降，需要用第 5 篇的评估来验证。
- **摘要被截断就报错。** 半截摘要比没有摘要更危险，因为它看起来是完整的。这和第一篇"截断的工具调用不执行"是同一个原则。

## 哪些不能交给摘要

摘要是模型写的，模型会遗漏、会概括过头，偶尔还会写错。所以有一条原则：**能用代码保留的信息，不交给摘要。**

对照这条原则，有三样东西不经过摘要：

**任务本身。** `transcript[:head]` 是用户最初的请求，永远原样保留在上下文开头。摘要可能把"api 服务 14:02 起大量 5xx，只看不要动"概括成"排查 api 的 5xx"，丢掉的那半句恰恰是最重要的约束。任务描述通常很短，没有理由压缩它。

**最近几轮。** `KeepTurns` 轮之内的消息保持原样，包括工具结果。模型正在进行的推理依赖这些细节，而且它们还没来得及被模型"消化"成文字。

**写操作。** 这是最不能丢的一项。如果摘要漏掉了"14:20 已经重启过 api"，模型在压缩之后可能再重启一次。第二篇的幂等键只能防住"同一个调用被重放"，防不住模型发起一个新的、ID 不同的重启。

写操作的记录由 Harness 从历史中直接提取。工具是不是只读，第二篇的 `ToolSpec.ReadOnly` 已经标好了：

```go
// ledger 从历史中提取所有写操作及其结果。这部分由代码生成，不交给模型摘要。
func (a *Agent) ledger(msgs []Message) string {
	results := map[string]ToolResult{}
	for _, m := range msgs {
		for _, r := range m.ToolResults {
			results[r.CallID] = r
		}
	}
	var b strings.Builder
	for _, m := range msgs {
		for _, c := range m.ToolCalls {
			if t, ok := a.Tools[c.Name]; ok && t.Spec().ReadOnly {
				continue
			}
			r, ok := results[c.ID]
			status := "结果：" + clip(r.Content, 300)
			if !ok {
				status = "无结果"
			} else if r.IsError {
				status = "失败：" + clip(r.Content, 300)
			}
			fmt.Fprintf(&b, "- %s(%s) [%s] %s\n", c.Name, c.Args, c.ID, status)
		}
	}
	return b.String()
}
```

这就是 `summary` 和 `ledger` 分成两个字段的原因：`ledger` 每次都从历史重新生成，不会被下一次摘要再概括一遍。压缩后模型看到的交接消息是这样的：

```
[较早的对话已被压缩]

## 进展摘要
1. 已确认：14:02:11 起 api 出现 upstream timeout (host=db-2)，15 分钟内 3870 次；
   其他 db 节点无超时。连接池耗尽（402 次）在 14:02:13 出现，晚于超时，判断为结果而非原因。
2. 已排除：payment 日志正常；14:00 前后没有部署记录。
3. 见下方写操作记录。
4. 未解决：db-2 为什么超时。下一步查 db-2 的慢查询和连接数。

## 已执行的写操作（Harness 记录，原文）
- restart_service({"service":"api","reason":"连接池泄漏"}) [toolu_01] 结果：api 已触发滚动重启
```

上半部分是模型写的，可能有错；下半部分是代码生成的，一定准确。`ReadOnly` 默认是 `false`，漏标的只读工具会出现在写操作记录里，多占一点上下文，但不会漏掉真正的写操作。这和第二篇选择默认值的思路一样。

## 压不下去的时候

有两种情况，压缩也救不回来。

第一种是**单个工具结果就超过了窗口**。第二篇的工具都控制了返回量，但新接入的工具未必，一次 `kubectl get pods -A -o yaml` 就可能返回几十万 token。这种结果在最近一轮里，既不会被清除，也不会被摘要。所以 Harness 在工具结果进入历史之前加一道上限：

```go
out, err := t.Call(ctx, c.Args)
// ...
return clip(out, a.Context.MaxResult), err
```

`clip` 截断时会写明总长度，和第二篇的工具一样。这是最后一道防线，不能代替工具本身的聚合设计。

第二种是**两级压缩都做完了，仍然超过窗口**，比如 `KeepTurns` 设得太大，最近几轮本身就放不下。这时继续调用模型只会得到 API 的报错，所以循环新增一个停止原因：

```go
const StopContextOverflow StopReason = "context_overflow"
```

第一篇说过，StopReason 是 Agent 和调用方之间的契约，每一个出口都要显式。`context_overflow` 不能混进 `model_error`：模型报错重试可能就好了，上下文超限重试多少次都一样，要调整的是 `KeepTurns`、`MaxResult` 或者工具本身。

| StopReason | 含义 | 调用方的典型处理 |
|---|---|---|
| context_overflow | 压缩后仍超过上下文窗口 | 不要重试；检查 `KeepTurns`、`MaxResult` 和工具的返回量 |

## 补上收尾轮

第一篇在"停下来之后"一节提了一个做法，没有实现：预算耗尽时，`Final` 可能只是一句"让我再查一下数据库"，对用户毫无意义。更好的做法是禁用工具，再调一次模型，让它总结目前的发现。

收尾轮和摘要其实是同一件事：**摘要是交接给之后的自己，收尾轮是交接给人。**所以它直接复用 `handoffSections`：

```go
func (a *Agent) wrapUp(ctx context.Context, view []Message, stop StopReason) ([]Message, Usage, error) {
	ask := Message{Role: RoleUser, Content: fmt.Sprintf(
		"任务因 %s 停止，不能再调用工具。请基于目前已有的信息，给接手的人写一份交接说明：\n%s", stop, handoffSections)}
	resp, err := a.Model.Generate(ctx, append(view, ask), nil) // 不提供任何工具
	if err != nil {
		return nil, resp.Usage, err
	}
	reply := resp.Message
	reply.ToolCalls = nil // 即使模型仍然发出了工具调用，也不执行
	return []Message{ask, reply}, resp.Usage, nil
}
```

循环里原来的 `done` 换成 `finish`，在返回之前判断是否需要收尾：

```go
finish := func(stop StopReason, turns int, err error) Result {
	if a.Limits.WrapUp && wrapsUp(stop) {
		if extra, u, werr := a.wrapUp(ctx, st.view(msgs), stop); werr == nil {
			msgs = append(msgs, extra...)
			usage.Add(u)
		}
	}
	return Result{Stop: stop, Final: lastText(msgs), Messages: msgs, Turns: turns, Usage: usage, Err: err}
}
```

几个设计决定：

- **哪些停止原因需要收尾。** `max_turns`、`token_budget`、`repeated_call`、`tool_failures` 这四种，模型都已经做了一些工作，值得交代一下。`completed` 已经有结论，`canceled` 是用户要求立刻停下，`truncated` 和 `model_error` 说明模型调用本身有问题，`context_overflow` 则根本放不下再一次调用，这几种都不收尾。
- **收尾不改变 StopReason。** 收尾之后 `Stop` 仍然是 `max_turns`，调用方仍然知道这是一次预算耗尽的任务，只是 `Final` 从一句没头没尾的话变成了一份交接说明。收尾失败也不影响返回，`Final` 退回到原来的最后一条文本。
- **收尾的预算。** 收尾在主预算检查之后执行，不受 `TokenBudget` 限制，所以实际的总消耗上限是"主预算 + 一次收尾的开销"。一次收尾的输入就是当前的整个上下文，这是控制上下文大小的又一个理由。

## 测试

压缩的测试有一个难点：要让上下文"变大"，又不想真的构造几十万 token 的消息。办法是利用循环信任 API 返回的 `InputTokens`，在脚本化模型的响应里直接填上一个大数：

```go
func withUsage(r Response, in int) Response { r.Usage = Usage{InputTokens: in, OutputTokens: 100}; return r }
```

再包一层记录模型，保存每次调用收到的上下文，就能检查压缩之后模型到底看到了什么：

```go
func TestCompactKeepsTaskAndLedger(t *testing.T) {
	m := &recordingModel{scriptedModel: scriptedModel{script: []Response{
		withUsage(toolUse("restart_service", `{"service":"api","reason":"连接池泄漏"}`), 1000),
		withUsage(toolUse("search_logs", `{"service":"api"}`), 3000),
		withUsage(toolUse("search_logs", `{"service":"payment"}`), 5000),
		withUsage(toolUse("search_logs", `{"service":"api-gateway"}`), 7000),
		withUsage(toolUse("search_logs", `{"service":"db"}`), 9000),
		withUsage(answer("根因是 db-2 连接数打满"), 3000),
	}}}
	sum := &recordingModel{scriptedModel: scriptedModel{script: []Response{answer("db-2 大量超时，已排除 payment")}}}
	a := newAgent(m, bigLogs, restart) // restart 是一个 ReadOnly=false 的假工具
	a.Context = ContextPolicy{Window: 100_000, CompactAt: 6000, CompactTo: 500, KeepTurns: 2, Summarizer: sum}

	r := a.Run(context.Background(), task)
	last := m.calls[len(m.calls)-1]
	// 任务原样保留在开头；交接消息里既有摘要，也有写操作记录
	// 每个工具结果都能找到对应的调用；完整历史里没有任何被清除的结果
	// ...
}
```

其中"每个工具结果都能找到对应的调用"值得单独写成一个辅助函数，因为这类错误在测试里不会报错，只有发给真实 API 时才会被拒绝：

```go
// 每个 tool_result 都要能在它前面找到对应的 tool_use
func checkPairs(t *testing.T, view []Message) {
	t.Helper()
	calls := map[string]bool{}
	for _, m := range view {
		for _, c := range m.ToolCalls {
			calls[c.ID] = true
		}
		for _, r := range m.ToolResults {
			if !calls[r.CallID] {
				t.Fatalf("orphan tool result %s", r.CallID)
			}
		}
	}
}
```

其他几个测试：

- 第一级压缩够用时，摘要模型不会被调用（传入一个一调用就让测试失败的模型）；
- 单个工具结果超过窗口时以 `context_overflow` 结束，设置 `MaxResult` 之后同一个场景正常完成；
- 轮数耗尽时执行收尾轮，最后一次调用没有工具，`Stop` 仍然是 `max_turns`，`Final` 是交接说明；
- 取消时不执行收尾轮。

和前两篇一样，这些测试保证的是机制正确，不能保证摘要的质量。摘要有没有保留关键证据、压缩之后模型有没有重复查已经排除的方向，只能从真实任务的轨迹里看出来。

## 小结

上下文管理的核心是把两样东西分开：历史是发生过的全部事情，必须完整、只能追加；上下文是每一轮发给模型的视图，应该尽可能小。分开之后，压缩不再需要在"省 token"和"丢信息"之间二选一，因为信息从来没有被删除，只是没有出现在这一轮的视图里。

在此基础上，压缩的设计可以逐项检查：

1. **什么时候压缩**：用 API 返回的真实 token 数判断，检查放在调用模型之前；用两条水位线成批压缩，不要每轮滑动。
2. **怎么压缩**：先清除旧的工具结果，不调用模型；不够再摘要。切点放在 assistant 消息上，工具调用和结果不能拆开。
3. **摘要写什么**：告诉模型它之后看不到原文；要求保留原始证据和已排除的方向。
4. **什么不交给摘要**：任务本身、最近几轮、写操作记录。能用代码保留的，不交给模型。
5. **压不下去怎么办**：工具结果进入历史前加上限；仍然超窗口就以 `context_overflow` 停下，不要混进 `model_error`。
6. **停下来之后**：预算类的停止执行收尾轮，复用摘要的结构，不改变 StopReason。

本文多次提到"需要从真实任务的轨迹里看"：压缩触发了几次、每次省了多少 token、收尾轮占了多少成本、`KeepTurns` 和水位线该设多少。第一篇的预算上限也留了同样的问题。这些都需要先把 Agent 每一轮做了什么记录下来。下一篇讨论可观测性：怎样给 Agent 加 trace，按停止原因和工具做统计，用数据而不是直觉来定这些参数。
