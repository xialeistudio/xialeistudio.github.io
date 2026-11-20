---
title: "Agent Tools Have a New Reader: the Model"
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

The previous post on the agent loop rested on one assumption: when a tool fails, the error goes back to the model as a tool result, and the model decides what to do next. That pushes a question down to the tool layer: if what a tool returns is meant to be read by a model, how should the tool interface itself be designed?

Most agent tools are thin wrappers around existing internal APIs: same parameters, same return values, same errors. Those APIs were designed for programmers, and now the reader is a model. This is the second post in the *Agent Engineering Notes* series. Continuing with the Go incident-investigation agent, it takes a tool copied straight from an API and reworks it, step by step, into a tool designed for a model.

<!--more-->

## A different reader

Programmers and models use the same interface in very different ways:

| | Programmer | Model |
|---|---|---|
| Learning the interface | Reads the docs once and remembers | Sees only the name, description and parameter schema, every time |
| Handling the response | Code picks out the fields it needs | Every byte enters the context, costs tokens and competes for attention |
| Hitting an error | Opens the logs, sets a breakpoint | Can only guess the next call from the error text |
| Missing information | Looks it up | Doesn't look it up; makes something up |

The last row is the most underestimated. Take "the current time": a programmer calling an API naturally knows what time it is. A model doesn't, unless you tell it in the context. An interface that requires an absolute timestamp is, for a model, an invitation to invent one.

## Starting point: a tool copied from the API

The tool an investigation agent uses most is log search. Copy the log service's API and you get this:

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

It returns the log service's raw JSON. In a real investigation, it fails like this:

- The model doesn't know the current time, fills `start_time` with a date common in its training data, and gets nothing back.
- The time is right but the timezone is wrong, so it queries logs from eight hours off.
- It sets `limit` to 100 and gets back 100 near-identical `upstream timeout` lines: over ten thousand tokens for one useful fact.
- To see later logs it pages with `offset`, spending a turn per page.
- It sets `level` to `ERROR`, the log service only accepts lowercase, and the result is empty.
- When the result is empty, the model can't tell "there really is nothing" from "I queried wrong", so it tries different arguments and falls into the circling described in the previous post.

None of these happen because the model "isn't smart enough". The interface gives the model too many chances to get it wrong, and when it does, doesn't give it enough information to correct itself.

## Granularity: cut by question, not by endpoint

Copying APIs has another consequence: too many tools, too fine-grained. The log service has query, stats and context endpoints; Kubernetes has pods, events and logs. So the agent ends up with six tools, and the model has to learn on its own to "list pods, get logs for each pod, then check events".

Every extra step in the chain is another model turn and another chance to get it wrong. A better cut starts from the questions the agent needs to answer:

- "What went wrong in this window, and what's most common?" → `search_logs`
- "What state is this service in right now?" → `inspect_service`, which merges pods, events and recent deploys into one summary internally
- "How has this metric been trending?" → `query_metrics`

The test is simple: if the model almost always calls A and then B, A and B should be one tool. Conversely, a tool that switches between completely different behaviors based on a parameter, like `action: "query" | "restart" | "delete"`, should be split. Reads and writes in particular must be split, for reasons covered in the "Side effects" section below.

## Parameters: make them hard to get wrong

The reworked `search_logs`:

```go
func (SearchLogs) Spec() ToolSpec {
	return ToolSpec{
		Name: "search_logs",
		Description: `Search logs by service and time range. Returns a summary grouped by pattern, not raw logs.
Use it to answer "what went wrong in this window, and which errors are most common".
To see raw logs for one kind of error, pass its pattern from the summary back unchanged.
Only covers the last 24 hours; for older data, use query_metrics to look at trends.`,
		Parameters: json.RawMessage(`{
  "type": "object",
  "properties": {
    "service": {"type": "string", "description": "Service name, e.g. api, payment"},
    "since":   {"type": "string", "description": "How far back to look, e.g. 15m, 2h; at most 24h", "default": "15m"},
    "level":   {"type": "string", "enum": ["error", "warn", "info"], "default": "error"},
    "pattern": {"type": "string", "description": "Optional. Only return raw logs for this pattern, taken from a previous summary"}
  },
  "required": ["service"]
}`),
		ReadOnly: true,
	}
}
```

Compared with the original, every change aims at the same thing: reducing what the model needs to "know".

- **Relative time instead of absolute time.** `since: "15m"` doesn't require knowing the current time, and has no timezone problem. The tool has an accurate clock; let it do the conversion.
- **Enums instead of free strings.** `level` has three values, so case problems disappear.
- **Defaults cover the most common use.** The most common investigation question is "what errors happened in the last 15 minutes", which now needs just one parameter, `service`. The fewer required parameters, the fewer chances to pass something wrong.
- **No pagination parameters.** `limit` and `offset` exist to control response size, and that's the tool's job. More in the next section.

