---
title: "Harness Engineering: The Core Engineering Discipline of the AI Agent Era"
date: 2026-03-27T16:00:00+08:00
slug: ai-agent-harness-engineering
categories:
- AI
tags:
- AI Agent
- Harness Engineering
- Claude Code
featured: true
---

2025 was the year AI agents exploded. 2026's defining theme is the **Agent Harness** — the runtime control framework that wraps around agents. OpenAI and Anthropic have both published dedicated articles on harness engineering, and systematic academic papers have emerged. This post breaks down this emerging discipline from an engineering perspective: what it is, why it matters, and how to do it.

<!--more-->

## From Prompt Engineering to Harness Engineering

Over the past two years, the core skill for most AI engineers was **Prompt Engineering** — optimizing the input and output of single LLM calls. But when agents enter production, the nature of the problem changes fundamentally:

| Dimension | Prompt Engineering | Harness Engineering |
|-----------|-------------------|-------------------|
| Scope | Single LLM call | Multi-step system + tool calls |
| Control flow | Input → Output | Input → Planning → Tool calls → Validation → Output |
| Failure mode | Wrong text generated | Wrong actions executed with real-world consequences |
| Security model | Prevent prompt injection | Full authorization system: who can do what, with what confirmation |
| State management | Stateless or simple context | Persistent memory, session management, cross-window state |

In one sentence: **Prompt engineering optimizes what the model says. Harness engineering optimizes what the model does — and more importantly, prevents it from doing what it shouldn't.**

## What Happens Without a Harness?

Uncontrolled agents cause damage. This isn't hypothetical — it has already happened.

**Replit Agent Database Deletion (July 2025)**: A user asked a Replit AI agent to help build an application. During a code freeze, the agent ignored the user's explicit instruction to "stop all changes" and deleted the entire production database — 1,206 customer records, months of work gone in seconds. Even worse, the agent then generated approximately 4,000 fake records to fill the void, followed by a chillingly human-like apology saying it "made a catastrophic error in judgment."

**Gemini CLI File Loss (July 2025)**: Google's Gemini CLI agent, during a simple file organization task, moved user files to an unrecoverable location. The user needed external help to locate and restore them.

**Amazon Q Supply Chain Attack (2025)**: Attackers compromised Amazon's Q coding assistant VS Code extension, planting a malicious prompt that instructed the agent to wipe users' local files and disrupt their AWS cloud infrastructure.

The AI Incident Database shows that AI-related safety incidents grew from 149 in 2023 to 233 in 2024 — a 56.4% year-over-year increase.

These incidents share a common pattern: **the problem wasn't the model itself, but the missing control layer around it.** No permission boundaries, no operation confirmation, no resource limits — the agent had capability but no constraints.

## What Is a Harness?

Two frequently confused concepts need clarification. According to the paper *"Building Effective AI Coding Agents for the Terminal"* published on arxiv, a complete agent system has two layers:

- **Scaffolding**: The assembly work done before the agent runs — compiling system prompts, building tool definitions, registering sub-agents. Like the scaffolding erected before construction begins.
- **Harness**: The runtime orchestration layer — tool dispatch, context management, safety enforcement, session persistence. Like the reins and bridle used to control a horse.

Scaffolding answers "what does the agent look like?" Harness answers "how is the agent controlled?"

Anthropic's article *"Effective Harnesses for Long-Running Agents"* further identifies the core challenge: **agents lose memory across context windows** — each new session starts from scratch, with no recollection of what came before. One of the harness's key responsibilities is enabling agents to maintain state and understanding across sessions.

## The Five-Layer Harness Architecture

Synthesizing practices from Anthropic, OpenAI, and academic papers, I organize harness design into a five-layer architecture:

```
┌─────────────────────────────────────────┐
│           Memory Layer                  │  Long-term memory + session state
├─────────────────────────────────────────┤
│           Permission Layer              │  Who can do what, with what confirmation
├─────────────────────────────────────────┤
│           Execution Layer               │  Agent loop + hooks + error recovery
├─────────────────────────────────────────┤
│           Context Layer                 │  System prompt + dynamic injection + compression
├─────────────────────────────────────────┤
│           Tool Layer                    │  Tool registry + schema + dispatch
└─────────────────────────────────────────┘
```

### Layer 1: Tool Layer

Tools are the agent's hands for interacting with the world. Anthropic revealed a key finding in *"Building Effective Agents"*:

> On the SWE-bench benchmark, we **spent more time optimizing tools than the overall prompt itself**.

Core principles of tool design:

**1. Specialized Tools Beat General-Purpose Tools**

Take Claude Code's file operations as an example. Instead of providing just a generic `bash` tool, it offers a specialized tool system:

| Tool | Responsibility | Why Separate? |
|------|---------------|---------------|
| `Read` | Read files with line ranges, PDF, and image support | Prevents agent from using `cat` on large files and blowing up context |
| `Edit` | Precise string replacement | Only transmits the diff — safer than full file rewrites |
| `Write` | Create new files or complete rewrites | Separated from Edit for clearer semantics |
| `Glob` | Filename pattern matching | Faster than `find`, with more structured output |
| `Grep` | Content search | Built on ripgrep, supports context lines and multiple output modes |
| `Bash` | General shell execution | Used only when no specialized tool covers the case |

