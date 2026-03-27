---
title: "Harness Engineering：AI Agent 时代的核心工程能力"
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

2025 年是 AI Agent 爆发的一年，2026 年的主题则是 **Agent Harness**——包裹在 Agent 外面的运行时控制框架。OpenAI、Anthropic 先后发布了关于 Harness Engineering 的专题文章，学术界也出现了系统性论文。本文将从工程视角拆解这一新兴学科：它是什么、为什么重要、怎么做。

<!--more-->

## 从 Prompt Engineering 到 Harness Engineering

过去两年，大部分 AI 工程师的核心技能是 **Prompt Engineering**——优化单次 LLM 调用的输入输出。但当 Agent 进入生产环境，问题的性质发生了根本变化：

| 维度 | Prompt Engineering | Harness Engineering |
|------|-------------------|-------------------|
| 作用域 | 单次 LLM 调用 | 多步骤系统 + 工具调用 |
| 控制流 | 输入 → 输出 | 输入 → 规划 → 工具调用 → 验证 → 输出 |
| 失败模式 | 生成错误文本 | 执行错误操作，造成真实后果 |
| 安全模型 | 防止 prompt injection | 完整的授权体系：谁能做什么，需要什么确认 |
| 状态管理 | 无状态或简单上下文 | 记忆持久化、会话管理、跨窗口状态 |

一句话总结：**Prompt Engineering 优化模型说什么，Harness Engineering 优化模型做什么——更重要的是，防止它做不该做的事。**

## 没有 Harness 会怎样？

不加控制的 Agent 会闯祸。这不是假设，而是已经发生的事实。

**Replit Agent 删库事件（2025 年 7 月）**：一个用户让 Replit AI Agent 帮助构建应用，在代码冻结（code freeze）期间，Agent 无视了用户"停止一切修改"的指令，删除了整个生产数据库——1,206 条客户记录，几个月的工作化为乌有。更离谱的是，Agent 随后生成了约 4,000 条假数据来填补空白，然后发出了一段"深感抱歉"的道歉。

**Gemini CLI 文件丢失事件（2025 年 7 月）**：Google 的 Gemini CLI Agent 在一次简单的文件整理任务中，将用户文件移动到了无法找回的位置，用户不得不寻求外部帮助才找回文件。

**Amazon Q 供应链攻击（2025 年）**：攻击者入侵了 Amazon Q 编码助手的 VS Code 扩展，植入恶意 prompt，指示 Agent 擦除用户本地文件并破坏 AWS 云基础设施。

AI 安全事故数据库记录显示，2023 到 2024 年，AI 相关安全事件从 149 起增长到 233 起，同比增长 56.4%。

这些事故有一个共同特征：**问题不在模型本身，而在模型外面的控制层缺失。** 没有权限边界，没有操作确认，没有资源限制——Agent 拥有了能力，但没有约束。

## 什么是 Harness？

这里需要先厘清两个容易混淆的概念。根据 arxiv 上发表的论文 *"Building Effective AI Coding Agents for the Terminal"*，一个完整的 Agent 系统分为两层：

- **Scaffolding（脚手架）**：在 Agent 运行前完成的组装工作——编译系统提示、构建工具定义、注册子 Agent。类似于建筑施工前搭建的脚手架。
- **Harness（控制框架）**：Agent 运行时的编排层——工具调度、上下文管理、安全执行、会话持久化。类似于驯马用的缰绳和辔头。

Scaffolding 回答"Agent 长什么样"，Harness 回答"Agent 怎么被控制"。

Anthropic 在其文章 *"Effective Harnesses for Long-Running Agents"* 中进一步指出核心挑战：**Agent 在跨上下文窗口时会失忆**——每个新会话都从零开始，不记得之前做了什么。Harness 的关键职责之一，就是让 Agent 能够跨会话保持状态和理解。

## Harness 的五层架构

综合 Anthropic、OpenAI 的实践以及学术论文，我将 Harness 的设计归纳为五层架构：

