---
title: "An Agent's Context Is a View of Its History, Not the History Itself"
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

In the first two posts, the agent sent its entire message history to the model on every turn. One investigation makes a dozen or more tool calls. The results pile up, and the earliest ones stop being useful for the current decision, yet they get sent again every turn.

The usual fixes are "drop the oldest messages when the history gets long" or "ask the model to summarize it". Both treat the history and the context sent to the model as the same thing, so every compression becomes a trade-off between saving tokens and losing information. This is the third post in the *Agent Engineering Notes* series. Continuing with the Go incident-investigation agent, it first separates those two things, then covers when to compress, how to compress, and what must never be left to a summary. It also adds the wrap-up turn the first post promised but never built.

<!--more-->

## Long histories cause three problems

Start with the numbers. Say the system prompt and tool definitions take 3,000 tokens, and each turn adds about 1,700 tokens of model output plus tool results (the second post already kept individual tool results to somewhere between a few hundred and a couple of thousand tokens). The input for turn n is roughly:

```
3000 + 1700 × (n − 1)
```

In a 15-turn investigation, the last turn's input is about 27k tokens, and the 15 turns together use about 220k. Only around 25k of that is new information. The rest is the same content sent over and over. **Total usage grows with the square of the turn count**, so most of the token budget from the first post goes to re-sending old content.

Cost is one problem. There are two more:

- **The context window is a hard limit.** Go past it and the model API returns an error, the loop ends with `model_error`, and all the work so far is lost.
- **Stale information misleads the model.** At the start of the investigation, `inspect_service` showed three api pods in CrashLoopBackOff. The service was restarted and is now healthy, but the old result is still in the context, and on turn 12 the model may still cite it.

So the job of context management is to keep what goes to the model each turn at a steady size, without losing the information that matters.

## Separate the history from the context

The loop in the first two posts had a single `msgs` slice doing two jobs:

- **The transcript**: everything that happened. It's used for auditing, persistence, resuming, and the evaluation covered in part 5. It has to be complete, and it's append-only.
- **The context**: what gets sent to the model this turn. It should be as small as possible, holding only what the next decision needs.

When the two are mixed, compressing means editing the transcript. Whatever you cut is gone for good, and an audit can't show what the model actually saw at the time. Once they're separate, **the transcript never changes, and the context is a view derived from it on every turn**.

For an investigation that has been compressed, the transcript maps to the view like this:

| Part of the transcript | What the model gets |
|---|---|
| The task (the user's original request) | Kept verbatim |
| Early turns (say, turns 1–5) | A summary plus a log of write operations |
| Middle turns (turns 6–8) | Tool calls kept, tool results cleared |
| Recent turns (turns 9–10) | Kept verbatim |

The older the content, the harder it's compressed, with the task as the one exception. The rest of this post walks through that table row by row.

In code, the view is described by a few indices and two pieces of text:

```go
// contextState describes how the context sent to the model is derived from
// the full transcript. The transcript is append-only; compression only
// changes this view.
type contextState struct {
	head      int    // transcript[:head] is the task itself, always kept verbatim
	from      int    // transcript[head:from] has been replaced by the summary
	clearedTo int    // tool results in transcript[from:clearedTo] have been cleared
	summary   string // progress summary written by the model
	ledger    string // write operations recorded by the harness, not by the model
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

The three indices match the first three rows of the table. Everything after `from` and `clearedTo` passes through unchanged, which is the last row.

In the loop, new messages are appended to `msgs`, and the model gets `st.view(msgs)`. `Result.Messages` still returns the full transcript, so what the first post said about using it "for auditing, recovery, or resuming" still holds.

## When to compress

### Use the numbers the API gives you

The most accurate measure of context size comes from the model API itself: the `InputTokens` returned by each call is the real size of that turn's context. Add this turn's output and the new tool results, and you have the size of the next turn:

```go
usage.Add(resp.Usage)
msgs = append(msgs, resp.Message)
// The API's input token count is this turn's real context size;
// adding this turn's output gives the starting point for the next turn.
ctxTokens = resp.Usage.InputTokens + resp.Usage.OutputTokens
// ... run tools
ctxTokens += estimate([]Message{toolMsg})
```

The new tool results don't have a real count yet, so `estimate` makes a rough guess from the byte count. It only decides whether to compress, so erring high is fine: compressing a little early beats hitting the window limit.

### Check before calling the model

Like the budget checks in the first post, the context check runs before `Generate`:

```go
// Context check, also done before calling the model
if a.Context.CompactAt > 0 && ctxTokens > a.Context.CompactAt {
	u, err := a.compact(ctx, msgs, &st)
	usage.Add(u)
	if err != nil {
		return finish(stopFor(ctx, err), turn-1, err) // overflow, cancellation, or model error
	}
}
resp, err := a.Model.Generate(ctx, st.view(msgs), specs)
```

Compression may call the model too. Those tokens are added to `usage` and count against the overall budget.

### Two watermarks instead of a sliding window

The obvious approach is a sliding window that keeps only the last N turns. The problem is that the start of the context changes every turn.

Prompt caching in model APIs works by prefix matching: if this turn's context starts with the same prefix as the last turn's, that part can hit the cache, which cuts both cost and latency a lot. A sliding window drops messages from the front every turn, so the prefix keeps changing and the cache never hits.

So compression uses two watermarks:

```go
type ContextPolicy struct {
	Window     int // the model's context limit (tokens); still over it after compressing means stop
	CompactAt  int // start compressing when the context exceeds this
	CompactTo  int // compression target: if still above this after clearing tool results, summarize
	KeepTurns  int // the most recent turns are kept verbatim, never cleared or summarized
	MaxResult  int // byte limit for a single tool result; longer ones are truncated
	Summarizer Model
}
```

When the context grows to `CompactAt`, it's compressed once, down below `CompactTo`, and then left alone until it grows back to `CompactAt`. Between compressions, the context only grows at the end, the prefix stays the same, and the cache keeps hitting.

With a 200k window, `CompactAt` at 100k and `CompactTo` at 40k, the agent can run dozens of turns before the next compression. Specific values and the savings from caching come up in part 9 on cost. For now, remember: **compress in batches, not every turn**.

## Stage one: clear old tool results

Compression happens in two stages, and the cheap one comes first.

Tool results take up the most space in the context, and old ones are mostly useless by now. The model has read them, written its conclusion in a later reply ("errors start at 14:02, mostly db-2 timeouts"), and picked its next step based on that. A few turns later, the value of the raw result has moved into the model's own text.

Stage one replaces those old results with a one-line placeholder:

```go
func clearResults(m Message) Message {
	rs := make([]ToolResult, len(m.ToolResults))
	for i, r := range m.ToolResults {
		r.Content = fmt.Sprintf("[Result cleared to save context; original was %d bytes. Call the tool again if you still need it.]", len(r.Content))
		rs[i] = r
	}
	m.ToolResults = rs
	return m
}
```

Three things to note:

- **Only the result is cleared; the call stays.** `search_logs({"service":"api"})` stays in the assistant message, so the model still knows what it queried. It just can't see the result.
- **The placeholder says the tool can be called again.** This is the same rule as "always say when output is truncated" from the second post. The model needs to know something used to be there, so it doesn't conclude that the call returned nothing.
- **It doesn't call the model.** It's a plain string replacement: close to free, and fully deterministic.

Everything older than the last `KeepTurns` turns gets cleared. There's one constraint on where to cut: model APIs require every tool result to have a matching tool call before it. If the cut falls between an assistant message and its tool results, a later summary will leave behind a result with no call, and the API will reject the request. So the cut always lands on an assistant message:

```go
// boundary returns the index of the keep-th assistant message from the end;
// messages from there on are kept verbatim. The cut always lands on an
// assistant message, so a tool call is never separated from its results.
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

In most investigations, this stage alone brings the context back under `CompactTo`.

## Stage two: summarize

If the context is still over `CompactTo` after clearing, tool results aren't the problem anymore. The space is going to the turns themselves: dozens of turns of calls and analysis. Only then does stage two kick in: hand the earlier turns to a model, have it write a summary, and replace the original messages with it.

```go
// compact brings the context under CompactTo: clear old tool results first,
// then summarize if that isn't enough.
func (a *Agent) compact(ctx context.Context, transcript []Message, st *contextState) (Usage, error) {
	p := a.Context
	b := boundary(transcript, st.from, p.KeepTurns)

	// Stage one: clear old tool results. No model call, close to free.
	st.clearedTo = max(st.clearedTo, b)
	tokens := estimate(st.view(transcript))
	if tokens <= p.CompactTo {
		return Usage{}, nil
	}

	// Stage two: summarize [from, b).
	if b <= st.from { // nothing left to summarize except the recent turns
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

### Who reads the summary

This summary is not an ordinary "sum this up". Its reader is the model itself, later on, and that reader **will never see the original**. "Checked the logs, found a database problem" is a fine summary for a person. For the model it's nearly useless: it doesn't know which database, what error, or when it started, so it has to look everything up again.

So the summary prompt first tells the model where it stands, then spells out the structure:

```go
const handoffSections = `1. Confirmed facts, with the original evidence (timestamps, hostnames, numbers, exact error text). Don't reduce them to "the database has a problem".
2. Ruled-out directions, and why they were ruled out.
3. Write operations performed: what was done and what happened.
4. Open questions and planned next steps.
Don't include anything that wasn't actually found, and mark anything uncertain as uncertain.`

prompt := "Below is the earlier part of an investigation. From now on you will only see " +
	"the summary you write, not the original. Write the summary in this structure:\n" +
	handoffSections + "\n\n" + history
```

"You will only see the summary you write" works far better than "please summarize in detail".

Item 2 is the one most often left out. Summaries tend to record what was found, not what was ruled out. In an investigation, though, "payment logs are clean, ruled out" matters as much as "db-2 is timing out". Drop the first, and after compression the model checks payment all over again. The repeat detection from the first post only catches *consecutive* identical calls. A repeat that comes several turns later, on the other side of a compression, gets past it.

The `host=db-<N>` example from the second post, where grouping erased the specific host, applies here too. A summary is another kind of grouping, and grouping loses detail. "Include the original evidence" asks the model to keep the trail for drilling down even as it condenses.

A few more details:

- **The summary reads the originals.** Its input comes from the full transcript, not the view, so tool results that stage one cleared are still there for the summarizer. That's another benefit of keeping history and context separate.
- **The summary rolls forward.** On the second compression, the previous summary and the next stretch of history go to the model together, and a new summary comes back. There's only ever one `summary`, and it doesn't keep growing.
- **The summary can come from a cheaper model.** `ContextPolicy.Summarizer` can be set separately; writing a summary doesn't take the reasoning that investigating does. The catch is that summary quality may drop, which needs checking with the evaluation from part 5.
- **A truncated summary is an error.** Half a summary is worse than none, because it looks complete. It's the same rule as "never execute a truncated tool call" from the first post.

## What never goes into a summary

The model writes the summary, and models leave things out, over-condense, and sometimes get things wrong. So the rule is: **if code can preserve it, don't leave it to a summary.**

Under that rule, three things skip the summary:

**The task itself.** `transcript[:head]` is the user's original request, and it always stays verbatim at the start of the context. A summary might turn "api has been throwing 5xx since 14:02; look, don't touch" into "investigate api 5xx", and the half it dropped is the most important constraint. Task descriptions are usually short, so there's no reason to compress them.

**The most recent turns.** Messages within the last `KeepTurns` turns stay as they are, tool results included. The model's current reasoning depends on those details, and it hasn't yet turned them into its own words.

**Write operations.** This is the one you can least afford to lose. If the summary leaves out "api was already restarted at 14:20", the model may restart it again after compression. The idempotency key from the second post only covers a replay of the *same* call. It can't stop the model from issuing a new restart with a different ID.

The harness pulls the write log straight from the transcript. Whether a tool is read-only is already marked by `ToolSpec.ReadOnly` from the second post:

```go
// ledger extracts every write operation and its result from the transcript.
// It's generated by code and never passes through a model summary.
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
			status := "result: " + clip(r.Content, 300)
			if !ok {
				status = "no result"
			} else if r.IsError {
				status = "failed: " + clip(r.Content, 300)
			}
			fmt.Fprintf(&b, "- %s(%s) [%s] %s\n", c.Name, c.Args, c.ID, status)
		}
	}
	return b.String()
}
```

That's why `summary` and `ledger` are separate fields. `ledger` is rebuilt from the transcript every time, so the next summary never gets a chance to condense it. After compression, the handoff message the model sees looks like this:

```
[Earlier conversation has been compressed]

