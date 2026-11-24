---
title: "Agent 的 trace，要能还原模型当时看到了什么"
date: 2026-11-24T08:00:00+08:00
slug: agent-observability
categories:
- ai
series:
- agent-engineering
tags:
- AI Agent
- Harness Engineering
- Observability
- Go
featured: true
---

前三篇留下了一串"要看数据才能定"的参数：第一篇的轮数和 token 上限要取"比 P99 略高的值"，第三篇的 `CompactAt`、`CompactTo`、`KeepTurns` 要从真实任务里调。还有一类问题连参数都谈不上：Agent 给出了一个错误的结论，循环以 `completed` 正常结束，没有任何报错，你想知道它是在哪一步想错的。

这两类问题都需要先把 Agent 每一轮做了什么记录下来。本文是「Agent 工程笔记」系列的第四篇，继续以 Go 实现的线上故障排查 Agent 为例，讨论 trace 该记什么、怎样用很小的存储还原模型每一轮看到的上下文，以及怎样从一批运行的统计里定出上限、压缩参数和成本预期。

<!--more-->

## 普通的日志回答不了的问题

先看一个具体的失败。用户问"api 服务 14:02 起大量 5xx，查一下原因"，Agent 跑了 11 轮，结论是"根因是 api 的连接池泄漏，建议重启"。实际的根因是 db-2 的慢查询，连接池耗尽只是结果。

如果只有普通服务的那套日志和指标，你能看到的是：11 次模型调用全部成功，平均延迟 2.8 秒；14 次工具调用全部成功；总共 9.6 万 token。每个数字都正常，因为**Agent 的失败大多不是异常，而是决策**。没有哪一行代码出错，是模型在某一轮做了一个错误的判断。

要定位这个判断，需要回答的问题是这样的：

- 第 7 轮模型决定不再追查 db-2，它当时看到了什么？
- db-2 超时的那条日志结果，那时还在上下文里吗？还是已经被第三篇的第一级压缩清掉了？
- 如果做过摘要，摘要里有没有保留"超时早于连接池耗尽"这个时间顺序？

这些问题的共同点是：**都要还原模型在某一轮看到的上下文**。延迟和 token 数只是附带的。

## 一次运行记什么

一次运行（run）由若干轮（turn）组成，每一轮里依次可能发生：压缩、一次模型调用、若干次工具调用。运行结束时可能还有一次收尾轮。trace 就按这个结构记录，每件事一条事件：

```go
type Event struct {
	RunID string
	Turn  int
	Kind  EventKind // model | tool | compact | wrap_up | run_end
	Start time.Time
	Dur   time.Duration
	Usage Usage
	Err   string

	// model：这一轮的视图如何从历史派生，以及模型的决定
	View   *ViewRef
	Finish FinishReason

	// tool
	Tool    string
	CallID  string
	Args    json.RawMessage
	ErrKind ErrorKind
	Bytes   int // 结果截断前的大小

	// compact
	Level         string // clear 或 summarize
	Before, After int
	Summary       string // 只在 summarize 时记录
	Ledger        string

	// run_end
	Stop       StopReason
	Transcript []Message
}
```

（实际代码里每个字段都带 `json:",omitempty"` 标签，这里省略了。）

几个取舍：

- **一个扁平的结构，而不是每种事件一个类型。** 事件最终要写进 JSONL、日志系统或者数据仓库，扁平结构最好处理，不同种类的事件只是用到的字段不同。
- **记 token，不记钱。** 价格会变，摘要可能用的是另一个更便宜的模型。原始数据只记 token，成本在分析时按当时的价格算，后面"成本"一节再展开。
- **工具结果记截断前的大小。** 第三篇在工具结果进入历史之前加了 `MaxResult` 上限。如果只记截断后的大小，就永远看不出哪个工具经常返回几十万字节，而这正是要回去改工具设计的信号。
- **错误按第二篇的 `ErrorKind` 分类。** `invalid_args` 多说明工具描述没写清楚，`unavailable` 多说明依赖有问题，两者的处理完全不同，统计时不能混在一起。
- **不记工具结果的内容。** 内容在完整历史里已经有了，下一节会说为什么不需要重复记。

