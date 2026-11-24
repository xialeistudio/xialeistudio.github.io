---
title: "An Agent Trace Should Show What the Model Saw"
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

The first three posts left a pile of parameters marked "tune this from real data". Part 1 said the turn and token limits should sit "a bit above the P99". Part 3 said `CompactAt`, `CompactTo` and `KeepTurns` should come from real runs. And there's a harder kind of question that isn't about parameters at all: the agent reaches the wrong conclusion, the loop ends with `completed`, nothing errors, and you want to know which step it got wrong.

Both need the same thing first: a record of what the agent did on every turn. This is the fourth post in the *Agent Engineering Notes* series. Continuing with the Go incident-investigation agent, it covers what a trace should record, how to reconstruct the exact context the model saw on any turn with very little storage, and how to set limits, compaction parameters and cost expectations from statistics over many runs.

<!--more-->

## What ordinary logs can't tell you

Start with a concrete failure. A user asks "the api service has been throwing 5xx since 14:02, find out why". The agent runs 11 turns and concludes "root cause is a connection pool leak in api; recommend a restart". The real cause was slow queries on db-2. The exhausted pool was a symptom.

With the usual service logs and metrics, here's what you see: 11 model calls, all successful, average latency 2.8s. 14 tool calls, all successful. 96k tokens in total. Every number looks healthy, because **most agent failures aren't exceptions, they're decisions**. No line of code failed. The model made a bad call on some turn.

To find that call, these are the questions you need answered:

- On turn 7 the model stopped pursuing db-2. What was in front of it at that point?
- Was the db-2 timeout result still in context, or had part 3's first-level compaction already cleared it?
- If a summary was written, did it keep the fact that the timeouts started *before* the pool ran out?

They all come down to one thing: **reconstructing the context the model saw on a given turn**. Latency and token counts are secondary.

## What a run records

A run is a sequence of turns. Each turn may contain a compaction, one model call, and some tool calls, in that order. A run may end with a wrap-up turn. The trace follows the same structure, one event per thing that happened:

```go
type Event struct {
	RunID string
	Turn  int
	Kind  EventKind // model | tool | compact | wrap_up | run_end
	Start time.Time
	Dur   time.Duration
	Usage Usage
	Err   string

	// model: how this turn's view was derived from the transcript, and what the model decided
	View   *ViewRef
	Finish FinishReason

	// tool
	Tool    string
	CallID  string
	Args    json.RawMessage
	ErrKind ErrorKind
	Bytes   int // result size before truncation

	// compact
	Level         string // clear or summarize
	Before, After int
	Summary       string // recorded only on summarize
	Ledger        string

	// run_end
	Stop       StopReason
	Transcript []Message
}
```

