# RDS (Relational Database Service)

> **One-line summary.** Managed relational databases. Pick an engine (PostgreSQL, MySQL, MariaDB, Oracle, SQL Server, Db2); AWS runs the EC2, EBS, OS, engine binary, patching, and backups.

## TL;DR

- The right default for "I need a relational database on AWS and the workload fits one box." Six engines supported.
- **Multi-AZ deployment is table stakes for production** — synchronous standby in another AZ; automatic failover in 30–120 seconds. The newer **Multi-AZ DB cluster** topology (one writer + two readable standbys) cuts failover to ~35 seconds and adds a read-only endpoint.
- For workloads that outgrow a single writer, look at **Aurora** (see [`aurora.md`](aurora.md)) — usually a better long-term home than RDS for high-availability MySQL / PostgreSQL.
- Snapshots and PITR are managed for you; **AWS Backup** for cross-account / cross-Region vault-locked retention.
- Big cost levers: right-sizing, Reserved Instances, **gp3 over gp2/io1**, and **Multi-AZ DB cluster vs single-standby** depending on whether you can use the read replicas.

## When to use it

- "Give me a Postgres / MySQL / SQL Server / Oracle / Db2 / MariaDB without managing the OS."
- Workloads with steady, predictable load that fits a single writer.
- Apps that need a specific engine version, parameter, or extension that RDS supports but Aurora doesn't.
- Workloads that already use the engine on-prem and want a lift-and-shift target.

## When NOT to use it

- High read scale needs — use **Aurora** (15 readers, lower replica lag) or Aurora Global.
- Sub-second failover — Aurora is faster.
- Sub-30-second failover *with* RDS — use **Multi-AZ DB cluster** (gets you to ~35 s) instead of the classic Multi-AZ.
- Workloads that don't actually need SQL — DynamoDB, ElastiCache, or OpenSearch may be cheaper and scale further.

## Key concepts

**DB instance** — the EC2 + EBS managed by RDS. Instance classes are EC2-shaped (`db.m6i.large`, `db.r7g.xlarge`, `db.m8g.4xlarge`). **Graviton (`g` suffix) is ~20% cheaper for the same performance**; use it unless the engine doesn't support ARM.

**Engines and licensing:**

- **PostgreSQL** — fully open source, full extension support (with version-specific allow-list), the most popular new-RDS-instance choice.
- **MySQL** — community MySQL.
- **MariaDB** — community MariaDB.
- **Oracle** — BYOL or license-included. Oracle on RDS has feature limitations vs on-prem Oracle.
- **SQL Server** — license-included (Web / Standard / Enterprise) or BYOL with rules.
- **Db2** — IBM Db2, license-included or BYOL.

**Multi-AZ topologies (two distinct options):**

- **Multi-AZ (single-standby)** — one writer + one synchronous standby in another AZ. Standby is *not* readable. Automatic failover in 30–120 s. The classic default.
- **Multi-AZ DB cluster** (PostgreSQL and MySQL only) — one writer + **two readable** standbys, semi-synchronous replication. Failover in ~35 s. Standbys serve read traffic via a cluster reader endpoint. Roughly 2× the cost of single-standby but you gain read scale.

**Storage** — uses EBS under the hood. Volume types:

- **`gp3`** — the right default. Cheaper *and* faster than `gp2`; supports independently provisioned IOPS / throughput.
- **`io1` / `io2`** — provisioned IOPS for very high-throughput workloads.
- Storage auto-scaling grows the volume up to a configured ceiling.

**Read replicas** — async-replicated read-only copies. Up to 15 (engine-dependent). Useful for read scale, reporting, blue/green migrations. Cross-Region read replicas exist; can be promoted to standalone primaries.

**Snapshots & backups** — automated daily snapshot during the backup window plus continuous transaction logs to support **point-in-time recovery (PITR)** within the retention window (max 35 days). Snapshots can be copied across Regions / accounts.

**Backups via AWS Backup** — recommended for longer retention, vault locking, and air-gapped storage. See [`backup.md`](../storage/backup.md).