## 不存视图，存下标

要还原模型每一轮看到的上下文，最直接的办法是把每一轮的视图原样存下来。但这又回到了第三篇开头那笔账：第 n 轮的上下文包含前面所有轮次，每轮都存一份，存储量随轮数平方增长，和不做压缩时的 token 消耗一样。

第三篇把历史和上下文分开之后，这个问题有了更好的解法。上下文是历史的视图，`view` 是一个纯函数：输入是完整历史和 `contextState` 里的几个下标、两段文本，输出就是这一轮发给模型的消息。所以 trace 不需要存视图，只需要存**生成视图的参数**：

```go
// ViewRef 记录视图的下标。view 是历史的纯函数，有了下标和摘要就能原样重建。
type ViewRef struct {
	Head, From, ClearedTo int
	Len                   int // 调用模型时历史的长度
}
```

`Len` 是调用模型那一刻历史的长度，因为历史只追加，前 `Len` 条消息就是模型当时面对的全部历史。摘要和写操作记录只在压缩发生变化时才变，所以只在 `summarize` 事件里记一次。完整历史在 `run_end` 事件里记一次。

还原某一轮的视图，就是找到这几样东西，再调一次 `view`：

```go
// ViewAt 重建第 turn 轮发给模型的上下文。
func ViewAt(events []Event, turn int) ([]Message, error) {
	var transcript []Message
	var ref *ViewRef
	var st contextState
	for _, e := range events {
		switch {
		case e.Kind == EventRunEnd:
			transcript = e.Transcript
		case e.Kind == EventModel && e.Turn == turn:
			ref = e.View
		case e.Kind == EventCompact && e.Level == "summarize" && e.Turn <= turn:
			st.summary, st.ledger = e.Summary, e.Ledger
		}
	}
	if ref == nil || transcript == nil {
		return nil, fmt.Errorf("turn %d not found", turn)
	}
	st.head, st.from, st.clearedTo = ref.Head, ref.From, ref.ClearedTo
	return st.view(transcript[:ref.Len]), nil
}
```

压缩事件发生在同一轮的模型调用之前，所以条件是 `e.Turn <= turn`。

这样一次运行的存储量是"完整历史 + 每轮几个整数 + 每次摘要一段文本"，和轮数成线性关系。前面那个错误结论的例子，现在可以直接调 `ViewAt(events, 7)`，看第 7 轮模型到底看到了什么。

这个方案有一个前提：**`view` 必须是确定的**。如果哪天在构造视图时加入了当前时间、随机采样或者外部查询，同样的参数就不再能还原出同样的上下文。后面"测试"一节有一个测试专门守住这一点。

还有两样东西不在历史里：系统提示和工具定义。它们会随着版本迭代变化，同一个 run 的 trace 必须能对应到当时的版本。最简单的做法是给它们算一个版本号或哈希，和 RunID 一起记下来。第 5 篇做评估时，"这次改了哪个版本的 prompt"正是要对比的对象。

## 埋点放在哪里

事件全部在 `Run` 里发出，不分散到各个函数里。下面是循环里新增的部分：

```go
rec := recorder{tracer: a.Tracer, runID: rand.Text()}
// ...
// 压缩：前后对比 contextState，就知道做的是哪一级
if a.Context.CompactAt > 0 && ctxTokens > a.Context.CompactAt {
	t0, from := time.Now(), st.from
	u, err := a.compact(ctx, msgs, &st)
	usage.Add(u)
	e := Event{Turn: turn, Kind: EventCompact, Start: t0, Dur: time.Since(t0), Usage: u, Err: errText(err),
		Level: "clear", Before: ctxTokens, After: estimate(st.view(msgs))}
	if st.from != from {
		e.Level, e.Summary, e.Ledger = "summarize", st.summary, st.ledger
	}
	rec.emit(e)
	// ...
}
t0 := time.Now()
resp, err := a.Model.Generate(ctx, st.view(msgs), specs)
rec.emit(Event{Turn: turn, Kind: EventModel, Start: t0, Dur: time.Since(t0), Usage: resp.Usage,
	Finish: resp.Finish, View: st.ref(len(msgs)), Err: errText(err)})
// ...
results, events, unavailable := a.execute(ctx, resp.Message.ToolCalls)
for _, e := range events {
	e.Turn = turn
	rec.emit(e)
}
```