(The real code has `json:",omitempty"` tags on every field; they're left out here.)

A few deliberate choices:

- **One flat struct rather than a type per event.** Events end up in JSONL, a log system or a warehouse, and flat records are the easiest to handle there. Different kinds just use different fields.
- **Record tokens, not money.** Prices change, and the summarizer may be a cheaper model. Raw data stays in tokens, and cost is computed at analysis time with current prices. More on this under "Cost".
- **Record tool result size before truncation.** Part 3 capped results with `MaxResult` before they enter the transcript. If you only record the post-truncation size, you'll never see which tool routinely returns hundreds of kilobytes, and that's exactly the signal that a tool needs redesigning.
- **Classify errors with part 2's `ErrorKind`.** Lots of `invalid_args` means a tool description is unclear. Lots of `unavailable` means a dependency is in trouble. The fixes have nothing in common, so the numbers shouldn't be lumped together.
- **Don't record tool result content.** It's already in the transcript. The next section explains why that's enough.

## Store indices, not views

The obvious way to reconstruct each turn's context is to store each turn's view verbatim. That walks straight back into the arithmetic from part 3: turn n's context contains everything before it, so storing one per turn grows quadratically with the number of turns, just like token usage without compaction.

Separating the transcript from the context in part 3 gives a better option. The context is a view of the transcript, and `view` is a pure function: given the full transcript plus a few indices and two strings from `contextState`, it returns exactly the messages sent to the model. So the trace doesn't need the view, only **the inputs that produce it**:

```go
// ViewRef records the view's indices. view is a pure function of the transcript,
// so the indices plus the summary are enough to rebuild it exactly.
type ViewRef struct {
	Head, From, ClearedTo int
	Len                   int // transcript length at the time of the model call
}
```

`Len` is the transcript length at the moment of the call. Because the transcript is append-only, its first `Len` messages are everything the model was working from. The summary and the write ledger only change when a compaction summarizes, so they're recorded once, on the `summarize` event. The full transcript is recorded once, on `run_end`.

Rebuilding a turn's view means collecting those pieces and calling `view` again:

```go
// ViewAt rebuilds the context sent to the model on the given turn.
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

A compaction happens before the model call on the same turn, hence `e.Turn <= turn`.

Storage per run is now "the transcript, a few integers per turn, and one string per summary", which grows linearly. For the wrong-conclusion example above, you call `ViewAt(events, 7)` and look at what the model actually had on turn 7.

This rests on one assumption: **`view` must be deterministic**. If anyone later adds the current time, random sampling or an external lookup to view construction, the same inputs will no longer produce the same context. The "Testing" section has a test whose only job is to guard this.

Two things aren't in the transcript at all: the system prompt and the tool definitions. They change between versions, and a trace has to map back to the version that produced it. The simplest approach is to give them a version number or hash and record it alongside the RunID. When we get to evaluation in part 5, "which prompt version was this" is exactly what you'll be comparing.

## Where the instrumentation goes

Every event is emitted from `Run`, not scattered across helper functions. Here's what's new in the loop:

```go
rec := recorder{tracer: a.Tracer, runID: rand.Text()}
// ...
// Compaction: comparing contextState before and after tells us which level ran
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

`compact` itself is unchanged. Whether `st.from` moved tells us if a summary was written.

`execute` now also returns one event per tool call. Duration, pre-truncation size and error kind are collected inside `execute` because it's the only place that knows when each call started and finished (read-only tools run in parallel). The `clip` that used to live in `callTool` moves here too, so the raw size is captured before truncation:

```go
run := func(i int) {
	c, t0 := calls[i], time.Now()
	out, err := a.callTool(ctx, c)
	e := Event{Kind: EventTool, Tool: c.Name, CallID: c.ID, Args: c.Args, Start: t0}
	if err != nil {
		out, e.ErrKind = err.Error(), kindOf(err)
	}
	e.Dur, e.Bytes = time.Since(t0), len(out) // size before truncation
	results[i] = ToolResult{CallID: c.ID, Content: clip(out, a.Context.MaxResult), IsError: err != nil}
	events[i] = e
}
```

The wrap-up and `run_end` events are emitted from `finish`. `run_end` carries the full transcript and the final StopReason.

`recorder` does two things: fill in the RunID, and make sure a broken tracer can't hurt the agent:

```go
func (r recorder) emit(e Event) {
	if r.tracer == nil {
		return
	}
	defer func() { _ = recover() }() // a tracing bug must not take down the investigation
	e.RunID = r.runID
	r.tracer.Event(e)
}
```

The rule here: **observing must not change what's being observed**. Tracing is supporting infrastructure. A bug in it shouldn't crash an incident investigation halfway through, and it must not influence control flow, such as skipping a check because writing the trace is slow. The `Tracer` interface has one method with no return value, so callers have nothing to branch on.

The simplest implementation writes one JSON line per event:

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

The lock is there because tool events can come from parallel goroutines. Strictly speaking, the current code emits tool events after `execute` returns, but the interface contract should allow concurrent calls so that switching to live emission later doesn't require touching implementations.

If your team already runs OpenTelemetry, these events map onto spans naturally: the run is the root span, model and tool calls are child spans, and the OpenTelemetry GenAI semantic conventions already define standard attributes for things like model name and token usage. Large text such as the transcript and summaries doesn't belong in span attributes, though. The usual pattern is to put it in object storage and have the span carry the RunID and a pointer.

## Reading a single run

The first thing you'll do with events is print a run as a timeline. Here's one investigation (numbers are illustrative):

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

One screen is enough to find a lead on the wrong conclusion. On turn 3, `query_slow_log` returned 48KB and got cut by `MaxResult`. It's a tool added later that returns raw slow-query logs instead of aggregating them the way part 2 recommends. Then on turn 7 the first-level compaction cleared that result. Calling `ViewAt(events, 7)` confirms it: the slow-query result is a one-line placeholder. The model never went back to db, because what it saw on turn 3 was already a truncated half, and the cut-off half contained the ordering of events.

The fix is now obvious, and it isn't a prompt change: make `query_slow_log` aggregate before returning, like part 2's `search_logs`, instead of relying on the harness to truncate it.

Timelines also expose bad configuration. This one comes from this post's own test case:

```
t3   model      in=5000   out=100   tool_use
t4   compact    summarize 7200→4312
t4   model      in=7000   out=100   tool_use
t5   compact    summarize 9200→4314
t5   model      in=9000   out=100   tool_use
t6   compact    summarize 11200→4313
```

A summary every turn, and the post-compaction size stuck around 4,300. The cause: `CompactTo` was set to 500, but the two turns kept by `KeepTurns` already take over 4,000 tokens on their own. Compaction can never reach its target, so the next turn pushes the context back over `CompactAt`. Part 3 said to compact in batches, not every turn. This configuration does the opposite, paying for a summary every turn and invalidating the prompt cache every turn. No single log line shows it. A timeline shows it at a glance.

## From one run to many

A single run's trace is for pinning down a specific problem. Parameters come from statistics across many runs. First, reduce each run to one row:

```go
type RunStats struct {
	RunID       string
	Stop        StopReason
	Turns       int
	Dur         time.Duration
	Usage       Usage // total, including compaction and wrap-up
	Summarizer  Usage // the summarizer's share
	WrapUp      Usage // the wrap-up turn's share
	Cumulative  []int // cumulative tokens at the end of each turn, for simulating tighter limits
	MaxInput    int   // largest single-turn input, i.e. peak context size
	Compactions int
	Summaries   int
	ToolCalls   map[string]int
	ToolErrors  map[ErrorKind]int
	Revisits    int // calls repeated after a compaction that were already made before it
}
```

`Stats(events)` computes these in one pass. Most fields are simple sums. Two are worth a closer look.

**`Cumulative`** holds the running token total at the end of each turn. It's what lets the next section answer "if the limit were tighter, where would this run have stopped, and what would it have cost?"

**`Revisits`** addresses a question part 3 left open: after compaction, does the model go back and re-query things it already checked, or already ruled out? The approach: remember the most recent turn each call was made (tool name plus normalized arguments, reusing `callsKey` from part 1), and count it as a revisit if it shows up again after a compaction:

```go
case EventTool:
	key := callsKey([]ToolCall{{Name: e.Tool, Args: e.Args}})
	if t, ok := seen[key]; ok && t < lastCompact {
		s.Revisits++
	}
	seen[key] = e.Turn
```

Part 1's repeat detection only catches *consecutive* identical calls. `Revisits` counts repeats that straddle a compaction. They aren't always bad, since sometimes the model really does need another look. But if the rate climbs as you lower `KeepTurns`, compaction is throwing away information the model still needs.

## The distribution by stop reason

Part 1 framed StopReason as a contract between the agent and its caller. For a single run, it tells the caller what to do. Across many runs, **the share of each stop reason is a metric you can track**.

Say you aggregate 200 investigation runs (numbers are illustrative):

| StopReason | Share | Turns P50 / P90 | Tokens P50 / P90 |
|---|---|---|---|
| completed | 78% | 8 / 14 | 61k / 130k |
| max_turns | 11% | 15 / 15 | 170k / 220k |
| token_budget | 4% | 9 / 12 | 200k / 200k |
| repeated_call | 3% | 6 / 10 | 42k / 90k |
| tool_failures | 2% | 3 / 4 | 15k / 24k |
| other | 2% | | |

This table alone raises several questions:

- **`max_turns` has P50 and P90 both at 15.** That's the limit itself. These runs were cut off, and you can't tell how many turns they actually needed. The next section deals with this.
- **`token_budget` runs used up the budget in 9 turns.** That's over 20k tokens per turn, far above `completed` runs. It's usually not task complexity but one tool returning too much. Sort tools by `Bytes` and you'll find it. Fix the tool. Don't raise the budget.
- **`repeated_call` clusters in a few task types.** Pull up those timelines. A common cause is tool errors that don't tell the model what to do next (part 2's `Hint`).

