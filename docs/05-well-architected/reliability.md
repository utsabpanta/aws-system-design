# Reliability

> **One-line summary.** The workload performs its intended function correctly and consistently — including when its dependencies don't.

## TL;DR
- Reliability is about *graceful degradation*, not zero failure. Plan for failure, measure recovery, design so the customer sees the smallest possible impact.
- Multi-AZ is table stakes. Multi-Region is an explicit trade-off (RTO/RPO vs cost vs operational complexity) — make the decision deliberately.
- Define your RTO and RPO before you pick your DR strategy. The strategy follows from the numbers, not the other way around.
- Auto-recovery beats human recovery. Health checks + replacement + retries with backoff handle 90% of transient failures with no page.
- Quotas, dependencies, and noisy neighbors are the three load-bearing constraints most teams forget until they hit them.

## What the pillar is about

Reliability is the pillar that asks "when something goes wrong, what happens?" It covers fault isolation, recovery, scaling under load, change management, and the relationship between your service and the dependencies it sits on top of.

The cloud doesn't make systems reliable. It makes *building* reliable systems cheaper than ever before — because the primitives (Multi-AZ databases, auto-scaling groups, managed load balancers) handle the parts that used to require a SRE team. What it doesn't do is design your application for failure; that's still on you.

## AWS's five design principles

1. **Automatically recover from failure.** Health checks, auto-scaling group instance replacement, RDS Multi-AZ failover, Lambda retries. A human is the fallback, not the primary mechanism.
2. **Test recovery procedures.** Chaos experiments, game days, scheduled failover drills. The first time you fail over to the standby is not a 3 AM page.
3. **Scale horizontally to increase aggregate availability.** Replace one big thing with many small things; the failure of any one becomes a partial degradation, not an outage.
4. **Stop guessing capacity.** Auto-scaling on the right signals (queue depth, request rate, custom metrics) replaces capacity planning spreadsheets.
5. **Manage change in automation.** Infrastructure as code, canary deploys, automatic rollback. Manual changes are the single biggest source of outages.

## RTO and RPO

These two numbers shape every DR conversation:

- **RTO (Recovery Time Objective)** — how long you're allowed to be down. "Two hours" means by hour 2:01 you're back.
- **RPO (Recovery Point Objective)** — how much data you're allowed to lose. "Five minutes" means you can lose the last 5 minutes of writes when you fail over.

There's no free lunch: every nine of recovery costs roughly an order of magnitude more in infrastructure and operations. Define the numbers per workload — your billing service and your blog have very different requirements.

The four canonical DR strategies (low to high cost):

| Strategy | RTO | RPO | Cost | What it is |
|---|---|---|---|---|
| Backup & restore | Hours–days | Hours | $ | Backups in another Region, infrastructure recreated from IaC on failure. |
| Pilot light | Tens of minutes | Minutes | $$ | DB replicated to standby Region; compute scaled down to near-zero, scaled up on failover. |
| Warm standby | Minutes | Seconds | $$$ | Full stack running at reduced capacity in standby Region; scale up on failover. |
| Multi-region active-active | Seconds | Near-zero | $$$$ | Traffic routed to both Regions continuously; failover is a routing change. |

The cliff is between Pilot Light and Warm Standby — the second always costs at least double the first because you're paying for full standby compute. Multi-Region active-active also adds data-consistency complexity that most workloads don't need.

See [`docs/02-patterns/disaster-recovery-strategies.md`](../02-patterns/disaster-recovery-strategies.md) and [`docs/02-patterns/multi-region-active-active.md`](../02-patterns/multi-region-active-active.md) for the AWS implementations.

## Key practices

### Redundancy
- **Multi-AZ everything that matters.** RDS Multi-AZ, Aurora (always multi-AZ), DynamoDB (always multi-AZ in single-Region, optional Global Tables for multi-Region), ALB across 2+ AZs, ASG across 2+ AZs.
- **Stateless application tier.** Sessions in DynamoDB/ElastiCache, not on disk. Then any instance can serve any request, and instance failure is invisible.
- **Replicated stateful tier.** Synchronous replication inside a Region (the default for Multi-AZ RDS), asynchronous across Regions (with the lag accepted as your RPO).

### Fault isolation
- **Cell-based architecture** (the Netflix/Amazon retail pattern). Partition customers into independent "cells," each a complete stack. A bad deploy or a poison-pill request blows up one cell, not the service.
- **Bulkheads.** Separate thread pools / connection pools / queues per dependency, so a slow dependency can't starve the rest of the system.
- **Circuit breakers.** When a downstream is failing, stop calling it for a window — fail fast, recover when health returns.