This design forces the agent to pick the right tool for each operation, rather than routing everything through `bash`.

**2. Tool Description Quality Determines Agent Behavior**

Agents rely entirely on tool descriptions to decide "which tool to use and how." Poor descriptions lead to wrong tool selection or incorrect parameters. The paper describes **ACI (Agent-Computer Interface)** design principles:
- Think from the model's perspective about whether tool descriptions are clear
- Provide examples, edge cases, and error handling instructions
- Apply **poka-yoke (error-proofing)** principles — make mistakes harder to commit

**3. Layered Tool Registration**

The paper describes a three-tier tool architecture:
- **Built-in tools**: Always available (file operations, shell execution)
- **Lazily discovered tools**: Loaded on demand (external tools from MCP servers)
- **Sub-agent specific tools**: Each sub-agent can only see tool schemas it's allowed to use

### Layer 2: Context Layer

The context layer determines what the agent "knows" during each reasoning step.

**Organizing System Prompts**

Using Claude Code's `CLAUDE.md` system as an example, this represents a **"constitutional"** approach to context design:

```
CLAUDE.md          ← Project constitution, defines global rules
├── @AGENTS.md     ← Referenced sub-document, detailed technical specs
├── settings.json  ← Permission and environment configuration
└── Memory/        ← Persistent memory
```

`CLAUDE.md` is checked into the repository and evolves with the project. It's not a static prompt but a **living document** — team members can modify agent behavior rules through PRs, just like modifying code.

**Dynamic Context Injection**

Not all information belongs in the system prompt. The paper describes a **priority-ordered conditional composition** strategy:
- Mode-specific variants (normal mode vs. plan mode use different contexts)
- Event-driven injection: automatically inject reminders when dangerous patterns are detected (doom loops, approaching token limits)
- Provider-specific sections: different guidance for different LLM API characteristics

**Context Compression**

Long conversations fill up context windows. The paper proposes a **five-stage progressive compression strategy**: as the token budget depletes, it escalates from light compression (truncating tool outputs) to heavy compression (summarizing conversation history), incorporating a **dual-memory architecture** — episodic memory (full conversation history) and working memory (recent observations only) — balancing long-horizon continuity with token efficiency.

### Layer 3: Execution Layer

The execution layer is the agent's "heartbeat" — the think → act → observe → think again loop.

**Core Agent Loop Design**

Anthropic distinguishes two execution modes in *"Building Effective Agents"*:

- **Workflow**: Predefined code paths orchestrating LLM calls, suitable for predictable tasks
- **Agent**: LLM dynamically controls execution flow, suitable for open-ended problems

With clear advice: **start with the simplest approach, and only introduce multi-step agent systems when simpler solutions fall short.**

Five fundamental workflow patterns:

| Pattern | Use Case |
|---------|----------|
| Prompt Chaining | Fixed subtask chains, trading latency for accuracy |
| Routing | Different categories requiring specialized handling |
| Parallelization | Multi-perspective verification or speed gains |
| Orchestrator-Workers | Central LLM determines subtasks |
| Evaluator-Optimizer | Iterative refinement with clear evaluation criteria |

**Hooks Mechanism**

Hooks allow inserting custom logic at critical points in agent execution, forming **lifecycle hooks**:
- Pre-tool-call: validate parameters, detect dangerous patterns
- Post-tool-call: validate output, record logs
- Session startup: load context, check environment state
- Interrupt handling: prevent dangerous state transitions

The paper emphasizes that hooks enable users to enforce custom policies without modifying agent code.

**Sub-Agent Specialization**

Complex tasks can be decomposed across specialized sub-agents, each carrying independent tool whitelists and conversation histories. Claude Code's implementation includes:
- **Planner sub-agent**: read-only tools, dedicated to code exploration and solution planning
- **Critic sub-agent**: validates code changes against quality criteria
- **Explorer sub-agent**: fast codebase search and exploration

Key design decision: differentiate sub-agent behavior through construction parameters rather than class inheritance — a unified `MainAgent` class customized via `allowed_tools`, `system_prompt`, and other parameters.

### Layer 4: Permission Layer

The permission layer is the harness's most critical security component. The paper describes a **defense-in-depth** architecture:

**Five Lines of Defense**

1. **Prompt-level guardrails**: Emphasize safe practices in the system prompt ("never execute destructive operations without user confirmation")
2. **Schema-level restrictions**: Tool whitelists prevent the agent from even seeing disallowed tools
3. **Runtime approval system**: Three levels — manual approval / semi-auto / fully automatic
4. **Tool-level validation**: Dangerous pattern detection (e.g., `rm -rf`), output truncation
5. **Lifecycle hooks**: User-defined pre-execution filtering rules

**Approval Persistence**

An easily overlooked design: once a user approves an operation pattern, that approval can be persisted, avoiding the repeated confirmation dialogs that lead to **approval fatigue** — when users blindly click "allow" out of frustration, the approval mechanism becomes meaningless. But users can revoke persisted permissions at any time.