`compact` 本身一行没改：调用前后对比 `st.from` 是否变化，就知道这次有没有做摘要。

`execute` 的返回值多了一组工具事件。每个工具调用的耗时、截断前的大小和错误类型都在 `execute` 里采集，因为只有它知道每个调用各自的起止时间（只读工具是并行执行的）。原来在 `callTool` 里做的 `clip` 也挪到了这里，先记下原始大小再截断：

```go
run := func(i int) {
	c, t0 := calls[i], time.Now()
	out, err := a.callTool(ctx, c)
	e := Event{Kind: EventTool, Tool: c.Name, CallID: c.ID, Args: c.Args, Start: t0}
	if err != nil {
		out, e.ErrKind = err.Error(), kindOf(err)
	}
	e.Dur, e.Bytes = time.Since(t0), len(out) // 记录截断前的大小
	results[i] = ToolResult{CallID: c.ID, Content: clip(out, a.Context.MaxResult), IsError: err != nil}
	events[i] = e
}
```

收尾轮和 `run_end` 在 `finish` 里发出，`run_end` 带上完整历史和最终的 StopReason。

`recorder` 只做两件事：填上 RunID，以及保证 trace 出问题时不影响 Agent：

```go
func (r recorder) emit(e Event) {
	if r.tracer == nil {
		return
	}
	defer func() { _ = recover() }() // trace 出问题不能影响排查本身
	e.RunID = r.runID
	r.tracer.Event(e)
}
```

这里的原则是：**观测不能改变被观测的东西**。trace 是辅助设施，它的 bug 不应该让一次线上排查中途崩溃；它也不能影响控制流，比如不能因为写 trace 慢就跳过某个检查。`Tracer` 接口只有一个方法，没有返回值，调用方根本无法根据它的结果做决定。

最简单的实现是每个事件写一行 JSON：

```go
type JSONLTracer struct {
	mu  sync.Mutex
	enc *json.Encoder
}

func (t *JSONLTracer) Event(e Event) {
	t.mu.Lock()
	defer t.mu.Unlock()
	_ = t.enc.Encode(e)
}
```

加锁是因为工具事件可能来自并行执行的 goroutine。准确地说，当前实现在 `execute` 返回之后才统一发出工具事件，但接口的契约应该允许并发调用，以后改成实时发出时不需要改实现。

如果团队已经在用 OpenTelemetry，也可以把这套事件映射成 span：run 是根 span，模型调用和工具调用是子 span，OpenTelemetry 的 GenAI 语义约定已经为模型名、token 用量等定义了标准属性。但完整历史和摘要这种大段文本不适合放进 span 属性，通常的做法是把它们存到对象存储，span 上只带 RunID 和存储位置。

## 读一次运行

有了事件，最先用到的是把一次运行打印成时间线。下面是一次排查的时间线（数字是示意）：

```
t1   model      2.3s  in=3412   out=212   tool_use
     tool       0.6s  search_logs {"service":"api","since":"30m"}  1840B ok
t2   model      3.1s  in=5480   out=305   tool_use
     tool       0.4s  inspect_service {"service":"api"}  920B ok
     tool       0.9s  query_metrics {"service":"db","metric":"latency_p99"}  2210B ok
t3   model      2.6s  in=8130   out=188   tool_use
     tool       1.2s  query_slow_log {"host":"db-2","since":"30m"}  48211B ok
...
t7   compact    0.0s  clear 41260→17830
t7   model      2.9s  in=17905  out=240   tool_use
...
end  completed  turns=11  tokens=96420  41s
```

只看这一屏，已经能发现前面那个错误结论的线索：第 3 轮 `query_slow_log` 返回了 48KB，被 `MaxResult` 截断。这是后来新接入的工具，直接返回原始的慢查询日志，没有按第二篇的方式做聚合。之后，第 7 轮的第一级压缩又把它清除了。再用 `ViewAt(events, 7)` 看一下模型在第 7 轮的上下文，那份慢查询结果只剩一行占位符。模型在那之后再也没有回去查 db，是因为它在第 3 轮看到的就是被截断的半截结果，而截断的部分恰好包含时间顺序。

