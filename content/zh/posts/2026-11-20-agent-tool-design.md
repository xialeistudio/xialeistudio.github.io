---
title: "Agent 的工具接口，读者是模型"
date: 2026-11-20T10:00:00+08:00
slug: agent-tool-design
categories:
- ai
series:
- agent-engineering
tags:
- AI Agent
- Harness Engineering
- Tool Use
- Go
featured: true
---

上一篇讲 Agent 循环时有一个前提：工具出错时，错误信息作为工具结果交给模型，由模型决定下一步。这句话把一个问题推给了工具层：如果工具返回的内容是给模型读的，那工具接口本身应该怎么设计？

大多数 Agent 的工具是把现有的内部 API 包一层：参数照搬，返回值照搬，错误照搬。这些 API 是为程序员设计的，而现在读者换成了模型。本文是「Agent 工程笔记」系列的第二篇，继续以 Go 实现的线上故障排查 Agent 为例，把一个照搬 API 的工具一步步改成为模型设计的工具。

<!--more-->

## 读者换了

程序员和模型使用同一个接口的方式差别很大：

| | 程序员 | 模型 |
|---|---|---|
| 了解接口 | 读一次文档，记住 | 每次调用前只能看到名字、描述和参数 schema |
| 处理返回值 | 代码只取需要的字段 | 每个字节都进入上下文，占 token，还会分散注意力 |
| 遇到错误 | 打开日志，加断点调试 | 只能根据错误文本猜下一次该怎么调 |
| 不知道的信息 | 去查 | 不会去查，会编一个 |

最后一行最容易被低估。比如"当前时间"：程序员调接口时自然知道现在几点，模型并不知道，除非你在上下文里告诉它。一个要求传入绝对时间的接口，对模型来说就是一个邀请它编造时间戳的接口。

## 起点：照搬 API 的工具

排查 Agent 最常用的工具是查日志。照搬日志服务的接口，得到的工具是这样的：

```json
{
  "name": "query_logs",
  "description": "Query logs.",
  "input_schema": {
    "type": "object",
    "properties": {
      "service":    {"type": "string"},
      "start_time": {"type": "string"},
      "end_time":   {"type": "string"},
      "level":      {"type": "string"},
      "limit":      {"type": "integer"},
      "offset":     {"type": "integer"}
    }
  }
}
```

返回值是日志服务的原始 JSON。在真实的排查任务中，它会这样失败：

- 模型不知道当前时间，`start_time` 填了一个训练数据里常见的日期，查询结果为空。
- 时间对了，但时区不对，查的是八小时前的日志。
- `limit` 填 100，返回 100 条几乎一样的 `upstream timeout`，一万多 token 换来一条有用信息。
- 想看后面的日志，就用 `offset` 翻页，每翻一页花掉一轮。
- `level` 填了 `ERROR`，日志服务只认小写，返回空结果。
- 返回空结果时，模型不知道是"真的没有"还是"查错了"，于是换个参数再查，进入上一篇说的打转。

这些问题没有一个是模型"不够聪明"造成的。是接口给了模型太多犯错的机会，而犯错之后又没有给它足够的信息去纠正。

## 粒度：按问题切，不按接口切

照搬 API 的另一个后果是工具太多、太碎。日志服务有查询、统计、上下文三个接口，K8s 有 pods、events、logs 三个接口，于是 Agent 就有了六个工具，模型要自己学会"先 list pods，再对每个 pod get logs，再查 events"。

每多一步串联，就多一轮模型调用，也多一次出错的机会。更好的切法是从 Agent 要回答的问题出发：

- "这段时间出了什么错，哪种最多" → `search_logs`
- "这个服务现在是什么状态" → `inspect_service`，内部把 pods、events、最近的部署记录合并成一份摘要
- "某个指标的趋势" → `query_metrics`

判断标准很简单：如果模型几乎总是连续调用 A 和 B，那 A 和 B 应该合成一个工具。反过来，一个工具如果靠参数在几种完全不同的行为之间切换，比如 `action: "query" | "restart" | "delete"`，就应该拆开，尤其是读和写必须拆开，原因在后面"副作用"一节。

## 参数：让模型难以传错

改写后的 `search_logs`：

```go
func (SearchLogs) Spec() ToolSpec {
	return ToolSpec{
		Name: "search_logs",
		Description: `按服务和时间范围检索日志，返回按模式聚合后的摘要，而不是原始日志。