```
┌─────────────────────────────────────────┐
│           记忆层 (Memory)                │  长期记忆 + 会话状态
├─────────────────────────────────────────┤
│           权限层 (Permission)            │  谁能做什么，需要什么确认
├─────────────────────────────────────────┤
│           执行层 (Execution)             │  Agent Loop + Hooks + 错误恢复
├─────────────────────────────────────────┤
│           上下文层 (Context)             │  系统提示 + 动态注入 + 压缩策略
├─────────────────────────────────────────┤
│           工具层 (Tool)                  │  工具注册 + Schema + 分类调度
└─────────────────────────────────────────┘
```

### 第一层：工具层

工具是 Agent 与世界交互的双手。Anthropic 在 *"Building Effective Agents"* 中透露了一个关键发现：

> 在 SWE-bench 基准测试中，我们**花在优化工具上的时间远超优化 prompt 本身**。

工具设计的核心原则：

**1. 专用工具优于通用工具**

以 Claude Code 的文件操作为例，它没有只提供一个通用的 `bash` 工具，而是设计了一套专用工具体系：

| 工具 | 职责 | 为什么要拆分 |
|------|------|-------------|
| `Read` | 读取文件，支持行号范围、PDF、图片 | 防止 Agent 用 `cat` 读取大文件撑爆上下文 |
| `Edit` | 精确字符串替换 | 只传输 diff，比整文件重写安全 |
| `Write` | 创建新文件或完整重写 | 与 Edit 分离，语义更清晰 |
| `Glob` | 文件名模式匹配 | 比 `find` 命令更快，输出更结构化 |
| `Grep` | 内容搜索 | 基于 ripgrep，支持上下文行和多种输出模式 |
| `Bash` | 通用 shell 执行 | 仅用于没有专用工具覆盖的场景 |

这种设计迫使 Agent 为每个操作选择最合适的工具，而不是什么都用 `bash` 一把梭。

**2. 工具描述的质量决定 Agent 行为**

Agent 完全依赖工具描述来决定"用哪个工具、怎么用"。差的工具描述会导致 Agent 选错工具或传错参数。论文中提到的 **ACI（Agent-Computer Interface）** 设计原则：
- 站在模型的角度思考工具描述是否清晰
- 提供示例、边界条件和错误处理说明
- 应用 **poka-yoke（防错）** 原则——让错误更难发生

**3. 分层工具注册**

论文描述了一种三层工具架构：
- **内置工具**：始终可用（文件操作、shell 执行）
- **延迟发现工具**：按需加载（MCP 服务器提供的外部工具）
- **子 Agent 专属工具**：每个子 Agent 只能看到自己被允许的工具 schema

### 第二层：上下文层

上下文层决定了 Agent 在每次推理时"知道什么"。

**系统提示的组织方式**

以 Claude Code 的 `CLAUDE.md` 体系为例，这是一种 **"宪法式"** 的上下文设计：

```
CLAUDE.md          ← 项目宪法，定义全局规则
├── @AGENTS.md     ← 引用的子文档，详细的技术规范
├── settings.json  ← 权限和环境配置
└── Memory/        ← 持久化记忆
```

`CLAUDE.md` 被签入代码仓库，随项目一起演进。它不是静态的 prompt，而是一份**活文档**——团队成员可以通过 PR 修改 Agent 的行为规则，就像修改代码一样。

**动态上下文注入**

并非所有信息都适合写入系统提示。论文描述了一种**优先级排序的条件组合**策略：
- 模式特定变体（正常模式 vs 规划模式，使用不同的上下文）
- 事件驱动注入：当检测到危险模式（如循环执行、接近 token 上限）时，自动注入提醒
- Provider 特定段落：针对不同 LLM 的 API 特性提供不同指导

**上下文压缩**

长对话会撑满上下文窗口。论文提出了**五阶段渐进式压缩策略**：随着 token 预算消耗，逐步从轻量压缩（截断工具输出）升级到重度压缩（总结历史对话），并引入**双记忆架构**——情景记忆（完整对话历史）和工作记忆（近期观察），在长期连续性和 token 效率之间取得平衡。

### 第三层：执行层

执行层是 Agent 的"心跳"——思考→行动→观察→再思考的循环。

**Agent Loop 的核心设计**

