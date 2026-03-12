---
title: "From Monolith to Microservices: The Redistribution of Complexity"
date: 2026-03-12T11:53:08+08:00
slug: complexity-redistribution-from-monolith-to-microservices
categories:
- Engineering
featured: true
tags:
- Microservices
---
Microservices are often introduced with a deceptively simple narrative: monoliths become too complex, microservices make systems easier to manage, therefore system evolution naturally moves from monolith to microservices. The problem with this narrative is not that it is entirely wrong. The problem is that it hides the more important truth: microservices usually do not remove complexity. They redistribute it.

In a monolith, complexity is concentrated inside the codebase. It shows up as coupling between modules, risky deployments, a rigid technology stack, and increasing coordination costs inside one delivery unit. Microservices attempt to break that delivery unit apart so teams can evolve parts of the system independently. But once the split happens, complexity does not disappear. It moves from in-process calls, local transactions, and shared code into service boundaries, network uncertainty, data consistency, runtime governance, and organizational coordination.

<!--more-->

That is why the real question is not whether microservices are "better" in the abstract. The real question is whether a different distribution of complexity fits the current business and the current organization.

## The problem with monoliths is not merely size

Teams often describe monolith problems as a matter of code volume. That is only partially true. The deeper problem is that different kinds of change are coupled into the same delivery unit.

When orders, payments, inventory, and promotions all live in one process, engineers benefit from a number of defaults that are easy to underestimate. Calls are local. Transactions are straightforward. Debugging paths are short. Operational behavior is comparatively deterministic. A monolith may become difficult to maintain, but its runtime model is often much easier to reason about.

The tension appears when the system and the organization grow. Different domains start to move at different speeds. One hot area forces frequent releases of the entire application. One local traffic hotspot forces the whole application to scale. One poor-quality change increases regression risk for everyone else. The core issue is not that all code lives together. It is that too many unrelated changes are forced to move together.

Microservices try to solve exactly this problem. They separate a large delivery unit into smaller business-aligned units so ownership, deployment, and scaling can happen more locally.

## Microservices optimize the location of complexity, not the total amount

Many misunderstandings around microservices come from the assumption that if a system is split into smaller pieces, overall complexity must go down. In practice, decomposition often makes local reasoning easier while making global reasoning more dependent on boundary design and operational discipline.

Inside a monolith, a module calling another module raises familiar design questions: is the interface sound, are dependencies pointing in the right direction, does the transaction boundary still hold. In a microservice system, the same interaction immediately creates new concerns: timeouts, retries, idempotency, traceability, version compatibility, and eventual consistency.

In other words, microservices do not automatically make a hard system easier. They expose complexity that used to remain hidden inside a single process and require the team to handle it explicitly. For strong teams, that exposure is useful because it clarifies boundaries and ownership. For weak teams, it turns "hard to understand code" into "hard to explain system behavior."

## Where the complexity moves

### 1. From module boundaries to service boundaries

When a module boundary inside a monolith is wrong, it can often be corrected gradually through refactoring. When a service boundary is wrong, the cost is much higher because the boundary is now embedded in APIs, databases, message contracts, and team ownership.

This is why many failed microservice efforts do not fail because services are too large. They fail because boundaries were frozen too early and drawn for the wrong reasons: by database tables, by technical layers, or by org chart convenience instead of business capability and change patterns. What used to be internal coupling inside a monolith becomes chronic cross-service chatter, unclear ownership, and unstable contracts.

Service boundaries are not mainly a code decomposition problem. They are a domain modeling problem.

### 2. From local calls to network uncertainty

In-process calls fail rarely. Network calls are uncertain by default. Requests time out. Connections flap. Peers fail partially. Retries duplicate writes. A distributed path introduces uncertainty even when every individual service is correct.

The difficult part is that this rarely appears only as dramatic outages. More often it appears as gray failure: intermittent latency, isolated node behavior, occasional duplicate processing, cascading slowdowns under load. These are not edge cases in microservices. They are part of the normal operating model.

That is why timeouts, retries, circuit breaking, rate limiting, isolation, and graceful degradation are not optional governance features. They are part of the application semantics once the application becomes distributed.

### 3. From local transactions to distributed consistency

One of the biggest practical advantages of a monolith is that many business constraints can rely on local transactions and direct queries against the same database. Success and rollback have relatively clear meanings.

Once each service owns its own data, many guarantees previously enforced by the database must be rebuilt at the application level. After an order is created, when exactly should inventory be considered reserved. After payment succeeds, how is order state updated. When a downstream step fails, which compensating action is authoritative. These questions do not become simpler after decomposition. They become persistent system design problems.