适合回答"这段时间出了什么错、哪种错最多"。
需要看某一种错误的原始日志时，把摘要里的 pattern 原样传回来。
只能查最近 24 小时；更早的数据请用 query_metrics 看趋势。`,
		Parameters: json.RawMessage(`{
  "type": "object",
  "properties": {
    "service": {"type": "string", "description": "服务名，例如 api、payment"},
    "since":   {"type": "string", "description": "从多久之前开始，例如 15m、2h，最长 24h", "default": "15m"},
    "level":   {"type": "string", "enum": ["error", "warn", "info"], "default": "error"},
    "pattern": {"type": "string", "description": "可选。只返回该模式的原始日志，取值来自上一次摘要"}
  },
  "required": ["service"]
}`),
		ReadOnly: true,
	}
}
```

和原版相比，改动都指向同一个目标：减少模型需要"知道"的东西。

- **相对时间代替绝对时间。** `since: "15m"` 不需要知道现在几点，也没有时区问题。时间换算交给工具，工具有准确的时钟。
- **枚举代替自由字符串。** `level` 只有三个取值，大小写问题不存在了。
- **默认值覆盖最常见的用法。** 排查时最常见的问题是"最近 15 分钟有什么错误"，这时只需要传 `service` 一个参数。必填参数越少，传错的机会越少。
- **去掉分页参数。** `limit` 和 `offset` 是为了控制返回量，这件事工具应该自己做，下一节展开。

`ToolSpec` 上多了一个 `ReadOnly` 字段，它带 `json:"-"` 标签，不会发给模型，只给 Harness 用，同样在后面展开。

## 描述：写清楚什么时候用

工具描述是模型了解这个工具的唯一途径，`"Query logs."` 这样的描述等于什么都没说。上面的描述回答了四个问题：

1. **它做什么**：检索日志，返回聚合摘要。
2. **什么时候用**：想知道出了什么错、哪种最多。
3. **怎么和其他调用配合**：要看原始日志，把 pattern 传回来。
4. **它做不到什么、做不到时该用什么**：只能查 24 小时，更早的用 `query_metrics`。

第 4 点经常被省略，但它最能减少无效调用。模型不知道工具的边界，就会去试探边界：传 `since: "7d"`，失败，再试 `"72h"`，再失败。在描述里写明边界和替代方案，这几轮就省掉了。

描述不必追求简短。它在每一轮都会发给模型，确实占 token，但和一次错误调用的代价相比，多几十个字的描述很便宜。

## 返回值：为上下文预算设计

原版工具返回 100 条原始日志。改写后返回的是按模式聚合的摘要：

```
api，14:00–14:15，level>=error 共 4312 条，7 种模式：
  3870× upstream timeout after <N>ms (host=db-<N>)（首次 14:02:11）
   402× connection pool exhausted, waiting <N>ms（首次 14:02:13）
    23× order <N> not found（首次 14:00:42）
     9× retry budget exceeded for /v1/charge（首次 14:05:30）
     4× slow query: <N>ms（首次 14:03:01）
其余 2 种模式共 4 条未列出。
```

几百个 token，模型就能看到全貌：错误从 14:02 开始，主要是下游数据库超时，连接池随之耗尽。这正是排查需要的信息，而 100 条原始日志里大概率只有第一种模式。

聚合的实现很朴素：把数字和十六进制 ID 替换成占位符，同一类日志就会变成同一个字符串。

```go
// 把数字、十六进制 ID 换成占位符，同一类日志就能归到一起。
var noise = regexp.MustCompile(`\b[0-9a-f]{8,}\b|\d+`)

func patternOf(msg string) string { return noise.ReplaceAllString(msg, "<N>") }
```

然后按模式计数、排序，只输出前 5 种，剩下的写一句"其余 N 种共 M 条未列出"。

聚合是有代价的：`host=db-<N>` 把具体是哪台数据库也抹掉了，而如果只有 `db-2` 有问题，这恰恰是关键信息。所以工具保留了下钻的路径，模型把 pattern 原样传回来，就能拿到这一类日志的原文：

```
api，14:00–14:15，level>=error，模式 "upstream timeout after <N>ms (host=db-<N>)" 共 3870 条，只显示最早的 20 条：
14:02:11 upstream timeout after 3000ms (host=db-2)
14:02:11 upstream timeout after 3001ms (host=db-2)
...
```

这里有一条规则值得单独强调：**截断必须明说**。"共 3870 条，只显示最早的 20 条"，模型就知道自己看到的是一部分；如果只是悄悄返回 20 条，模型会以为这就是全部，然后基于不完整的数据下结论。