修复的方向也随之清楚：不是改 prompt，而是让 `query_slow_log` 像第二篇的 `search_logs` 一样先聚合再返回，而不是依赖 Harness 的硬截断。

时间线还能暴露参数配置的问题。下面这段来自本文的测试用例：

```
t3   model      in=5000   out=100   tool_use
t4   compact    summarize 7200→4312
t4   model      in=7000   out=100   tool_use
t5   compact    summarize 9200→4314
t5   model      in=9000   out=100   tool_use
t6   compact    summarize 11200→4313
```

每一轮都在做摘要，压缩后的大小却一直停在 4300 左右。原因是 `CompactTo` 设成了 500，而 `KeepTurns` 保留的最近两轮本身就有 4000 多 token，压缩永远达不到目标，下一轮一涨又超过 `CompactAt`。第三篇说压缩要成批做、不要每轮做，这种配置恰好违反了它：每轮多花一次摘要的钱，提示缓存也每轮失效。这个问题在任何单条日志里都看不出来，在时间线上一眼就能看到。

## 从一次运行到一批运行

单次运行的 trace 用来定位具体问题，参数要靠一批运行的统计来定。每次运行先归纳成一行：

```go
type RunStats struct {
	RunID       string
	Stop        StopReason
	Turns       int
	Dur         time.Duration
	Usage       Usage // 全部消耗，含压缩和收尾
	Summarizer  Usage // 其中摘要的部分
	WrapUp      Usage // 其中收尾轮的部分
	Cumulative  []int // 第 i 轮结束时的累计 token，用来模拟更紧的上限
	MaxInput    int   // 单轮最大输入，即上下文的峰值
	Compactions int
	Summaries   int
	ToolCalls   map[string]int
	ToolErrors  map[ErrorKind]int
	Revisits    int // 压缩之后，重新发起压缩之前做过的相同调用
}
```

`Stats(events)` 按顺序扫一遍事件就能算出这些字段。大部分字段是直接累加，有两个值得单独说。

**`Cumulative`** 记录每一轮结束时的累计 token。它的用处在下一节：有了它，就能回答"如果上限更紧，这次运行会在哪里停下、花多少"。

**`Revisits`** 是第三篇留下的问题：压缩之后，模型会不会重新去查已经查过、甚至已经排除的方向。统计方法是记下每个调用（工具名加规范化后的参数，复用第一篇的 `callsKey`）最近一次发起的轮次，如果它在一次压缩之后又出现了，就算一次重访：

```go
case EventTool:
	key := callsKey([]ToolCall{{Name: e.Tool, Args: e.Args}})
	if t, ok := seen[key]; ok && t < lastCompact {
		s.Revisits++
	}
	seen[key] = e.Turn
```

第一篇的重复检测只能拦住连续的相同调用，`Revisits` 统计的是隔着压缩的重复。它不一定是坏事，有时候模型确实需要重新看一眼结果，但如果它随着 `KeepTurns` 调小而明显上升，就说明压缩丢了模型还需要的信息。

## 按停止原因看分布

第一篇把 StopReason 定义为 Agent 和调用方之间的契约。对单次运行，它告诉调用方该怎么处理；对一批运行，**每种停止原因所占的比例，都是一个可以追踪的指标**。

比如对 200 次排查任务做一次统计（数字是示意）：

| StopReason | 占比 | 轮数 P50 / P90 | token P50 / P90 |
|---|---|---|---|
| completed | 78% | 8 / 14 | 6.1 万 / 13 万 |
| max_turns | 11% | 15 / 15 | 17 万 / 22 万 |
| token_budget | 4% | 9 / 12 | 20 万 / 20 万 |
| repeated_call | 3% | 6 / 10 | 4.2 万 / 9 万 |
| tool_failures | 2% | 3 / 4 | 1.5 万 / 2.4 万 |
| 其他 | 2% | | |

单看这张表，就有几个值得追的问题：