This is why "a database per service" is better understood as the beginning of the problem rather than the completion of a principle. The hard part is not splitting the database. The hard part is redefining consistency, recovery, replay, and auditability in a world where local ACID boundaries no longer cover the business flow.

### 4. From code coordination to platform dependency

In monoliths, the main object of coordination is the codebase. In microservices, it gradually becomes the platform. Service discovery, configuration management, tracing, log aggregation, deployment pipelines, release controls, identity systems, and contract management together form the control plane of the architecture.

This is the part many teams underestimate. Splitting services is rarely the hardest step. The hard step is building an environment in which dozens of services can run in a way that is observable, operable, auditable, and reversible. Teams often feel fine early in a microservice journey because the system is still small enough for human memory and ad hoc communication to compensate for missing infrastructure. Once service count, team count, and deployment frequency grow together, the lack of control-plane capability turns into noisy alerts, fragile releases, and expensive incident analysis.

Microservices are therefore not just an application architecture decision. They are also a platform maturity decision.

### 5. From shared code to shared constraints

In a monolith, collaboration failures usually show up as merge conflicts, release conflicts, or architectural disagreements. In microservices, those same failures become more subtle: who owns an API contract, when a field can change meaning, who is accountable for latency across a call chain, who pays for cross-service failures.

This happens because microservices replace shared implementation with shared protocol. Shared implementation creates tight coupling, but it also makes breakage visible early. Shared protocol can appear clean for quite a while, until a consumer upgrades late, a field drifts semantically, or an SLA has been silently violated long enough for the system to become brittle.

Microservices therefore demand more than team-level coding autonomy. They demand durable ownership, disciplined contract evolution, and governance strong enough to maintain shared constraints over time.

## Why many teams get slower after decomposition

It is common to see teams gain theoretical independence after adopting microservices while actual delivery becomes slower. The reason is usually not a single bad tool choice. It is that the team misjudged the kind of complexity it would have to absorb.

One common mistake is treating code splitting as architectural progress. Multiple repositories do not imply better boundaries. HTTP or RPC endpoints do not imply sound responsibilities. Without business-aligned boundaries, distributed systems simply replicate monolithic confusion at a higher operational cost.

Another mistake is treating independent deployment as pure upside. Independent releases do reduce full-system rollout frequency, but they also introduce compatibility management, release coordination, environment drift, rollback complexity, and a larger surface for partial failure.

A third mistake is overestimating governance capacity. Microservices require teams not only to write business code, but also to maintain contracts, reason about distributed failure, build observability, and manage production change safely. Teams that never established these disciplines in a monolith rarely acquire them automatically through decomposition.

## What microservices truly depend on

If there is one factor that most strongly predicts whether microservices will work, it is not the number of services. It is the strength of the control plane around them.

Without service discovery, configuration governance, tracing, logging, metrics, release controls, identity boundaries, and contract discipline, a microservice system is merely a set of processes talking to one another. The architecture becomes meaningful only when those processes can be managed as a coherent operational system.

This is why mature microservice organizations often evolve into a layered collaboration model: business engineering builds domain capabilities, platform engineering consolidates shared infrastructure, and SRE turns operational risk into an engineering discipline. Remove any one of these layers and microservices tend to collapse into nominal service separation without real operational leverage.

Microservices are therefore not a shortcut for teams that are still struggling with engineering discipline. They are more often a later-stage tool for teams that already have enough discipline to redistribute complexity safely.

## When microservices are worth it

None of this means microservices are a mistake. They can deliver real value when the prerequisites are present: domains have genuinely different rates of change, scaling characteristics diverge meaningfully, ownership is stable, observability and release engineering are already established, and the organization is willing to invest continuously in platform capability.

In that environment, microservices can make both technical and organizational sense because they align system boundaries with responsibility boundaries.

But if requirements are still volatile, domain boundaries are still shifting, infrastructure is still thin, and production safety depends mostly on individual experience, a modular monolith is usually the more pragmatic choice. That is not a conservative fallback. It is often the right way to control complexity until the organization is ready to absorb a different kind of it.

The more reliable evolution path is usually not "the monolith hurts, therefore split it." It is "make the monolith modular, clarify boundaries, stabilize delivery, and then extract the parts that truly need independent evolution."

## Conclusion

Moving from a monolith to microservices is not a movement from backward to advanced architecture. It is a movement from one distribution of complexity to another. Monoliths compress complexity inside code and delivery boundaries. Microservices spread complexity across networks, data flows, platforms, and team interfaces.

That makes microservices more flexible, but also more dependent on governance maturity. The key question is therefore not whether the system is large enough. The key question is whether the organization can reliably absorb the complexity that decomposition introduces.

If the answer is no, microservices will not make the system simpler. They will only turn visible code-level complexity into harder-to-diagnose system-level complexity.