What a rising share means for each stop reason fits in a table worth reading next to part 1's handling table:

| Rising StopReason | Usually means | Look at first |
|---|---|---|
| max_turns | Tasks got harder, or the model is going in circles | Turn distribution; whether the last few calls repeat |
| token_budget | Turns are too expensive | Tools sorted by `Bytes`; `MaxInput` |
| repeated_call | The model is stuck | Tool errors and hints at the point it got stuck |
| tool_failures | A dependency is unhealthy | `unavailable` in `ToolErrors` |
| truncated | Output limit is too low | Distribution of output tokens |
| context_overflow | Compaction settings or tool output size | `KeepTurns`, `MaxResult`, post-compaction size |

These shares work best as trend charts. Switch models, edit the prompt or add a tool, and you can see which line moved. What this table can't tell you is how many `completed` runs reached the *right* answer. That's part 5's job.

## Derive limits from traces

Part 1 said the limit should be "a bit above the P99 of normal runs". Try to compute it and you hit a problem: **the distribution you observe is already truncated by the limit**. With `MaxTurns` at 15, a task that needs 20 turns stops at 15 with `max_turns` and shows up in the data as 15 turns, forever. The P99 across all runs comes out as 15 and tells you nothing. Looking only at `completed` runs is wrong too, since that pretends the truncated tasks don't exist.