- **`max_turns` 的轮数 P50 和 P90 都是 15。** 这是上限本身，说明这部分任务的真实需求被截断了，看不出它们本来需要多少轮。下一节专门讨论这个问题。
- **`token_budget` 只用了 9 轮就耗尽预算。** 平均每轮两万多 token，远高于 `completed` 的水平。这通常不是任务复杂，而是某个工具返回量过大，按 `Bytes` 排一下工具就能找到。应该改工具，而不是加预算。
- **`repeated_call` 集中在少数几类任务上。** 把这些运行的时间线拉出来，常见的原因是工具的错误提示没有告诉模型下一步该怎么做（第二篇的 `Hint`）。

每种停止原因比例上升时意味着什么，可以整理成一张表，和第一篇的处理表放在一起看：

| 比例上升的 StopReason | 通常说明 | 先看什么 |
|---|---|---|
| max_turns | 任务变复杂，或模型在绕圈 | 轮数分布；最后几轮的调用是否重复 |
| token_budget | 单轮消耗过大 | 按 `Bytes` 排序的工具；`MaxInput` |
| repeated_call | 模型卡住 | 卡住时的工具错误和提示 |
| tool_failures | 依赖服务有问题 | `ToolErrors` 中 `unavailable` 的分布 |
| truncated | 输出上限太低 | 模型输出 token 的分布 |
| context_overflow | 压缩参数或工具返回量有问题 | `KeepTurns`、`MaxResult`、压缩后的大小 |

这些比例最适合做成趋势图：换了模型、改了 prompt、加了一个工具之后，哪一项变了，一目了然。至于 `completed` 里有多少结论是对的，这张表回答不了，那是第 5 篇评估的事。

## 上限从轨迹里算出来

第一篇说上限应该取"正常任务实际用量的 P99 再高一点"。真去算的时候会发现一个问题：**你看到的分布已经被上限截断了**。`MaxTurns` 设成 15，需要 20 轮的任务在第 15 轮就以 `max_turns` 停下，它在数据里永远是 15 轮。把所有运行的轮数放在一起算 P99，得到的就是 15，什么也说明不了。只看 `completed` 的运行也不对，那等于假设被截断的任务都不存在。

办法是先用宽松的上限跑一批，比如 `MaxTurns` 设到 60、token 预算放到很大，拿到真实的分布。这一步不要直接在线上做，用第 5 篇要讲的评估集，或者回放历史故障来跑。

宽松上限的运行有一个很好的性质：**更紧的上限只是把轨迹截短，截短之前的部分和真实运行完全一样**。一次跑了 25 轮的运行，如果上限是 15，它会在第 15 轮结束时停下，前 15 轮一模一样，花掉的 token 就是 `Cumulative[14]`。所以一批宽松上限的运行，可以离线模拟任意更紧的上限：

```go
// TurnCurve 用宽松上限下的运行，模拟更紧的 MaxTurns 会得到什么结果。
// 更紧的上限只是把轨迹截短，所以截短之前的部分和真实运行完全一样。
func TurnCurve(runs []RunStats, ok func(RunStats) bool, limits ...int) []Point {
	var pts []Point
	for _, k := range limits {
		var succ, tokens float64
		for _, r := range runs {
			if r.Turns <= k {
				tokens += float64(r.Usage.Total() - r.WrapUp.Total())
				if ok(r) {
					succ++
				}
			} else {
				tokens += float64(r.Cumulative[k-1]) // 第 k 轮结束时就会停下
			}
		}
		n := float64(len(runs))
		pts = append(pts, Point{Limit: k, Success: succ / n, MeanTokens: tokens / n})
	}
	return pts
}
```

反过来就不行：上限 15 跑出来的数据，回答不了上限 25 会怎样。所以**收集数据时上限要放宽，定上限时再收紧**。

`ok` 判断一次运行是否成功。最粗的版本是 `r.Stop == StopCompleted`，但 `completed` 不等于结论正确，更好的做法是用人工标注或第 5 篇的评估结果。

对 200 次宽松上限的运行算出的曲线大致是这样（数字是示意）：

| MaxTurns | 成功率 | 每次平均 token |
|---|---|---|
| 10 | 61% | 5.8 万 |
| 15 | 82% | 7.4 万 |
| 20 | 89% | 8.3 万 |
| 30 | 92% | 9.6 万 |
| 60 | 93% | 11.2 万 |