`ToolSpec` gained a `ReadOnly` field. It's tagged `json:"-"`, so it's never sent to the model; it's for the harness only, also covered below.

## Descriptions: say when to use it

The tool description is the model's only way to learn about the tool, and a description like `"Query logs."` says nothing. The description above answers four questions:

1. **What it does**: searches logs and returns a grouped summary.
2. **When to use it**: to find out what went wrong and which errors dominate.
3. **How it fits with other calls**: to see raw logs, pass the pattern back.
4. **What it can't do, and what to use instead**: only 24 hours; for older data, use `query_metrics`.

Point 4 is often left out, but it does the most to cut wasted calls. A model that doesn't know a tool's limits will probe them: pass `since: "7d"`, fail, try `"72h"`, fail again. State the limit and the alternative in the description, and those turns disappear.

Descriptions don't need to be short. They're sent to the model every turn and do cost tokens, but compared with the cost of one wrong call, a few extra sentences are cheap.

## Responses: design for the context budget

The original tool returned 100 raw log lines. The reworked one returns a summary grouped by pattern:

```
api, 14:00–14:15, level>=error: 4312 lines, 7 patterns:
  3870× upstream timeout after <N>ms (host=db-<N>) (first seen 14:02:11)
   402× connection pool exhausted, waiting <N>ms (first seen 14:02:13)
    23× order <N> not found (first seen 14:00:42)
     9× retry budget exceeded for /v1/charge (first seen 14:05:30)
     4× slow query: <N>ms (first seen 14:03:01)
2 more patterns (4 lines) not shown.
```

In a few hundred tokens, the model sees the whole picture: errors started at 14:02, mostly downstream database timeouts, followed by connection pool exhaustion. That's exactly what the investigation needs, whereas 100 raw lines would most likely contain only the first pattern.

The grouping is simple: replace numbers and hex IDs with placeholders, and lines of the same kind become the same string.

```go
// Replace numbers and hex IDs with placeholders so lines of the same kind group together.
var noise = regexp.MustCompile(`\b[0-9a-f]{8,}\b|\d+`)

func patternOf(msg string) string { return noise.ReplaceAllString(msg, "<N>") }
```

Then count by pattern, sort, output the top 5, and add one line saying "N more patterns (M lines) not shown".

Grouping has a cost: `host=db-<N>` also erases which database it was, and if only `db-2` is having trouble, that's precisely the key fact. So the tool keeps a drill-down path. Pass the pattern back unchanged, and the model gets the raw lines for that group:

```
api, 14:00–14:15, level>=error, pattern "upstream timeout after <N>ms (host=db-<N>)": 3870 lines, showing the earliest 20:
14:02:11 upstream timeout after 3000ms (host=db-2)
14:02:11 upstream timeout after 3001ms (host=db-2)
...
```

One rule deserves its own emphasis: **truncation must be stated**. With "3870 lines, showing the earliest 20", the model knows it's seeing a slice. If the tool quietly returns 20 lines, the model assumes that's everything and draws conclusions from incomplete data.

Empty results need to be stated too. The original tool returned `[]`, and the model couldn't tell "no logs" from "wrong query". The reworked version:

```go
if len(lines) == 0 {
	return fmt.Sprintf("No matching logs (%s). This means there were no logs at this level in the window; "+
		"the query did not fail. Repeating it won't change the result; try a broader level or since.", scope), nil
}
```

Including the actual query scope (service, window, level) in the response lets the model check that it queried what it meant to. The previous post's "empty log result, model rephrases and queries again" problem can only be contained by repeat detection and budgets. Making empty results explicit at the tool layer keeps it from happening at all.

## Errors: tell the model what to do next

The previous post's loop treated all tool errors the same: the error text goes to the model, and several consecutive turns of total failure end the loop. That breaks in one scenario:

On turn one the model passes `since: "1d"`, on turn two `"yesterday"`, on turn three `"24 hours"`. All three fail, and the loop ends with `tool_failures`. Yet the log service is perfectly healthy, and the model was one step away from getting it right.

The problem is that failures come in different kinds, with completely different next steps:

| Error kind | Example | What the model should do | Counts toward consecutive failures |
|---|---|---|---|
| invalid_args | `since` is malformed | Fix the arguments as hinted | No |
| not_found | Service name doesn't exist | Try a different target | No |
| unavailable | Log service unreachable or timing out | Retrying won't help; switch tools or finish | Yes |
| denied | Replica count outside the allowed range | Don't retry; hand it to a human | No |

Only `unavailable` means the dependency itself is broken, and only repeated occurrences of it mean it's time to stop. The other three are either correctable by the model or clearly not worth retrying.

