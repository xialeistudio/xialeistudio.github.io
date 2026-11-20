---
title: "The Hard Part of an Agent Loop Is Knowing When to Stop"
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

The main loop is the shortest piece of code in an agent: call the model, run the tools, call the model again. It fits in a dozen lines. Yet once an agent is in production, a large share of its problems come from those dozen lines, and they are almost always the same kind of problem: it didn't stop when it should have, or it stopped and nobody knows why.

This is the first post in the *Agent Engineering Notes* series. Using an incident-investigation agent written in Go as the running example, it takes apart every exit path of the agent loop.

<!--more-->

## The dozen-line loop

The agent loop in almost every tutorial looks like this:

```go
for {
    resp, err := model.Generate(ctx, msgs, tools)
    if err != nil {
        return "", err
    }
    msgs = append(msgs, resp.Message)
    if len(resp.Message.ToolCalls) == 0 {
        return resp.Message.Content, nil // no more tool calls means we're done
    }
    for _, call := range resp.Message.ToolCalls {
        out, _ := tools[call.Name].Call(ctx, call.Args)
        msgs = append(msgs, toolResult(call.ID, out))
    }
}
```

It works fine in a demo. In a real environment, you run into things like this:

- A log query comes back empty. The model rephrases and queries again, still empty, and again... until the tokens run out.
- The log service is down, the tool returns `connection refused`, and the model retries the same call every turn.
- The model's output is cut off by `max_tokens`, the tool arguments are half a JSON object, and the loop executes them anyway.
- The user clicks "Stop", but the loop only notices after the current tool finishes and the model replies one more time.
- The loop finally exits, and the caller gets a block of text with no way to tell "investigation complete" from "half-finished work when the budget ran out".

What these have in common: the loop has one exit (the model stops calling tools), while reality has at least eight.

## Two kinds of "stop"

The first step is to separate two concepts that are often conflated:

- **FinishReason**: why the model stopped generating *this turn*. Returned by the model API, usually `end_turn`, `tool_use` or `max_tokens`.
- **StopReason**: why the agent ended *this task*. Decided by the harness, and the output of the loop.

The first is one of the inputs; the second is what the caller actually cares about. The tutorial loop's problem is that it uses a single value of FinishReason to decide the StopReason directly.

In the implementation, StopReason should be an explicit enum, not something hidden in an error or the returned text:

```go
type StopReason string

const (
	StopCompleted    StopReason = "completed"     // model ended on its own
	StopMaxTurns     StopReason = "max_turns"     // out of turns
	StopTokenBudget  StopReason = "token_budget"  // out of tokens
	StopRepeatedCall StopReason = "repeated_call" // same call repeated back to back
	StopToolFailures StopReason = "tool_failures" // tools kept failing
	StopTruncated    StopReason = "truncated"     // model output was cut off
	StopCanceled     StopReason = "canceled"      // external cancel or timeout
	StopModelError   StopReason = "model_error"   // the model call itself failed
)
```

When designing a loop, write this table first, then the `for`. Every value in the enum maps to a specific checkpoint in the loop.

## The exit paths, one by one

The code below uses a minimal set of types: a `Model` interface with a single `Generate` method, and a `Tool` interface with `Spec` and `Call`. Which model SDK sits behind them doesn't affect the design of the loop, so I won't go into it.

### The model says it's done

```go
case FinishEndTurn:
    return done(StopCompleted, turn, nil)
```

This is the only "normal" exit, but be careful about what it means: **the model thinks it's done**, which is not the same as the task being done. The model may have looked at one log line and drawn a conclusion, or simply replied "I can't access the logging system".

What the harness can do is label it honestly: StopCompleted only means "the model ended on its own". Whether the task actually succeeded is for the caller or an evaluation system to judge, which is the subject of part 5.

### Truncated output

```go
case FinishMaxTokens:
    // tool arguments in truncated output may be half a JSON object; never execute them
    return done(StopTruncated, turn, nil)
```

Truncation is easy to overlook because most of the time it doesn't happen. When it does, the consequences can be serious: whether `{"svc":"ap` parses depends on the tool's implementation, and in the worst case a lenient parser completes it into a wrong call.