### Self-healing
- **Health checks** at every layer: ELB target health, ECS container health, Route 53 health checks for DNS failover.
- **Auto Scaling Group instance replacement.** Failed instance health check → ASG terminates and replaces, no human involvement.
- **Lambda + EventBridge** for cross-service self-healing — alarm fires, Lambda runs the remediation runbook.

### Retries and timeouts
- **Every network call has a timeout.** No exceptions. The default in most SDKs is "never," which is the wrong default.
- **Retries with exponential backoff and jitter.** Without jitter, retries synchronize across the fleet and cause retry storms.
- **Idempotent operations only.** If you can't safely retry, you can't build a reliable system. See [`docs/02-patterns/idempotency.md`](../02-patterns/idempotency.md).

### Dependency mapping
A service's reliability is at most the product of the reliability of its hard dependencies. Two 99.9% dependencies multiplied is 99.8% — you can't be more reliable than the chain.

Practices:
- **Identify hard vs soft dependencies.** Can the request succeed if this dependency is down? If yes, it's soft (recommendation engine, A/B test config); failure should degrade, not fail. If no, it's hard (auth, primary DB) — improving these is the only way to improve your composite reliability.
- **Budget per dependency.** "We can afford 0.1% errors from the auth service; if it goes higher, we either invest in their reliability or remove the dependency."

### Quotas as constraints
Every AWS service has account-level quotas. The defaults are sized for small workloads, not yours. The reliability failure mode: you hit a quota in production, get throttled, and the whole service degrades.

Practices:
- Inventory quotas for every service in your design.
- Use Service Quotas + CloudWatch alarms to alert at 70–80% utilization.
- Pre-raise the obvious ones (Lambda concurrency, EC2 vCPUs, EBS volume size) before you need them.

### Change management
Most outages are self-inflicted via deploys. Mitigations:
- **Canary deploys.** Roll to 1% → 10% → 100% with alarm-gated promotion.
- **Feature flags** decoupled from deploys (AppConfig). Roll out the code dark, flip the flag separately.
- **Schema changes** that are forward-compatible (add-only, rename-via-double-write). See [`docs/02-patterns/`](../02-patterns/) for evolutionary schema patterns.

## AWS services that support this pillar

- **Auto Scaling** (EC2, ECS, application auto-scaling) — capacity automation.
- **ELB (ALB/NLB)** — load balancing with health-check based instance removal.
- **Route 53** — DNS, health checks, multi-Region failover routing.
- **RDS Multi-AZ, Aurora, DynamoDB Global Tables** — replicated stateful tier.
- **S3** — eleven 9s of durability, cross-Region replication.
- **CloudFront, Global Accelerator** — edge resilience and intelligent routing around outages.
- **SQS, EventBridge, Step Functions** — durable async coupling.
- **Backup, AWS Elastic Disaster Recovery (DRS), Resilience Hub** — backup, DR orchestration, RTO/RPO tracking.
- **CloudWatch alarms, EventBridge, Lambda** — automated remediation pipelines.
- **Fault Injection Service (FIS)** — chaos engineering, scheduled failure injection.

## Common anti-patterns

- **Single-AZ databases in production.** Even the dev environment should mirror the prod topology when it's affordable.
- **No timeouts on network calls.** The "infinite hang" is the most common cause of cascading failures.
- **Retry without backoff or jitter.** Synchronous retry storms can take down the dependency you're retrying against.
- **Health checks that lie.** "Is the process running" is not a health check; "can it serve a real request" is.
- **Untested DR plans.** A DR runbook that's never been executed is a fiction. Schedule a quarterly failover drill.
- **Manual scaling.** "We'll scale up before the marketing campaign" doesn't survive a 9 AM Slack panic.
- **Single-Region everything, but claiming "high availability."** Multi-AZ ≠ multi-Region. Pick a target and design to it; don't conflate them.

## Pairs well with
- [Operational Excellence](operational-excellence.md) — the deploys and observability that make reliability targets real.
- [Performance Efficiency](performance-efficiency.md) — performance regressions are reliability events for users on tight SLOs.
- `docs/02-patterns/multi-region-active-active.md`, `multi-region-active-passive.md`, `disaster-recovery-strategies.md`.
- `docs/02-patterns/circuit-breaker.md`, `bulkhead.md`, `idempotency.md`.

## Further reading
- AWS Well-Architected Framework — Reliability pillar whitepaper.
- AWS Resilience Hub documentation.
- *Release It!* (Michael Nygard) — circuit breakers, bulkheads, the stability patterns vocabulary.
- *Chaos Engineering* (Casey Rosenthal, Nora Jones) — game day and chaos experiment design.
- Amazon Builders' Library — Amazon's own essays on reliability practices.
