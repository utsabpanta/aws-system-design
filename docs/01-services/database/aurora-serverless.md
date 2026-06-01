# Aurora Serverless

> **One-line summary.** Aurora that auto-scales capacity in fine-grained units (Aurora Capacity Units, ACUs) without you running it as a fleet of fixed instances. **Renamed from "Aurora Serverless v2" to "Aurora Serverless" in April 2026.**

## TL;DR

- The serverless flavor of Aurora MySQL and Aurora PostgreSQL. Capacity scales between a min and max in **0.5-ACU steps** based on live load.
- Now scales **all the way down to 0 ACUs** with an automatic pause-and-resume — set a min of 0 ACUs and an idle timeout, and you pay nothing for compute during inactivity. Scale-up after pause is on the order of seconds.
- Max **256 ACUs** per writer. AWS recently bumped default scaling rate ~45% faster across all clusters.
- **April 2026 rename:** "Aurora Serverless v2" → "Aurora Serverless" (no migration required for existing users; v1 had been EOL'd previously).
- Right for **spiky** or **uncertain** workloads, multi-tenant SaaS isolation per tenant, dev/test environments, and any workload where a fixed-size instance overprovisions most of the time.

## When to use it

- Bursty workloads that idle for long stretches between peaks (B2B SaaS, internal tools, dev/test environments).
- Multi-tenant SaaS where you want database-per-tenant isolation but can't afford a fixed instance per tenant.
- Unpredictable or new workloads where you'd rather autoscale than guess instance size.
- Workloads where you want to scale to zero overnight or weekends with **min ACU = 0**.

## When NOT to use it

- Steady, predictable, high-utilization workloads — fixed Aurora provisioned instances on Reserved Instances are typically cheaper at ≳60% utilization.
- Very-low-latency cold-path scenarios — scaling up from a paused state takes seconds; pre-warming with `min ACU > 0` avoids it but costs more.
- Workloads needing very large per-writer capacity (> 256 ACUs ≈ very large vCPU/memory) — provisioned Aurora has bigger instance options.
- Engine versions Aurora Serverless doesn't support yet — always check the current support matrix before committing.

## Key concepts

**Aurora Capacity Unit (ACU)** — the billable unit, roughly 2 GiB memory + matched CPU and network. Capacity scales in **0.5-ACU increments**. A cluster has `min_capacity` and `max_capacity` (in ACUs); Aurora autoscales between those continuously based on CPU, memory, and active connections.

**Scaling to 0 ACUs (auto-pause).** Set `min_capacity = 0` and `seconds_until_auto_pause` (300 s – 86,400 s, i.e., 5 min – 24 h). After the idle period, the writer pauses; compute charges stop. Storage / backup charges continue. Next connection wakes the cluster automatically — first query takes a few seconds; subsequent queries run normally.

**Replicas.** Aurora Serverless supports up to 15 readers, same as provisioned Aurora. Readers can also be Serverless (independent min/max ACUs per replica) or provisioned. Mixed clusters are supported.

**Storage layer is the same as provisioned Aurora.** 6-way multi-AZ replication, the same durability and read-after-write guarantees, the same backup model.

**Endpoints.** Same writer / reader / custom endpoints as provisioned Aurora.

**Compatibility.** Most Aurora MySQL and Aurora PostgreSQL features work on Serverless; some advanced features (e.g., Aurora Global Database, certain extensions, Backtrack) have evolving Serverless support. Check the current matrix.

**Connection management.** RDS Proxy is recommended in front of Aurora Serverless for the same reason as provisioned Aurora — sudden client scale-out can exhaust connection slots, and Proxy pools them.

**Cold-start (when scaling from 0)** — typically a few seconds to wake the cluster on first connection. Persist `min_capacity > 0` (e.g., 0.5 ACU) if first-query latency matters and the workload doesn't idle long enough to justify the saving.

## Pricing model

- **ACU-hours** — per second, billed in 0.5-ACU increments. Roughly proportional to instance class price; the saving vs provisioned comes from actually scaling down when load drops.
- **Paused (0 ACU)** — no compute charge; storage and backups still bill.
- **Storage and I/O** — same as provisioned Aurora. **Aurora I/O-Optimized** storage class works with Serverless and is often the right choice for write-heavy or analytical workloads.
- **Reserved capacity for Serverless** — committed ACU-hours at a discount.

The economic argument: for workloads at < ~60% steady-state utilization, Aurora Serverless typically wins on cost vs a fixed-size provisioned instance. For sustained near-100% workloads, provisioned with Reserved Instances wins.

## Quotas & limits

- **ACU range** — 0 (or 0.5) up to **256** per writer/reader.
- **Auto-pause idle window** — 5 min to 24 h.
- **Readers** — up to 15 per cluster.
- **Engine versions** — specific MySQL / PostgreSQL versions supported; the supported list changes — check before committing.
- **Aurora Global Database with Serverless** — support has improved over time; verify current state for your version.

## Common pitfalls

- **`min ACU > 0` set "for safety."** Pays for capacity 24/7. If your workload genuinely has idle periods, scale-to-0 with a sensible idle window wins.
- **`max ACU` too low.** Caps your scale-out. Watch CloudWatch's `ACUUtilization` near 100% as a signal to raise the max.
- **Treating ACU like an EC2 instance size.** ACU isn't a class; it's a continuous capacity unit. Don't reason about it as "I want a 16-vCPU box" — reason about it as "I'll budget up to 64 ACUs of headroom at peak."
- **No RDS Proxy.** Serverless clusters that auto-scale can briefly choke on connection bursts during scaling events; Proxy buffers them.
- **Cold first-query as a critical-path problem.** A consumer-facing API where the first query after a quiet period must be sub-100ms isn't a great fit for scale-to-0. Use `min_capacity = 0.5` to keep the cluster warm.
- **Underestimating storage / backup cost during pauses.** Compute is free, storage isn't. Long-paused clusters with large datasets aren't free overall.
- **Forgetting the rename.** Documentation and tooling will straddle "Aurora Serverless v2" and "Aurora Serverless" for a while; they're the same service post-April-2026.

## Pairs well with

- [Aurora](aurora.md) — the provisioned counterpart.
- [RDS Proxy](rds.md) — connection pooling.
- **AWS Backup** — vault-locked retention.
- **Performance Insights** — observability.
- **AppConfig + feature flags** — quietly dial workloads on/off, letting Serverless scale accordingly.

## Pairs well with these repo pages

- [Aurora](aurora.md), [RDS](rds.md), [DynamoDB](dynamodb.md).
- [Cost Optimization pillar](../../05-well-architected/cost-optimization.md) — Aurora Serverless's scale-to-0 is one of the cleanest cost optimizations available.

## Further reading

- [Aurora Serverless documentation](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless-v2.html).
- [Scaling to 0 ACUs with auto-pause and resume](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless-v2-auto-pause.html).
- [How ACU min/max ranges affect scaling](https://aws.amazon.com/blogs/database/understanding-how-acu-minimum-and-maximum-range-impacts-scaling-in-amazon-aurora-serverless-v2/).
- [Aurora Serverless requirements and limitations](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless-v2.requirements.html).
- [Faster scaling announcement (2025)](https://aws.amazon.com/blogs/database/aurora-serverless-faster-performance-enhanced-scaling-and-still-scales-down-to-zero/).