从 15 放到 20，成功率涨 7 个点，平均成本涨 12%；从 30 放到 60，成功率只涨 1 个点，成本涨 17%。上限应该设在曲线变平的地方，这里是 20 到 30 之间。这比"P99 再高一点"更好，因为它直接把**多一轮带来的收益和多一轮的成本**放在一起比较，而 P99 只看了成本这一边。

用这条曲线时有几点要注意：

- **长尾的成功要打折扣。** 第 30 轮之后才完成的运行，结论的可信度往往更低，模型可能是绕了很多圈之后"凑"出了一个答案。如果 `ok` 只看 `completed`，曲线尾部会显得比实际更好。
- **收尾轮没有被模拟。** 上限收紧后，被截断的运行会多一次收尾轮，实际成本比模拟值略高。
- **token 预算用同样的方法。** 在 `Cumulative` 里找第一个超过预算的轮次，就是这次运行在该预算下停下的位置。轮数上限和 token 预算应该让一个主要起作用，另一个作为保险；如果两者都经常触发，说明其中一个设得不对。
- **要定期重算。** 换模型、改 prompt、加工具都会改变这条曲线。这件事也适合放进第 5 篇的评估流程里。

## 压缩参数也一样

第三篇的压缩参数可以用同样的思路调，看这几个指标：

- **每次运行的压缩次数，以及压缩后的大小是否低于 `CompactTo`。** 压缩后仍高于 `CompactTo` 的比例一旦明显大于零，就是前面时间线里那种每轮都在压缩的配置。
- **摘要占压缩的比例。** 多数压缩应该在第一级就够用。如果摘要占比很高，要么 `CompactTo` 太低，要么任务的轮数确实很多。
- **`Revisits`。** 调小 `KeepTurns` 或降低 `CompactTo` 能省 token，但如果重访率随之上升，省下的 token 又被重复调用花回去了，还可能丢掉结论。
- **摘要的成本占比。** `Summarizer` 里的 token 占总消耗的比例。如果为了省钱换了更便宜的摘要模型，要同时看 `Revisits` 和成功率有没有变差。

调参的方法和定上限一样：固定一批任务，改一个参数，对比这些指标和成功率。区别在于压缩参数改变的是模型看到的内容，不能像轮数上限那样从已有轨迹离线模拟，每组参数都要真的跑一遍。

## 成本

前面说过，trace 只记 token，成本在分析时计算。每个模型有自己的价格，摘要的 token 要按摘要模型计价：

```go
// Price 是每百万 token 的价格。
type Price struct{ In, Out float64 }

func (p Price) Of(u Usage) float64 {
	return (float64(u.InputTokens)*p.In + float64(u.OutputTokens)*p.Out) / 1e6
}

// Cost 按模型分别计价：摘要可能用的是另一个模型。
func (s RunStats) Cost(main, summarizer Price) float64 {
	rest := Usage{s.Usage.InputTokens - s.Summarizer.InputTokens, s.Usage.OutputTokens - s.Summarizer.OutputTokens}
	return main.Of(rest) + summarizer.Of(s.Summarizer)
}
```

看成本时有两点比总额更有用：

- **看分布，不看平均。** Agent 的单次成本是长尾的，少数绕圈的运行可能花掉平均值的十倍。预算和告警应该按 P90、P99 定，平均值会掩盖它们。
- **按阶段拆开。** 主循环、摘要、收尾轮各占多少。第三篇说收尾轮的输入是整个当前上下文，如果它的占比很高，说明预算类停止太多，或者停下时上下文太大。

这里的成本计算没有考虑提示缓存。缓存命中的输入 token 价格只有正常价格的一小部分，对 Agent 这种前缀稳定、反复调用的场景影响很大，第 9 篇会专门讨论，届时 `Usage` 要增加缓存相关的字段。

## trace 里有什么

最后说一个容易被忽略的问题：trace 里存的是完整历史，也就是所有工具结果的原文。对排查 Agent 来说，这意味着线上日志、可能包含用户信息的请求内容、内部服务的拓扑，都会原样进入 trace 存储。