**Performance Insights** — built-in DB load analyzer. Shows top queries / wait events without your DBA having to install pgbadger / awr.

**Blue/Green Deployments** — RDS-managed dual environments for zero-downtime version upgrades, schema changes, and parameter changes. Cut over in seconds.

**Proxy** — **RDS Proxy** pools connections in front of RDS / Aurora. Use it for serverless callers (Lambda, ECS Fargate scale-out) so the DB doesn't drown in connection setup.

## Pricing model

- **Instance** — per second on-demand, with Reserved Instance discounts (1- or 3-year, ~30–60% off). Multi-AZ doubles the instance cost (you pay for the standby).
- **Multi-AZ DB cluster** — three instances (writer + 2 standbys) priced per instance.
- **Storage** — per GB-month, type-dependent. Provisioned IOPS billed per IOPS-month.
- **Backups** — free up to 100% of provisioned storage; beyond that, charged per GB-month.
- **PITR / extended retention** — included up to 35 days; longer retention via AWS Backup.
- **Data transfer** — same AWS rules (cross-AZ for Multi-AZ replication is free; cross-AZ to clients is billed; cross-Region replicas pay transfer).

## Quotas & limits

- **DB instances per Region** — 40 default (raisable).
- **Max storage per instance** — 64 TiB on most engines (engine-specific).
- **Read replicas** — 15 (most engines).
- **Connections** — engine and instance-class dependent (small instances have surprisingly low connection ceilings; RDS Proxy is the answer).
- **Backup retention** — 0–35 days for PITR; longer via AWS Backup or manual snapshots.

## Common pitfalls

- **Single-AZ in production.** A whole AZ failure or RDS host failure takes the database down with no failover. Always Multi-AZ.
- **Single-standby Multi-AZ when you'd benefit from readable standbys.** Multi-AZ DB cluster gives you read scale and faster failover; the cost premium is often worth it.
- **`gp2` for new workloads.** `gp3` is cheaper and faster.
- **No RDS Proxy from serverless clients.** Lambda scale-out events open thousands of connections; the DB pool ceiling becomes the bottleneck instead of CPU. Proxy fixes this.
- **Using AWS Console for parameter group changes.** Forces a reboot to apply for many params. Use Blue/Green Deployments for low-risk upgrades and big config changes.
- **Skipping minor version auto-upgrade.** Skipping patches accumulates risk and forces big-bang upgrades when you finally do it. Auto-apply minor versions in a maintenance window; pin majors.
- **Backups retention "managed" by manual snapshots.** Manual snapshots persist forever (and bill forever) unless you actively delete them. Use AWS Backup with a lifecycle policy.
- **Cross-Region read replica as your only DR.** Async replication = data loss on Region failure proportional to replica lag. For tight RPO, use Aurora Global or app-level dual-writes.
- **Single-engine sprawl across many small instances.** Consolidating onto fewer larger instances (or onto Aurora) often saves 30%+ in licensing and instance overhead.

## Pairs well with

- [Aurora](aurora.md) — when you need higher HA, more read scale, or Serverless.
- **RDS Proxy** — connection pooling.
- **AWS Backup** — managed cross-account / cross-Region backups with vault lock.
- **Secrets Manager** — DB credentials with automatic rotation.
- **Performance Insights + CloudWatch** — observability.
- **Database Migration Service (DMS)** — to / from / between engines.

## Pairs well with these repo pages

- [Aurora](aurora.md), [Aurora Serverless](aurora-serverless.md) — the AWS-native engines.
- [DynamoDB](dynamodb.md) — for workloads that don't actually need SQL.
- [Backup](../storage/backup.md) — for retention beyond 35 days.

## Further reading

- [Amazon RDS documentation](https://docs.aws.amazon.com/rds/).
- [Multi-AZ DB cluster deployments](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/multi-az-db-clusters-concepts.html).
- [RDS Blue/Green Deployments](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/blue-green-deployments.html).
- [RDS Proxy](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy.html).
- [RDS Performance Insights](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PerfInsights.html).