The fix is to run a batch with loose limits first, say `MaxTurns` at 60 and a very large token budget, to get the real distribution. Don't do this in production. Use the evaluation set from part 5, or replay past incidents.

Loose-limit runs have a useful property: **a tighter limit just cuts the trajectory short, and everything before the cut is identical to the real run**. A run that took 25 turns would, under a limit of 15, stop at the end of turn 15 with the same first 15 turns and exactly `Cumulative[14]` tokens spent. So a batch of loose-limit runs lets you simulate any tighter limit offline:

```go
// TurnCurve simulates what a tighter MaxTurns would have produced, using runs made under a loose limit.
// A tighter limit only truncates the trajectory, so everything before the cut is identical to the real run.
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
				tokens += float64(r.Cumulative[k-1]) // it would have stopped at the end of turn k
			}
		}
		n := float64(len(runs))
		pts = append(pts, Point{Limit: k, Success: succ / n, MeanTokens: tokens / n})
	}
	return pts
}
```

It doesn't work the other way: data collected at a limit of 15 can't tell you what a limit of 25 would do. So **collect with loose limits, then tighten**.

`ok` decides whether a run succeeded. The crudest version is `r.Stop == StopCompleted`, but `completed` doesn't mean correct. Human labels or part 5's evaluation results are better.

Over 200 loose-limit runs, the curve might look like this (numbers are illustrative):

| MaxTurns | Success rate | Mean tokens per run |
|---|---|---|
| 10 | 61% | 58k |
| 15 | 82% | 74k |
| 20 | 89% | 83k |
| 30 | 92% | 96k |
| 60 | 93% | 112k |

Going from 15 to 20 buys 7 points of success for 12% more cost. Going from 30 to 60 buys 1 point for 17% more. The limit belongs where the curve flattens, here somewhere between 20 and 30. This beats "a bit above P99" because it puts **what an extra turn buys** next to **what it costs**, while P99 only looks at the cost side.

Some caveats when reading the curve:

- **Discount late successes.** Runs that only finish after turn 30 tend to be less trustworthy. The model may have wandered around and then pieced together an answer. If `ok` only checks `completed`, the tail looks better than it is.
- **Wrap-up isn't simulated.** Under a tighter limit, truncated runs would do a wrap-up turn, so the real cost is a bit higher than simulated.
- **Token budgets work the same way.** Find the first turn in `Cumulative` that exceeds the budget. That's where the run would have stopped. Let either the turn limit or the token budget be the one that normally binds, with the other as a backstop. If both trigger often, one of them is set wrong.
- **Recompute regularly.** New models, prompt edits and new tools all reshape the curve. This belongs in the evaluation pipeline from part 5.

## Same approach for compaction settings

Part 3's compaction settings can be tuned the same way. Watch these:

- **Compactions per run, and whether post-compaction size gets below `CompactTo`.** If the fraction of compactions that end above `CompactTo` is noticeably above zero, you have the compact-every-turn setup from the timeline earlier.
- **Share of compactions that summarize.** Most should be handled by the first level. If summaries dominate, either `CompactTo` is too low or the tasks really are that long.
- **`Revisits`.** Lowering `KeepTurns` or `CompactTo` saves tokens, but if revisits rise with it, the savings go to repeated calls, and you may lose conclusions along the way.
- **Summarizer cost share.** The summarizer's tokens as a fraction of the total. If you switched to a cheaper summarizer model to save money, check whether `Revisits` and success rate got worse.

The method matches limit-setting: fix a batch of tasks, change one parameter, compare these metrics and the success rate. The difference is that compaction settings change what the model sees, so unlike turn limits you can't simulate them offline from existing traces. Every configuration has to actually run.

## Cost

As mentioned, traces record tokens and cost is computed at analysis time. Each model has its own price, and summarizer tokens are priced at the summarizer's rate:

```go
// Price is the cost per million tokens.
type Price struct{ In, Out float64 }

func (p Price) Of(u Usage) float64 {
	return (float64(u.InputTokens)*p.In + float64(u.OutputTokens)*p.Out) / 1e6
}

// Cost prices each model separately: the summarizer may be a different model.
func (s RunStats) Cost(main, summarizer Price) float64 {
	rest := Usage{s.Usage.InputTokens - s.Summarizer.InputTokens, s.Usage.OutputTokens - s.Summarizer.OutputTokens}
	return main.Of(rest) + summarizer.Of(s.Summarizer)
}
```

Two views are more useful than the total:

- **Look at the distribution, not the mean.** Per-run cost for agents is long-tailed. A few runs that go in circles can cost ten times the average. Budgets and alerts should be set on P90 and P99, which the mean hides.
- **Break it down by phase.** Main loop, summaries, wrap-up. Part 3 noted that a wrap-up's input is the entire current context. If its share is high, either too many runs stop on budget limits or the context is too large when they stop.

This doesn't account for prompt caching. Cached input tokens cost a fraction of the normal price, which matters a lot for agents, whose prefixes are stable and which call the model over and over. Part 9 covers it, and `Usage` will grow cache fields then.

## What's in a trace

One last thing that's easy to miss: the trace stores the full transcript, meaning every tool result verbatim. For an incident agent, that means production logs, request payloads that may contain user data, and internal service topology all land in trace storage as-is.

So treat trace storage like production data: access control, retention limits, and redaction where needed. Redaction belongs in the Tracer implementation, not in the tools. What a tool returns to the model shouldn't change because a trace is being written, or you've broken "observing must not change what's being observed".

## Testing

The trace tests guard three things.

**A replayed view matches exactly what the model received.** Part 3's `recordingModel` records the context the model gets on each call. Rebuild every turn from the trace and compare. The scenario deliberately triggers several rolling summaries:

```go
func TestTraceReplaysView(t *testing.T) {
	tr := &memTracer{}
	m, r := compactingRun(tr)
	// ...
	// Every turn rebuilt from the trace must match what the model actually received
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

This is the guard for the "`view` must be deterministic" assumption. Whoever adds something nondeterministic to view construction will see this test fail first. A second test writes the events to JSONL and reads them back to make sure replay survives serialization, since production traces are always read back from storage.

**Tracing doesn't change the agent's behavior.** Run the same scenario with no tracer and with a tracer that panics on every event. The results must be identical:

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

**The statistics are right.** Total usage from `Stats` must equal `Result.Usage`, the last entry of `Cumulative` must equal the total, and re-querying the same service after a compaction must count as one revisit. `TurnCurve` is checked against a few hand-built `RunStats`: at a limit of 10, a 12-turn run is charged its turn-10 cumulative tokens, and an unfinished 30-turn run doesn't count as a success.

The compact-every-turn timeline earlier was found while writing the `Stats` test. The test case had `CompactTo` casually set to 500, and asserting the compaction count showed it firing every turn. A small proof of the point: once you have traces, configuration problems surface on their own.

## Summary

The biggest difference between agent observability and ordinary service observability is that what you're debugging is mostly the model's decisions, not exceptions. So the first requirement for a trace is that it can reconstruct the context the model saw on every turn. Latency and tokens come after that.

To make that work in practice, check each of these:

1. **What to record**: organize events as run → turn → compaction, model call, tool calls. Record tokens, not money. Record tool result size before truncation. Classify errors by kind.
2. **How to reconstruct context**: don't store views, store the indices that produce them. Record summaries only when they change, and the transcript once. This depends on view construction being deterministic, so guard it with a test.
3. **Where to instrument**: emit everything from the loop. The Tracer returns nothing and is wrapped in recover, so it can't change the agent's behavior.
4. **Stop reasons**: each StopReason's share is a metric. When one rises, look at the matching data before touching the prompt.
5. **Setting limits**: collect with loose limits, simulate tighter ones offline, plot success against cost, and set the limit where the curve flattens.
6. **Cost**: price per model at analysis time. Look at the distribution and the per-phase breakdown, not the mean.
7. **Trace contents**: the full transcript is production data. Manage it like production data.

Several places in this post handed the hard part to "success rate": success on the limit curve, success after tuning compaction, how many `completed` runs are actually right. So far, success means `Stop == completed` or a human reading the transcript. The next post is about evaluation: after changing one line of the prompt, how do you know, systematically, that the agent didn't get worse?