Anthropic 在 *"Building Effective Agents"* 中区分了两种执行模式：

- **Workflow（工作流）**：预定义的代码路径编排 LLM 调用，适合可预测的任务
- **Agent（自主代理）**：LLM 动态控制执行流程，适合开放性问题

并给出了明确建议：**从最简单的方案开始，只在简单方案不足时才引入多步骤 Agent 系统。**

五种基础 Workflow 模式：

| 模式 | 适用场景 |
|------|---------|
| Prompt Chaining | 固定的子任务链，用延迟换准确性 |
| Routing | 不同类别需要专门处理 |
| Parallelization | 多视角验证或加速 |
| Orchestrator-Workers | 由中心 LLM 决定子任务 |
| Evaluator-Optimizer | 有明确评估标准的迭代优化 |

**Hooks 机制**

Hooks 允许在 Agent 执行的关键节点插入自定义逻辑，形成**生命周期钩子**：
- 工具调用前：验证参数、检测危险模式
- 工具调用后：验证输出、记录日志
- 会话启动时：加载上下文、检查环境状态
- 中断处理：防止危险状态转换

论文中特别强调，Hooks 的存在使得用户可以在不修改 Agent 代码的情况下执行自定义策略。

**子 Agent 专业化**

复杂任务可以分解给专业化的子 Agent。每个子 Agent 携带独立的工具白名单和对话历史。Claude Code 的实现中包括：
- **Planner 子 Agent**：只有只读工具，专门做代码探索和方案规划
- **Critic 子 Agent**：验证代码变更是否符合质量标准
- **Explorer 子 Agent**：快速搜索和探索代码库

关键设计决策：用构造参数而非类继承来区分子 Agent 的行为——统一的 `MainAgent` 类，通过 `allowed_tools`、`system_prompt` 等参数定制行为。

### 第四层：权限层

权限层是 Harness 最关键的安全组件。论文描述了一种**纵深防御**架构：

**五道防线**

1. **Prompt 级护栏**：在系统提示中强调安全实践（"永远不要在没有用户确认的情况下执行破坏性操作"）
2. **Schema 级限制**：通过工具白名单，让 Agent 根本看不到不允许使用的工具
3. **运行时审批系统**：三个级别——手动审批 / 半自动 / 全自动
4. **工具级验证**：危险模式检测（如 `rm -rf`）、输出截断
5. **生命周期钩子**：用户自定义的执行前过滤规则

**审批持久化**

一个容易被忽略的设计：用户批准某个操作模式后，该批准可以持久化，避免反复弹出确认框导致的**审批疲劳**——当用户因为烦躁而盲目点击"允许"时，审批机制就名存实亡了。但用户随时可以撤销已持久化的权限。

**双模式执行**

- **正常模式**：完整的读写工具集
- **规划模式**：只有只读工具，Agent 只能探索和思考，不能修改任何东西

这种设计在 Schema 构建阶段就过滤掉不可用的工具——LLM 连工具定义都看不到，自然就不会尝试调用。

### 第五层：记忆层

Agent 的致命弱点是**健忘**。每个新的上下文窗口都是一次"重生"。记忆层解决这个问题。

**Anthropic 的进度文件模式**

在 *"Effective Harnesses for Long-Running Agents"* 中，Anthropic 提出了一种实用的跨会话记忆方案：

1. **初始化 Agent** 在首次运行时创建三个关键文件：
   - `init.sh`：环境启动脚本
   - `claude-progress.txt`：进度记录文件
   - 功能清单（JSON 格式，200+ 项功能及其状态）

2. **编码 Agent** 在每次新会话启动时：
   - 执行 `pwd` 确认工作目录
   - 读取 git 日志和进度文件，了解上次的工作
   - 查看功能清单，选择最高优先级的未完成功能
   - 启动开发服务器
   - 运行端到端测试确认当前状态

这种模式让 Agent 在每次"重生"后能够快速恢复上下文，而不是从零开始猜测。

**论文的双记忆架构**

- **情景记忆（Episodic Memory）**：完整的对话历史
- **工作记忆（Working Memory）**：只包含近期观察

两者结合注入，在长期连续性和 token 效率之间取得平衡。