空结果也一样需要明说。原版工具返回 `[]`，模型分不清是没有日志还是查错了。改写后：

```go
if len(lines) == 0 {
	return fmt.Sprintf("没有匹配的日志（%s）。这说明该时段没有此级别的日志，不是查询失败；"+
		"重复查询不会有不同结果，可以放宽 level 或 since。", scope), nil
}
```

返回内容里带上实际的查询范围（服务、时间段、级别），模型就能核对"我查的是不是我想查的"。上一篇里"日志查询返回空，模型换个措辞又查一次"的问题，用重复检测和预算只能止损，在工具层把空结果说清楚，才能让它不发生。

## 错误：告诉模型下一步做什么

上一篇的循环把所有工具错误一视同仁：错误文本交给模型，连续几轮全部失败就终止。这在一个场景下会出问题：

模型第一轮传了 `since: "1d"`，第二轮改成 `"yesterday"`，第三轮改成 `"24 hours"`。三轮全部失败，循环以 `tool_failures` 终止。可实际上日志服务好好的，模型只差一步就能传对。

问题在于"失败"有不同的种类，对应的下一步完全不同：

| 错误类型 | 例子 | 模型该做什么 | 计入连续失败 |
|---|---|---|---|
| invalid_args | `since` 格式不对 | 按提示改参数 | 否 |
| not_found | 服务名不存在 | 换一个对象 | 否 |
| unavailable | 日志服务连不上、超时 | 重试意义不大，换工具或结束 | 是 |
| denied | 副本数超出允许范围 | 不要再试，交给人 | 否 |

只有 `unavailable` 表示依赖本身出了问题，连续出现才说明该停了。其他三种是模型自己可以纠正的，或者是明确不该再试的。

工具用一个结构化的错误类型来表达这些信息：

```go
type ErrorKind string

const (
	ErrInvalidArgs ErrorKind = "invalid_args" // 参数不对：改参数再试
	ErrNotFound    ErrorKind = "not_found"    // 对象不存在：换个对象
	ErrUnavailable ErrorKind = "unavailable"  // 依赖不可用：重试意义不大
	ErrDenied      ErrorKind = "denied"       // 不允许：别再试了
)

type ToolError struct {
	Kind ErrorKind
	Msg  string // 发生了什么
	Hint string // 模型下一步可以怎么做
}

func (e *ToolError) Error() string {
	if e.Hint == "" {
		return fmt.Sprintf("[%s] %s", e.Kind, e.Msg)
	}
	return fmt.Sprintf("[%s] %s\n提示：%s", e.Kind, e.Msg, e.Hint)
}
```

`Hint` 是这个类型里最重要的字段。对比两条错误信息：

```
invalid duration "yesterday"
```

```
[invalid_args] since="yesterday" 无法识别
提示：使用 15m、2h 这样的相对时间，最长 24h
```

前者是写给程序员的，程序员会去查文档；后者是写给模型的，它不会查文档，所以错误信息里要直接给出正确的写法。`not_found` 同理，服务名写错时，把相近的服务名列出来：

```go
if !slices.Contains(t.Store.Services(), args.Service) {
	return "", &ToolError{Kind: ErrNotFound,
		Msg:  fmt.Sprintf("没有名为 %q 的服务", args.Service),
		Hint: "相近的服务：" + strings.Join(similar(args.Service, t.Store.Services()), ", ")}
}
```

没有被分类的错误，比如日志服务返回的 `connection refused`，一律当作 `unavailable`。这样新接入的工具即使没有仔细处理错误，行为也和上一篇一致，不会因为分类缺失而无限重试：

```go
func kindOf(err error) ErrorKind {
	var te *ToolError
	if errors.As(err, &te) {
		return te.Kind
	}
	return ErrUnavailable // 没分类的错误，按依赖故障处理
}
```

循环里只改一处：`execute` 返回的不再是"是否全部失败"，而是"是否全部因依赖不可用而失败"。

## 副作用：读和写区别对待

到目前为止讨论的都是只读工具。排查 Agent 最终可能需要动手：扩容、重启。写操作带来两个新问题。

### 只读的调用可以并行

模型经常在一轮里发出多个工具调用，比如同时查 `api` 和 `payment` 两个服务的日志。上一篇的循环串行执行它们，这对只读调用是没必要的等待。

`ToolSpec.ReadOnly` 就是为此加的。一轮里的调用全部是只读的，就并行执行；只要有一个写操作，就整轮按模型给出的顺序串行执行：