Here the loop simply terminates. The alternative is to raise `max_tokens` and have the model regenerate. Either way, the rule is: **never execute a truncated tool call**.

### Running out of budget

```go
if turn > a.Limits.MaxTurns {
    return done(StopMaxTurns, turn-1, nil)
}
if a.Limits.TokenBudget > 0 && usage.Total() >= a.Limits.TokenBudget {
    return done(StopTokenBudget, turn-1, nil)
}
```

Both checks go **before** the model call. Put them after, and the last call has already been paid for, only for its result to be thrown away.

Limit turns and tokens together. With only a turn limit, a long-context task can burn hundreds of thousands of tokens in ten turns. With only a token limit, cheap short calls can loop forever.

The limits shouldn't be guesses. Start with loose limits, measure how many turns and tokens normal tasks actually use, then pick a value a bit above P99. That takes observability, which part 4 covers.

### Going in circles

This is the most common and most wasteful case: the model gets a result it doesn't like and makes the same call with the same arguments, hoping for a different answer.

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

`callsKey` concatenates the names and arguments of every tool call in a turn into one string. One detail: run the arguments through `json.Compact` first, or `{"svc":"api"}` and `{"svc": "api"}` count as different calls. Often all the model changed was whitespace; the meaning is identical.

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

This detects **consecutive** repeats, not "seen before". Some calls are supposed to repeat, such as polling a service's status after a deploy: with other calls in between, repetition is reasonable. Three identical calls in a row is a fairly reliable sign of going in circles.

It only catches exact repeats. If the model changes the query from `timeout` to `time out` to `timed out`, it's semantically going in circles too, but the strings differ. That case is caught by the budget limits from the previous section; there's no need for semantic judgment inside the loop.

### Tool failures

Tool failures are different from the cases above: **a single failure should not end the loop**.

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

Return the error to the model as a tool result (`IsError: true`) rather than swallowing it in the harness or panicking. After seeing "argument `since` is malformed, expected RFC3339", the model usually gets it right on the next turn. This is where agents are more resilient than traditional programs, and the loop's error handling shouldn't throw that away.

Only **several consecutive turns where every call failed** end the loop. That usually means the dependency itself is unavailable, and further retries are waste.

Two more failure sources are easy to miss:

```go
func (a *Agent) callTool(ctx context.Context, c ToolCall) (string, error) {
	t, ok := a.Tools[c.Name]
	if !ok {
		// the model hallucinated a tool: tell it what exists instead of crashing
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

- **The model calls a tool that doesn't exist**: the tutorial code hits a nil pointer panic here. The right move is to return the list of available tools as the error.
- **A tool hangs**: every tool call needs its own timeout. One stuck query shouldn't stall the whole agent. Make the timeout message explicit so the model can decide between "try different arguments" and "try a different tool".

### External cancellation

```go
if err := ctx.Err(); err != nil {
	return done(StopCanceled, turn-1, err)
}
```

The cancellation signal has to flow all the way down from the entry point: check it at the start of every turn, and pass the same `ctx` to both `Generate` and `Tool.Call`. Then whether the user clicks Stop during generation or during a tool call, the loop exits as soon as the current operation returns, without running another turn.

There's a problem this post won't cover: when cancellation happens, a tool may already have had a side effect, like restarting a service. "Able to stop" and "consistent state after stopping" are different things. The latter depends on whether the tools are idempotent, which part 2 picks up when discussing tool design.

## The full loop

Putting the checkpoints together:

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
		// 1. external cancellation
		if err := ctx.Err(); err != nil {
			return done(StopCanceled, turn-1, err)
		}
		// 2. budget checks, before calling the model
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

		// 3. repeated-call detection
		key := callsKey(resp.Message.ToolCalls)
		if key == lastKey {
			repeats++
		} else {
			lastKey, repeats = key, 1
		}
		if a.Limits.MaxRepeats > 0 && repeats > a.Limits.MaxRepeats {
			return done(StopRepeatedCall, turn, nil)
		}

		// 4. run tools; errors go to the model, only consecutive failures stop the loop
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

Only two lines in the loop body actually do work: `Generate` and `execute`. Everything else answers one question: should we stop now?

## After stopping

When the loop ends, it returns a struct, not a string:

```go
type Result struct {
	Stop     StopReason
	Final    string    // last assistant text, may be empty
	Messages []Message // full history, for auditing, recovery or resuming
	Turns    int
	Usage    Usage
	Err      error
}
```

The caller decides what to do next based on `Stop`, and different stop reasons call for completely different handling:

| StopReason | Meaning | Typical caller handling |
|---|---|---|
| completed | Model ended on its own | Show the conclusion; let evaluation judge quality |
| max_turns / token_budget | Task was harder than expected | Show progress so far; ask whether to add budget and resume |
| repeated_call | Model got stuck in a loop | Record as a failure case for the eval set |
| tool_failures | A dependency is unavailable | Alert; tell the user to check the dependency |
| truncated | Output too long | Adjust `max_tokens` or split the task |
| canceled | User stopped it | No error; keep the history |
| model_error | Model service failure | Treat as any downstream outage: retry or switch models |

This table is the contract between the agent and its caller. Without it, the caller has to guess from the text.

Two practices are worth adding:

**A wrap-up turn.** If you return as soon as the budget runs out, `Final` might be "let me check the database next" from turn 6, which means nothing to the user. A better approach is to call the model once more before terminating, **with all tools disabled**, and have it summarize what it found and what's left. Reserve a separate budget for this turn rather than counting it against the main budget, or the two will compete.

**Resuming from history.** `Messages` is the agent's entire state. Persist it at the end of every turn, and after a crash you can continue from the last turn; for the user, this is "add budget and resume". The one thing to watch is the last turn: if the crash happens after a tool ran but before its result was written, that tool runs again on recovery. Which brings us back to idempotency.

## Testing every exit path

Exit paths are hard to reproduce in production: you can't make a real model "happen" to repeat the same call three times. That's why `Model` is an interface; tests use a fake model that follows a script:

```go
type scriptedModel struct {
	script []Response
	i      int
}

func (m *scriptedModel) Generate(ctx context.Context, _ []Message, _ []ToolSpec) (Response, error) {
	if err := ctx.Err(); err != nil {
		return Response{}, err
	}
	r := m.script[min(m.i, len(m.script)-1)] // after the script runs out, keep repeating the last step
	m.i++
	return r, nil
}
```

One test per exit path. For repeated-call detection, confirm that arguments differing only by a space are still caught:

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

On truncation, the tool must never run:

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

If cancellation happens while a tool is running, the loop must not run another turn:

```go
func TestCanceledDuringTool(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	tool := funcTool{"query_logs", func(context.Context, json.RawMessage) (string, error) {
		cancel() // simulate the user clicking Stop mid-tool
		return "partial", nil
	}}
	r := newAgent(&scriptedModel{script: []Response{toolUse("query_logs", `{}`), answer("x")}}, tool).Run(ctx, nil)
	if r.Stop != StopCanceled || r.Turns != 1 {
		t.Fatalf("got %s after %d turns", r.Stop, r.Turns)
	}
}
```

The full implementation has 8 tests covering normal completion, repeated calls, turn exhaustion, token exhaustion, consecutive tool failures, tool timeout, truncated output, and cancellation mid-run. None of them call a real model; they finish in milliseconds and can run in CI on every commit.

## Summary

Most of the code in an agent loop isn't about doing work. It's about deciding when to stop doing work.

The tutorial loop has one exit and assumes the model will always stop on its own at the right moment. A production loop needs at least eight exits, each tied to a specific way of failing, and it has to hand the reason for stopping to the caller explicitly.

When designing an agent loop, I'd suggest this order:

1. List the StopReason enum first, writing down each value's trigger and how the caller should handle it;
2. Then write the loop, making sure every enum value has a matching checkpoint;
3. Finally, use a scripted model to write one test per exit path.

The loop in this post is deliberately simple: tools run serially, there's no wrap-up turn and no persistence. Those get filled in over the rest of the series. The next post moves to the tool layer: if tool errors are meant to be read by the model, how should tool interfaces be designed for a model rather than a person?
