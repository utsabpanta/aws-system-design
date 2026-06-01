# Aurora

> **One-line summary.** AWS's purpose-built relational engine — MySQL- and PostgreSQL-compatible — with a custom distributed storage layer that gives you 6-way multi-AZ replication, fast failover, and up to 15 readers off a single source of truth.

## TL;DR

- A re-engineered storage layer + a familiar SQL engine. **Storage is logged to six copies across three AZs**; the database instance is just a compute node above it.
- Failover is **single-digit seconds** (vs 30–120 s on RDS Multi-AZ). Up to **15 low-lag read replicas** share the same storage — no async replica lag.
- **Aurora Global Database** replicates across Regions with typical RPO < 1 s, RTO ~1 min on planned failover; supports up to 5 secondary Regions.
- Two storage classes: **standard** (the default; cheaper per GB, charged per I/O) and **I/O-optimized** (flat per-instance pricing; better at high I/O workloads — switch above ~25% I/O cost share).
- Aurora Serverless is documented separately — see [`aurora-serverless.md`](aurora-serverless.md).

## When to use it

- High-availability MySQL or PostgreSQL on AWS with read scale and fast failover.
- Apps that want SQL semantics but expect to grow into multi-Region (Aurora Global Database).
- Workloads that benefit from cheap point-in-time clones (zero-copy at first write).
- Migrating from on-prem MySQL / PostgreSQL where the operational ceiling of vanilla RDS doesn't cut it.

## When NOT to use it

- Engines other than MySQL / PostgreSQL — use RDS.
- Workloads small enough that the Aurora premium isn't justified — RDS PostgreSQL with Multi-AZ DB cluster can be cheaper for small writers.
- True horizontal-scale writes (shard-the-keyspace patterns) — Aurora is a single-writer cluster (with Global Database write forwarding as a limited workaround). For multi-writer global, you're looking at DynamoDB Global Tables MRSC or sharding above Aurora.
- Workloads that need a specific extension / feature only available in vanilla Postgres — check the [Aurora PostgreSQL extensions list](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraPostgreSQLReleaseNotes/AuroraPostgreSQL.Extensions.html) first.

## Key concepts

**Cluster vs instance.** An Aurora cluster is the storage layer plus a primary writer instance plus 0–15 reader instances. The cluster has stable endpoints: **writer endpoint** (always routes to the current primary), **reader endpoint** (load-balanced across readers), **custom endpoints** (pinned subsets), **instance endpoints** (direct).

**Storage layer.** A distributed, log-structured store striped in 10 GB segments across 3 AZs with 6 copies (2 per AZ). Quorum reads (3 of 6) and writes (4 of 6) tolerate AZ loss + one additional segment loss with no data loss and no read interruption.

**Replicas.** Up to 15 readers per cluster, replicating via the shared storage (not log shipping) — replica lag is typically tens of milliseconds, not seconds. Promotion of a reader to writer happens in seconds; reader instances are eligible promotion targets ordered by priority tier.

**Storage classes:**

- **Aurora Standard** — pay per GB-month + per I/O. Cheaper when I/O is light.
- **Aurora I/O-Optimized** — flat per-instance pricing, no per-I/O charge. Cheaper above ~25% of total cost being I/O. The right default for analytical or write-heavy workloads.

**Aurora Global Database.** Cross-Region replication via dedicated storage-layer replication (not logical replay). Typically < 1 s lag. One primary Region, up to **5 secondary Regions**. **Managed planned failover** in ~1 min; **detach and promote** for unplanned failover (acceptable up to the lag = your RPO).

**Backtrack** (Aurora MySQL only) — rewind the cluster to a previous point without restoring from backup. Useful for accidental-write recovery.

**Cloning.** Zero-copy clones share storage with the source until first write — instant, near-free. Great for "give me a prod-like environment for this test."

**Performance.** Modern Aurora versions are several times faster than equivalent vanilla MySQL/PostgreSQL on the same hardware, primarily due to the storage layer and parallel query.