```go
func (a *Agent) execute(ctx context.Context, calls []ToolCall) ([]ToolResult, bool) {
	results := make([]ToolResult, len(calls))
	kinds := make([]ErrorKind, len(calls))
	run := func(i int) {
		out, err := a.callTool(ctx, calls[i])
		if err != nil {
			out, kinds[i] = err.Error(), kindOf(err)
		}
		results[i] = ToolResult{CallID: calls[i].ID, Content: out, IsError: err != nil}
	}

	if a.readOnly(calls) {
		var wg sync.WaitGroup
		for i := range calls {
			wg.Go(func() { run(i) })
		}
		wg.Wait()
	} else {
		for i := range calls {
			run(i) // 有副作用的调用按模型给出的顺序串行执行
		}
	}

	unavailable := len(calls) > 0
	for _, k := range kinds {
		if k != ErrUnavailable {
			unavailable = false
		}
	}
	return results, unavailable
}
```

`ReadOnly` 默认是 `false`。忘了标注的工具会被当作写操作串行执行，慢一点，但不会出错。反过来的默认值则意味着一个漏标的写操作可能和别的调用并发执行。

这也是前面说读和写必须拆成两个工具的原因：一个 `action` 参数可读可写的工具，Harness 无法在执行前判断它的性质，只能按最保守的方式处理。

### 写操作要能安全地重复执行

上一篇留了一个问题：每轮结束时持久化 `Messages`，进程崩溃后就能从最后一轮继续。但如果崩溃发生在工具执行之后、结果写入之前，恢复时这个工具会被再执行一次。对查日志无所谓，对重启服务就是重启两次。

第一种办法是**把命令式的操作改成声明式**。"扩容 3 个副本"重复执行就是扩 6 个，"把副本数设置为 6"重复执行多少次结果都一样：

```go
func (ScaleService) Spec() ToolSpec {
	return ToolSpec{
		Name: "scale_service",
		Description: `把服务的副本数设置为指定值。这是写操作，会真实影响线上。
replicas 是目标值，不是增量：用同样的参数重复调用，结果不变。
只在确认是容量问题（CPU 或连接数打满）后使用，排查阶段不要调用。`,
		// ...
	}
}
```

实现上先读当前值，相同就直接返回"已经是 6 个副本，未做变更"。这句话对模型也有用：它知道这次调用没有产生任何效果，而不是以为又扩了一次。

有些操作天然不是声明式的，重启就是。这时用**幂等键**：同一个工具调用只执行一次。键从哪来？模型 API 给每个工具调用分配了 ID，这个 ID 随 assistant 消息一起持久化，从历史恢复时重放的是同一条消息，ID 不变。所以 Harness 把它放进 context 传给工具：

```go
func (a *Agent) callTool(ctx context.Context, c ToolCall) (string, error) {
	// ...
	ctx = context.WithValue(ctx, callIDKey{}, c.ID)
	// ...
}
```

工具用它查询变更记录，执行过就直接返回上次的结果：

```go
func (t RestartService) Call(ctx context.Context, raw json.RawMessage) (string, error) {
	// ... 解析参数
	key := "restart:" + CallID(ctx)
	if out, ok, err := t.Changes.Lookup(ctx, key); err != nil {
		return "", err
	} else if ok {
		return out, nil // 同一个调用被重放：返回上次的结果，不再重启
	}
	if err := t.Deploy.Restart(ctx, args.Service); err != nil {
		return "", err
	}
	out := fmt.Sprintf("%s 已触发滚动重启（变更记录 %s）", args.Service, key)
	return out, t.Changes.Record(ctx, key, out)
}
```

这里有三个细节：

- **持久化的时机。** 这个方案依赖调用 ID 在恢复前后保持一致，所以 assistant 消息必须在**执行工具之前**持久化。如果等工具执行完再一起写入，崩溃后模型会重新生成这一轮，得到一个新 ID，幂等键就失效了。
- **变更记录必须是持久化的。** 放在进程内存里的 map 随崩溃一起消失，等于没有。
- **仍然有一个窗口。** `Restart` 成功之后、`Record` 之前崩溃，恢复时还是会重启第二次。彻底消除这个窗口，需要下游系统本身接受幂等键，比如把 key 作为部署系统变更单的 ID，由它去重。工具层的变更记录只是把窗口缩小到两次调用之间。

### 限制写在代码里，不写在描述里