## Progress summary
1. Confirmed: from 14:02:11, api logged "upstream timeout (host=db-2)" 3,870 times in
   15 minutes; no timeouts on other db nodes. Connection pool exhaustion (402 times)
   first appeared at 14:02:13, after the timeouts, so it's likely an effect, not the cause.
2. Ruled out: payment logs are clean; no deploys around 14:00.
3. See the write log below.
4. Open: why db-2 is timing out. Next: check db-2's slow queries and connection count.

## Write operations (recorded by the harness, verbatim)
- restart_service({"service":"api","reason":"connection pool leak"}) [toolu_01] result: rolling restart triggered for api
```

The top half was written by the model and may be wrong. The bottom half was generated by code and is exact. `ReadOnly` defaults to `false`, so a read-only tool someone forgot to mark ends up in the write log. That costs a bit of context, but no real write ever goes missing. It's the same reasoning behind the defaults in the second post.

## When compression isn't enough

There are two cases compression can't rescue.

The first is **a single tool result that's bigger than the window**. The tools in the second post all limit their output, but a newly added tool might not. One `kubectl get pods -A -o yaml` can return hundreds of thousands of tokens. A result like that sits in the most recent turn, so it won't be cleared or summarized. That's why the harness caps tool results before they enter the transcript:

```go
out, err := t.Call(ctx, c.Args)
// ...
return clip(out, a.Context.MaxResult), err
```

Like the tools in the second post, `clip` states the total length when it truncates. This is a last line of defense, not a replacement for grouping inside the tool.

The second is **still being over the window after both stages**. For example, `KeepTurns` is set too high and the recent turns alone don't fit. Calling the model at that point just gets an API error, so the loop gets a new stop reason:

```go
const StopContextOverflow StopReason = "context_overflow"
```

As the first post said, StopReason is the contract between the agent and its caller, and every exit should be explicit. `context_overflow` can't be folded into `model_error`. A model error may go away on retry. A context overflow won't, however many times you retry. What needs changing is `KeepTurns`, `MaxResult`, or the tool itself.

| StopReason | Meaning | Typical caller response |
|---|---|---|
| context_overflow | Still over the context window after compression | Don't retry; check `KeepTurns`, `MaxResult`, and how much the tools return |

## Adding the wrap-up turn

In "After it stops", the first post described an idea without building it. When the budget runs out, `Final` might be nothing more than "let me check the database again", which is useless to the user. A better approach is to turn off tools, call the model once more, and have it sum up what it found so far.

The wrap-up turn and the summary do the same job: **the summary hands off to the model's future self, and the wrap-up hands off to a person.** So the wrap-up reuses `handoffSections` directly:

```go
func (a *Agent) wrapUp(ctx context.Context, view []Message, stop StopReason) ([]Message, Usage, error) {
	ask := Message{Role: RoleUser, Content: fmt.Sprintf(
		"The task stopped because of %s, and no more tools can be called. Based on what you have so far, "+
			"write a handoff note for whoever takes over:\n%s", stop, handoffSections)}
	resp, err := a.Model.Generate(ctx, append(view, ask), nil) // no tools provided
	if err != nil {
		return nil, resp.Usage, err
	}
	reply := resp.Message
	reply.ToolCalls = nil // even if the model still emits tool calls, they don't run
	return []Message{ask, reply}, resp.Usage, nil
}
```

In the loop, the old `done` becomes `finish`, which decides whether to wrap up before returning:

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

A few design decisions:

- **Which stop reasons get a wrap-up.** In four cases (`max_turns`, `token_budget`, `repeated_call`, `tool_failures`) the model has already done some work worth reporting. `completed` already has a conclusion, `canceled` means the user wants it to stop now, `truncated` and `model_error` mean the model call itself is failing, and with `context_overflow` there's no room for another call. None of those get a wrap-up.
- **The wrap-up doesn't change the StopReason.** After the wrap-up, `Stop` is still `max_turns`, so the caller still knows the task ran out of budget. The only difference is that `Final` is a handoff note instead of a sentence cut off mid-thought. If the wrap-up fails, the result isn't affected: `Final` falls back to the last text as before.
- **The wrap-up budget.** The wrap-up runs after the main budget check and isn't limited by `TokenBudget`, so the real ceiling on total usage is "main budget plus the cost of one wrap-up". The wrap-up's input is the entire current context, which is one more reason to keep the context small.

## Testing

Testing compression has one awkward part: you need the context to grow, without actually building messages with hundreds of thousands of tokens. The trick is that the loop trusts the `InputTokens` the API reports, so the scripted model can simply put a large number in its responses:

```go
func withUsage(r Response, in int) Response { r.Usage = Usage{InputTokens: in, OutputTokens: 100}; return r }
```

Wrap that in a recording model that saves the context it receives on every call, and you can check exactly what the model saw after compression:

```go
func TestCompactKeepsTaskAndLedger(t *testing.T) {
	m := &recordingModel{scriptedModel: scriptedModel{script: []Response{
		withUsage(toolUse("restart_service", `{"service":"api","reason":"connection pool leak"}`), 1000),
		withUsage(toolUse("search_logs", `{"service":"api"}`), 3000),
		withUsage(toolUse("search_logs", `{"service":"payment"}`), 5000),
		withUsage(toolUse("search_logs", `{"service":"api-gateway"}`), 7000),
		withUsage(toolUse("search_logs", `{"service":"db"}`), 9000),
		withUsage(answer("Root cause: db-2 ran out of connections"), 3000),
	}}}
	sum := &recordingModel{scriptedModel: scriptedModel{script: []Response{answer("db-2 timing out heavily; payment ruled out")}}}
	a := newAgent(m, bigLogs, restart) // restart is a fake tool with ReadOnly=false
	a.Context = ContextPolicy{Window: 100_000, CompactAt: 6000, CompactTo: 500, KeepTurns: 2, Summarizer: sum}

	r := a.Run(context.Background(), task)
	last := m.calls[len(m.calls)-1]
	// The task stays verbatim at the start; the handoff has both the summary and the write log.
	// Every tool result has a matching call; the full transcript has no cleared results.
	// ...
}
```

"Every tool result has a matching call" deserves its own helper, because this kind of bug doesn't fail anything in tests. It only shows up when a real API rejects the request:

```go
// Every tool_result must have a matching tool_use before it.
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