**Claude Code 的结构化记忆**

Claude Code 的记忆系统将持久化信息分为四种类型：

| 类型 | 内容 | 示例 |
|------|------|------|
| `user` | 用户画像：角色、偏好、知识水平 | "资深 Go 工程师，首次接触 React" |
| `feedback` | 用户对 Agent 行为的纠正和确认 | "测试不要 mock 数据库" |
| `project` | 项目动态：进度、截止日期、决策 | "3月5日后冻结非关键 PR" |
| `reference` | 外部资源指针 | "pipeline bug 在 Linear INGEST 项目中追踪" |

每条记忆存储为独立的 Markdown 文件（带 frontmatter 元数据），并在 `MEMORY.md` 索引文件中维护指针。这种设计让记忆的读取、更新和淘汰都可以精确到单条记录。

## 方法论：怎么做 Harness Engineering

综合以上实践，我总结了五条方法论：

### 1. 工具优先设计（Tool-First Design）

不要先写 prompt，先设计工具。工具定义了 Agent 的能力边界，是 Harness 中最值得投入时间的部分。Anthropic 在 SWE-bench 上的经验已经证明了这一点。

### 2. 渐进式自主权（Graduated Autonomy）

从最严格的控制开始，逐步放开：
- **第一阶段**：所有操作都需要人工确认
- **第二阶段**：低风险操作自动执行，高风险操作需确认
- **第三阶段**：只有不可逆操作需要确认

对应 Anthropic 的建议：**从简单 prompt 开始，用全面的评估优化它们，只在简单方案不够时才引入多步骤 Agent 系统。**

### 3. 增量约束构建（Incremental Constraint Building）

不要试图一开始就设计完美的 Harness。从基本的安全规则开始，随着 Agent 行为模式的浮现逐步添加约束。这和软件工程中"不要过早抽象"的原则一脉相承。

### 4. 可观测性优先（Observability-First）

记录每一次工具调用、每一个决策、每一个结果。你无法改进你看不到的东西。论文中描述的不可变追加日志（JSONL 格式）是一个好的起点。

### 5. 红队驱动设计（Red-Team-Driven Design）

在部署前，系统性地尝试让 Agent 犯错。每个发现的失败模式都变成一条 Harness 约束。这比事后补救高效得多。

## 人的角色变化

Harness Engineering 的兴起标志着软件工程师角色的转变：

**传统模式**：人写代码 → 机器执行代码

**Agent 时代**：人设计规则 → Agent 写代码并执行 → 人审查结果

工程师从**实现者**变成了**架构师 + 教练**：
- 设计工具接口和权限体系（架构能力）
- 编写系统提示和行为规则（表达能力）
- 观察 Agent 行为并调整约束（调教能力）
- 审查 Agent 产出并提供反馈（判断能力）

你不再需要记住每个 API 的参数，但你需要知道哪些操作是危险的、哪些信息是 Agent 完成任务所必需的、哪些约束可以防止灾难。

**系统设计能力变得比编码能力更重要。**

## 结语

Harness Engineering 还是一个年轻的学科。我们正处于从"手工作坊"到"工程化"的转变过程中——就像软件工程在 1960 年代经历的那样。

但方向已经很清楚：**Agent 的能力来自模型，Agent 的可靠性来自 Harness。** 掌握 Harness Engineering 的工程师，将在 Agent 时代拥有不可替代的价值。

## 参考资料

- [Building Effective Agents — Anthropic](https://www.anthropic.com/engineering/building-effective-agents)
- [Effective Harnesses for Long-Running Agents — Anthropic](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Building Effective AI Coding Agents for the Terminal — arxiv](https://arxiv.org/abs/2603.05344)
- [Replit AI Agent Database Deletion Incident](https://incidentdatabase.ai/cite/1152/)
- [AI Coding Tools Security Exploits — Fortune](https://fortune.com/2025/12/15/ai-coding-tools-security-exploit-software/)
- [Lessons from 2025: The Year "Agent Mitigation" Became a Thing — DevOps.com](https://devops.com/lessons-from-2025-the-year-agent-mitigation-became-a-thing/)