`scale_service` 的描述里可以写"副本数不要超过 10"，但这只是建议，模型可能不听。真正的限制要在工具里检查，超出时返回 `denied`：

```go
if args.Replicas < 1 || args.Replicas > t.Max {
	return "", &ToolError{Kind: ErrDenied,
		Msg:  fmt.Sprintf("replicas=%d 超出允许范围 1–%d", args.Replicas, t.Max),
		Hint: "超过上限需要人工处理，请在结论里写明建议的副本数"}
}
```

描述是给模型的引导，代码是最后一道防线，两者不能互相替代。`Hint` 在这里告诉模型被拒绝之后该做什么：不是换个数字再试，而是把建议写进结论交给人。至于哪些写操作需要人工确认后才能执行，那是权限设计的问题，本文不展开。

## 测试

上一篇的脚本化模型在这里继续可用。本文新增的测试覆盖三类行为。

第一类是错误信息本身：`since` 格式错误时，错误里要包含正确写法的示例；服务名写错时，要列出相近的服务。这类测试看起来像在测字符串，其实测的是"模型能不能从这条错误里学会下一步"。

第二类是错误分类对循环的影响。开头那个场景，连续三轮参数错误、第四轮改对，循环必须正常完成：

```go
func TestInvalidArgsDoNotStop(t *testing.T) {
	m := &scriptedModel{script: []Response{
		toolUse("search_logs", `{"service":"api","since":"1d"}`),
		toolUse("search_logs", `{"service":"api","since":"yesterday"}`),
		toolUse("search_logs", `{"service":"api","since":"24 hours"}`),
		toolUse("search_logs", `{"service":"api","since":"24h"}`),
		answer("done"),
	}}
	r := newAgent(m, search()).Run(context.Background(), nil)
	if r.Stop != StopCompleted || r.Turns != 5 {
		t.Fatalf("got %s after %d turns", r.Stop, r.Turns)
	}
}
```

而 `connection refused` 连续三轮，仍然以 `tool_failures` 终止。

第三类是副作用。从历史恢复时同一个调用被重放，服务只能重启一次：

```go
func TestRestartReplay(t *testing.T) {
	d := &fakeDeploy{}
	tool := RestartService{Deploy: d, Changes: memChangeLog{}}
	call := ToolCall{ID: "toolu_01", Name: "restart_service",
		Args: json.RawMessage(`{"service":"api","reason":"连接池泄漏"}`)}
	a := newAgent(nil, tool)
	a.execute(context.Background(), []ToolCall{call})
	a.execute(context.Background(), []ToolCall{call}) // 崩溃后恢复，重放同一个调用
	if d.restarts != 1 {
		t.Fatalf("restarted %d times", d.restarts)
	}
}
```

还有两个测试分别确认只读调用确实并行执行、混有写操作的一轮按顺序串行执行。

这些测试保证的是工具的行为符合设计，但不能保证设计本身对模型有效。描述写得清不清楚、摘要的粒度合不合适，最终要看模型在真实任务中的调用轨迹：它有没有在第一次就传对参数，有没有用上下钻，有没有在空结果后停止重查。怎样系统地收集和评估这些轨迹，是第 4、5 篇的内容。

## 小结

把工具接口从"为程序员设计"改成"为模型设计"，核心是承认模型的几个限制：它只看得到描述，不会去查文档；它不知道你没告诉它的事；它读到的每个字节都要占上下文；它遇到错误只能靠错误文本决定下一步。

对照这几点，设计一个工具时可以逐项检查：

1. **粒度**：模型是否总是连续调用某几个工具？是的话合并。读和写是否在同一个工具里？是的话拆开。
2. **参数**：有没有要求模型提供它不知道的信息，比如当前时间？能用枚举的是否用了枚举？最常见的用法是否只需要一两个参数？
3. **描述**：是否写了什么时候用、什么时候不用、做不到时用什么？
4. **返回值**：是否经过聚合或摘要？截断和空结果是否明说？是否带上了实际的查询范围？
5. **错误**：是否区分了类型？是否告诉模型下一步怎么做？
6. **副作用**：是否标注了只读？写操作能否安全地重复执行？限制是否写在代码里？

本文的工具返回值都控制在几百个 token 以内，但一次排查往往要调用十几次工具，结果在消息历史里越积越多，最早的那些对当前判断已经没有用，却每一轮都要重新发给模型。下一篇讨论上下文管理：Agent 的历史什么时候该压缩，压缩时哪些信息不能丢。