The other tests:

- When stage one is enough, the summarizer is never called (it's given a model that fails the test if called).
- A single tool result bigger than the window ends with `context_overflow`; with `MaxResult` set, the same scenario completes normally.
- When turns run out, the wrap-up turn runs, its call has no tools, `Stop` is still `max_turns`, and `Final` is the handoff note.
- Canceling skips the wrap-up.

As in the first two posts, these tests make sure the mechanism works, not that the summaries are any good. Whether a summary kept the key evidence, and whether the model went back to directions it had ruled out after compression, can only be seen in traces from real tasks.

## Summary

Context management comes down to separating two things. The transcript is everything that happened: complete and append-only. The context is the view sent to the model each turn, and it should be as small as possible. Once they're separate, compression no longer forces a choice between saving tokens and losing information, because nothing is ever deleted. It just isn't in this turn's view.

With that in place, a compression design can be checked item by item:

1. **When to compress**: Decide from the real token counts the API returns, and check before calling the model. Compress in batches between two watermarks, not with a window that slides every turn.
2. **How to compress**: Clear old tool results first, with no model call. Summarize only if that isn't enough. Cut on an assistant message so tool calls and results stay together.
3. **What the summary says**: Tell the model it won't see the original again. Require original evidence and ruled-out directions.
4. **What skips the summary**: The task, the most recent turns, and the write log. If code can preserve it, don't leave it to the model.
5. **When compression isn't enough**: Cap tool results before they enter the transcript. If the context is still over the window, stop with `context_overflow` instead of folding it into `model_error`.
6. **After stopping**: Run a wrap-up turn for budget-type stops, reuse the summary structure, and leave the StopReason unchanged.

This post kept saying "you can only see that in traces from real tasks": how often compression fires, how many tokens each one saves, how much the wrap-up costs, and what `KeepTurns` and the watermarks should be. The budget limits from the first post left the same question open. Answering any of them starts with recording what the agent does on every turn. The next post covers observability: adding traces to an agent, breaking down stats by stop reason and by tool, and setting these parameters from data instead of gut feel.