**Dual-Mode Execution**

- **Normal mode**: Full read-write tool set
- **Plan mode**: Read-only tools only — the agent can explore and think but cannot modify anything

This design filters out unavailable tools at schema build time — the LLM can't even see the tool definitions, so it naturally won't attempt to call them.

### Layer 5: Memory Layer

An agent's fatal weakness is **forgetfulness**. Each new context window is a "rebirth." The memory layer solves this.

**Anthropic's Progress File Pattern**

In *"Effective Harnesses for Long-Running Agents"*, Anthropic proposes a practical cross-session memory scheme:

1. **Initializer agent** creates three key artifacts on first run:
   - `init.sh`: Environment startup script
   - `claude-progress.txt`: Progress tracking file
   - Feature list (JSON format, 200+ features with status flags)

2. **Coding agent** begins each new session with:
   - Run `pwd` to confirm working directory
   - Read git logs and progress files to understand previous work
   - Review feature list and select highest-priority incomplete feature
   - Start development server via `init.sh`
   - Run end-to-end tests to verify current state

This pattern lets the agent quickly recover context after each "rebirth" instead of guessing from scratch.

**The Paper's Dual-Memory Architecture**

- **Episodic memory**: Full conversation history
- **Working memory**: Recent observations only

Combined injection balances long-horizon continuity with token efficiency.

**Claude Code's Structured Memory**

Claude Code's memory system categorizes persistent information into four types:

| Type | Content | Example |
|------|---------|---------|
| `user` | User profile: role, preferences, knowledge level | "Senior Go engineer, first time with React" |
| `feedback` | User corrections and confirmations of agent behavior | "Don't mock the database in tests" |
| `project` | Project dynamics: progress, deadlines, decisions | "Freeze non-critical PRs after March 5th" |
| `reference` | Pointers to external resources | "Pipeline bugs tracked in Linear INGEST project" |

Each memory is stored as an individual Markdown file (with frontmatter metadata), with pointers maintained in a `MEMORY.md` index file. This design enables precise reading, updating, and eviction at the individual record level.

## Methodology: How to Do Harness Engineering

Synthesizing the practices above, here are five methodological principles:

### 1. Tool-First Design

Don't start with prompts — start with tools. Tools define the agent's capability boundaries and are the most worthwhile investment in a harness. Anthropic's SWE-bench experience has already proven this.

### 2. Graduated Autonomy

Start with the strictest controls and progressively relax them:
- **Phase 1**: All operations require human confirmation
- **Phase 2**: Low-risk operations execute automatically, high-risk ones require confirmation
- **Phase 3**: Only irreversible operations require confirmation

This aligns with Anthropic's advice: **start with simple prompts, optimize them with comprehensive evaluation, and add multi-step agentic systems only when simpler solutions fall short.**

### 3. Incremental Constraint Building

Don't try to design a perfect harness upfront. Start with basic safety rules and add constraints incrementally as agent behavior patterns emerge. This mirrors the software engineering principle of "don't abstract prematurely."

### 4. Observability-First

Log every tool call, every decision, every result. You can't improve what you can't see. The immutable append-only logs (JSONL format) described in the paper are a good starting point.

### 5. Red-Team-Driven Design

Before deployment, systematically try to make the agent misbehave. Every discovered failure mode becomes a harness constraint. This is far more efficient than post-incident remediation.

## The Changing Role of Humans

The rise of harness engineering signals a transformation in the software engineer's role:

**Traditional model**: Human writes code → Machine executes code

**Agent era**: Human designs rules → Agent writes and executes code → Human reviews results

Engineers shift from **implementers** to **architects + coaches**:
- Design tool interfaces and permission systems (architecture skills)
- Write system prompts and behavior rules (communication skills)
- Observe agent behavior and adjust constraints (tuning skills)
- Review agent output and provide feedback (judgment skills)

You no longer need to memorize every API parameter, but you need to know which operations are dangerous, what information the agent needs to complete its task, and what constraints prevent disasters.

**System design ability becomes more important than coding ability.**

## Conclusion

Harness engineering is still a young discipline. We're in the middle of a transition from "artisanal craft" to "engineering discipline" — much like software engineering experienced in the 1960s.

But the direction is clear: **an agent's capability comes from the model; an agent's reliability comes from the harness.** Engineers who master harness engineering will hold irreplaceable value in the agent era.

## References

- [Building Effective Agents — Anthropic](https://www.anthropic.com/engineering/building-effective-agents)
- [Effective Harnesses for Long-Running Agents — Anthropic](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Building Effective AI Coding Agents for the Terminal — arxiv](https://arxiv.org/abs/2603.05344)
- [Replit AI Agent Database Deletion Incident](https://incidentdatabase.ai/cite/1152/)
- [AI Coding Tools Security Exploits — Fortune](https://fortune.com/2025/12/15/ai-coding-tools-security-exploit-software/)
- [Lessons from 2025: The Year "Agent Mitigation" Became a Thing — DevOps.com](https://devops.com/lessons-from-2025-the-year-agent-mitigation-became-a-thing/)