所以 trace 存储要按生产数据对待：访问控制、保留期限、必要时脱敏。脱敏最好放在 Tracer 的实现里，而不是放在工具里：工具返回给模型的内容不应该因为"要写 trace"而改变，否则又违反了"观测不能改变被观测的东西"。

## 测试

trace 的测试要守住三件事。

**还原出的视图和模型当时收到的完全一致。** 用第三篇的 `recordingModel` 记下模型每次收到的上下文，再用 trace 逐轮还原，逐条比较。测试场景故意触发了多次滚动摘要：

```go
func TestTraceReplaysView(t *testing.T) {
	tr := &memTracer{}
	m, r := compactingRun(tr)
	// ...
	// 用 trace 重建的每一轮上下文，必须和模型当时收到的完全一致
	for i, got := range m.calls {
		v, err := ViewAt(tr.events, i+1)
		if err != nil {
			t.Fatal(err)
		}
		if !reflect.DeepEqual(v, got) {
			t.Fatalf("turn %d: replayed view differs", i+1)
		}
	}
}
```

这个测试就是前面说的"`view` 必须是确定的"那条前提的守护者。以后谁在构造视图时加入了不确定的东西，它会第一个失败。另一个测试把事件写成 JSONL 再读回来，确认还原经过序列化之后仍然成立，因为线上的 trace 都是从存储里读出来的。

**trace 不改变 Agent 的行为。** 同一个场景分别不带 Tracer 和带一个每次都 panic 的 Tracer 运行，结果必须完全相同：

```go
type panicTracer struct{}

func (panicTracer) Event(Event) { panic("tracer bug") }

func TestTracerDoesNotChangeBehavior(t *testing.T) {
	_, plain := compactingRun(nil)
	_, traced := compactingRun(panicTracer{})
	if plain.Stop != traced.Stop || plain.Turns != traced.Turns || plain.Usage != traced.Usage || plain.Final != traced.Final {
		t.Fatalf("tracer changed the run: %+v vs %+v", plain, traced)
	}
}
```

**统计是对的。** `Stats` 算出的总消耗必须等于 `Result.Usage`，`Cumulative` 的最后一项必须等于总消耗，压缩之后重新查询同一个服务要被计为一次 `Revisits`。`TurnCurve` 用几条手工构造的 `RunStats` 验证：上限 10 时，跑了 12 轮的运行按第 10 轮的累计 token 计算，跑了 30 轮未完成的运行不算成功。

前面时间线里那段每轮都在压缩的输出，就是写 `Stats` 测试时发现的：测试用例里的 `CompactTo` 随手设成了 500，断言压缩次数时才发现它每轮都在触发。这也算是一个小小的证明：有了 trace，配置问题会自己浮出来。

## 小结

Agent 的可观测性和普通服务最大的区别是：要排查的大多不是异常，而是模型的决策。所以 trace 的第一个要求是能还原模型在每一轮看到的上下文，延迟和 token 都排在后面。

把这件事做到可用，可以逐项检查：

1. **记什么**：按 run → turn → 压缩、模型调用、工具调用组织事件；记 token 不记钱；工具结果记截断前的大小；错误按类型分类。
2. **怎么还原上下文**：不存视图，存生成视图的下标；摘要只在变化时记一次；完整历史记一次。前提是视图构造必须是确定的，要有测试守住。
3. **埋点放在哪里**：全部在循环里发出；Tracer 没有返回值，出错时 recover，不能改变 Agent 的行为。
4. **按停止原因看**：每种 StopReason 的比例都是一个指标；比例上升时先看对应的数据，而不是先改 prompt。
5. **上限怎么定**：用宽松上限收集数据，离线模拟更紧的上限；看成功率和成本的曲线，设在变平的地方。
6. **成本怎么看**：分析时按模型计价；看分布和分阶段的占比，不看平均。
7. **trace 里有什么**：完整历史就是生产数据，按生产数据管理。

本文有好几处把问题推给了"成功率"：曲线上的成功率、压缩参数调整后的成功率、`completed` 里到底有多少结论是对的。到目前为止，判断成功只能靠 `Stop == completed` 或者人工去看。下一篇讨论评估：改了一行 prompt 之后，怎样系统地知道 Agent 没有变差。