The tool expresses this with a structured error type:

```go
type ErrorKind string

const (
	ErrInvalidArgs ErrorKind = "invalid_args" // bad arguments: fix and retry
	ErrNotFound    ErrorKind = "not_found"    // target doesn't exist: try another
	ErrUnavailable ErrorKind = "unavailable"  // dependency down: retrying won't help
	ErrDenied      ErrorKind = "denied"       // not allowed: stop trying
)

type ToolError struct {
	Kind ErrorKind
	Msg  string // what happened
	Hint string // what the model can do next
}

func (e *ToolError) Error() string {
	if e.Hint == "" {
		return fmt.Sprintf("[%s] %s", e.Kind, e.Msg)
	}
	return fmt.Sprintf("[%s] %s\nHint: %s", e.Kind, e.Msg, e.Hint)
}
```

`Hint` is the most important field in this type. Compare two error messages:

```
invalid duration "yesterday"
```

```
[invalid_args] since="yesterday" is not recognized
Hint: use a relative duration like 15m or 2h, at most 24h
```

The first is written for a programmer, who will go read the docs. The second is written for a model, which won't, so the error itself has to show the correct form. Same for `not_found`: when the service name is wrong, list similar names:

```go
if !slices.Contains(t.Store.Services(), args.Service) {
	return "", &ToolError{Kind: ErrNotFound,
		Msg:  fmt.Sprintf("no service named %q", args.Service),
		Hint: "similar services: " + strings.Join(similar(args.Service, t.Store.Services()), ", ")}
}
```

Unclassified errors, such as `connection refused` from the log service, are all treated as `unavailable`. That way a newly added tool that doesn't handle errors carefully still behaves like the previous post's loop, rather than retrying forever because a classification is missing:

```go
func kindOf(err error) ErrorKind {
	var te *ToolError
	if errors.As(err, &te) {
		return te.Kind
	}
	return ErrUnavailable // unclassified errors are treated as dependency failures
}
```

The loop changes in only one place: instead of "did every call fail", `execute` now returns "did every call fail because a dependency was unavailable".

## Side effects: treat reads and writes differently

So far everything has been read-only. An investigation agent may eventually need to act: scale up, restart. Write operations bring two new problems.

### Read-only calls can run in parallel

Models often issue several tool calls in one turn, such as searching logs for both `api` and `payment`. The previous post's loop ran them serially, which is unnecessary waiting for read-only calls.

That's what `ToolSpec.ReadOnly` is for. If every call in a turn is read-only, they run in parallel; if even one is a write, the whole turn runs serially in the order the model gave:

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
			run(i) // calls with side effects run serially, in the order the model gave
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

`ReadOnly` defaults to `false`. A tool someone forgot to mark is treated as a write and runs serially: a bit slower, but never wrong. The opposite default would mean an unmarked write could run concurrently with other calls.

This is also why reads and writes must be separate tools: a tool whose `action` parameter can mean either read or write can't be classified by the harness before it runs, so it can only be handled the most conservative way.

### Writes must be safe to repeat

The previous post left a problem open: persist `Messages` at the end of each turn, and after a crash you can continue from the last turn. But if the crash happens after a tool ran and before its result was written, that tool runs again on recovery. For a log search, no harm done. For a service restart, that's two restarts.

The first fix is to **turn imperative operations into declarative ones**. "Add 3 replicas" run twice adds 6; "set replicas to 6" gives the same result no matter how many times it runs:

```go
func (ScaleService) Spec() ToolSpec {
	return ToolSpec{
		Name: "scale_service",
		Description: `Set the service's replica count to the given value. This is a write and affects production.
replicas is the target, not an increment: repeating the call with the same arguments changes nothing.
Only use after confirming a capacity problem (CPU or connections maxed out); do not call during investigation.`,
		// ...
	}
}
```

The implementation reads the current value first, and if it already matches, returns "already at 6 replicas, no change made". That sentence helps the model too: it knows the call had no effect, instead of believing it scaled again.

Some operations are inherently not declarative; restart is one. For those, use an **idempotency key**: the same tool call executes only once. Where does the key come from? The model API assigns every tool call an ID. That ID is persisted with the assistant message, and when recovering from history, the same message is replayed with the same ID. So the harness passes it to the tool through the context:

```go
func (a *Agent) callTool(ctx context.Context, c ToolCall) (string, error) {
	// ...
	ctx = context.WithValue(ctx, callIDKey{}, c.ID)
	// ...
}
```

The tool checks its change log with it, and if the call already ran, returns the previous result:

```go
func (t RestartService) Call(ctx context.Context, raw json.RawMessage) (string, error) {
	// ... parse arguments
	key := "restart:" + CallID(ctx)
	if out, ok, err := t.Changes.Lookup(ctx, key); err != nil {
		return "", err
	} else if ok {
		return out, nil // same call replayed: return the previous result, don't restart again
	}
	if err := t.Deploy.Restart(ctx, args.Service); err != nil {
		return "", err
	}
	out := fmt.Sprintf("rolling restart triggered for %s (change record %s)", args.Service, key)
	return out, t.Changes.Record(ctx, key, out)
}
```

Three details matter here:

- **When to persist.** This scheme relies on the call ID being the same before and after recovery, so the assistant message must be persisted **before the tool runs**. If you wait and write it together with the tool result, after a crash the model regenerates the turn with a new ID, and the idempotency key is useless.
- **The change log must be durable.** An in-memory map disappears with the crash, which is the same as having nothing.
- **A window remains.** A crash after `Restart` succeeds but before `Record` still causes a second restart on recovery. Closing that window completely requires the downstream system to accept the idempotency key itself, for example by using the key as the deploy system's change ticket ID and letting it deduplicate. The tool-level change log only shrinks the window to the gap between two calls.

### Limits belong in code, not in the description

`scale_service`'s description can say "don't exceed 10 replicas", but that's only advice, and the model may ignore it. The real limit has to be checked in the tool, returning `denied` when exceeded:

```go
if args.Replicas < 1 || args.Replicas > t.Max {
	return "", &ToolError{Kind: ErrDenied,
		Msg:  fmt.Sprintf("replicas=%d is outside the allowed range 1–%d", args.Replicas, t.Max),
		Hint: "going above the limit requires a human; state the recommended replica count in your conclusion"}
}
```

The description guides the model; the code is the last line of defense. Neither replaces the other. Here `Hint` tells the model what to do after being denied: not try another number, but write the recommendation into its conclusion for a human. Which writes need human approval before they run is a permissions question, outside the scope of this post.

## Testing

The scripted model from the previous post still works here. The new tests cover three kinds of behavior.

First, the error messages themselves: when `since` is malformed, the error must include an example of the correct form; when the service name is wrong, it must list similar services. These look like string tests, but what they really test is "can the model learn its next step from this error".

Second, how error kinds affect the loop. In the opening scenario, three turns of bad arguments followed by a correct fourth must end with normal completion:

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

Meanwhile, three consecutive turns of `connection refused` still end with `tool_failures`.

Third, side effects. When the same call is replayed during recovery from history, the service must restart only once:

```go
func TestRestartReplay(t *testing.T) {
	d := &fakeDeploy{}
	tool := RestartService{Deploy: d, Changes: memChangeLog{}}
	call := ToolCall{ID: "toolu_01", Name: "restart_service",
		Args: json.RawMessage(`{"service":"api","reason":"connection pool leak"}`)}
	a := newAgent(nil, tool)
	a.execute(context.Background(), []ToolCall{call})
	a.execute(context.Background(), []ToolCall{call}) // recover after a crash and replay the same call
	if d.restarts != 1 {
		t.Fatalf("restarted %d times", d.restarts)
	}
}
```

Two more tests confirm that read-only calls really run in parallel and that a turn containing a write runs serially in order.

These tests guarantee the tools behave as designed, but not that the design actually works for the model. Whether the descriptions are clear and the summaries are at the right granularity ultimately shows up in the model's call traces on real tasks: did it pass the right arguments the first time, did it use the drill-down, did it stop re-querying after an empty result. How to collect and evaluate those traces systematically is the subject of parts 4 and 5.

## Summary

Redesigning a tool interface from "for programmers" to "for models" comes down to accepting a few of the model's limits: it only sees the description and won't read docs; it doesn't know what you haven't told it; every byte it reads takes up context; and when it hits an error, the error text is all it has to decide what's next.

With those in mind, here's a checklist for designing a tool:

1. **Granularity**: Does the model almost always call certain tools back to back? Merge them. Are reads and writes in the same tool? Split them.
2. **Parameters**: Does it ask the model for information it doesn't have, like the current time? Are enums used wherever possible? Does the most common use need only one or two parameters?
3. **Description**: Does it say when to use it, when not to, and what to use when it can't help?
4. **Response**: Is it grouped or summarized? Are truncation and empty results stated? Does it include the actual query scope?
5. **Errors**: Are kinds distinguished? Does it tell the model what to do next?
6. **Side effects**: Is it marked read-only? Can writes be safely repeated? Are limits enforced in code?

The tool responses in this post stay within a few hundred tokens, but one investigation often makes a dozen or more tool calls. The results pile up in the message history, and the earliest ones are no longer useful for the current decision, yet they're sent to the model again every turn. The next post covers context management: when to compress an agent's history, and what must never be dropped.