**Aurora Optimized Reads** (PostgreSQL) — local NVMe instance store on the reader node caches hot data, speeding read-heavy workloads.

**Aurora Limitless Database** (preview / GA in subsets) — horizontal-scale PostgreSQL on top of Aurora, exposing a single endpoint over distributed shards.

## Pricing model

- **Instance** — per second, by class (`db.r7g.xlarge`, `db.m8g.4xlarge`, etc.). RIs / Savings Plans apply.
- **Storage** — per GB-month of actual data stored (storage auto-grows).
- **I/O** — per million IOs (Aurora Standard only; Aurora I/O-Optimized doesn't bill per-I/O).
- **Backup storage** — included up to size of cluster; beyond that, per GB-month.
- **Global Database** — replicated writes billed per million; secondary Region storage + instances billed normally.
- **Data transfer** — same AWS rules.

Picking I/O-Optimized vs Standard is one of the biggest cost levers. Check the I/O percentage in the cost report — over 25% means I/O-Optimized is cheaper.

## Quotas & limits

- **Readers per cluster** — 15.
- **Max storage** — 128 TiB.
- **Backtrack window** (MySQL) — up to 72 hours.
- **Global Database secondary Regions** — up to 5.
- **Clusters per Region** — 40 default.
- **Aurora Limitless Database** — preview / limited engine versions, check current GA Regions.

## Common pitfalls

- **Aurora Standard for I/O-heavy workloads.** Switch to I/O-Optimized once I/O is a meaningful share of cost.
- **One Aurora instance and "we have Multi-AZ."** A single-instance cluster doesn't automatically run readers in other AZs. Provision at least one reader for HA. The storage layer is multi-AZ but the compute isn't unless you say so.
- **Using the cluster endpoint for both reads and writes.** Cluster endpoint = writer. Use the reader endpoint for read traffic; otherwise readers sit idle and the writer takes all load.
- **Forgetting RDS Proxy in front of Aurora.** Same connection-storm problem as RDS — Lambda fleets and Fargate scale-out exhaust the connection pool quickly without it.
- **Aurora Global Database treated as synchronous DR.** Replication is async — RPO is whatever the cross-Region lag is. Plan for measurable data loss on Region failure unless you're using the managed planned failover.
- **Not using Blue/Green Deployments for major upgrades.** Manual blue/green via clones is more error-prone than the managed feature.
- **Cloning the wrong thing.** Clones share storage initially but diverge as you write — a long-lived "dev clone" of a hot prod cluster ends up costing as much as the source.
- **Forgetting that some engine versions / extensions lag vanilla Postgres / MySQL.** Verify the extension and version availability before committing.

## Pairs well with

- [RDS](rds.md) — the simpler choice when Aurora's features aren't needed.
- [Aurora Serverless](aurora-serverless.md) — for spiky or low-utilization workloads.
- **RDS Proxy** — connection pooling.
- **AWS DMS** — migrate from on-prem MySQL / Postgres or between engines.
- **AWS Backup** — vault-locked, cross-Region backup retention.
- **Performance Insights, Database Activity Streams** — observability and audit.

## Pairs well with these repo pages

- [RDS](rds.md), [Aurora Serverless](aurora-serverless.md), [DynamoDB](dynamodb.md).
- `docs/02-patterns/multi-region-active-passive.md` (forthcoming) — Aurora Global Database is the canonical AWS example.

## Further reading

- [Amazon Aurora documentation](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/).
- [Aurora storage and reliability](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.Overview.StorageReliability.html).
- [Aurora I/O-Optimized vs Standard](https://aws.amazon.com/blogs/database/introducing-amazon-aurora-i-o-optimized-and-amazon-rds-optimized-reads/).
- [Aurora Global Database](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database.html).
- ["Amazon Aurora: Design Considerations for High Throughput Cloud-Native Relational Databases"](https://www.amazon.science/publications/amazon-aurora-design-considerations-for-high-throughput-cloud-native-relational-databases) — the original SIGMOD paper.
