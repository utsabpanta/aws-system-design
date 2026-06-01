# MemoryDB

> **One-line summary.** Redis- and Valkey-compatible in-memory database with **multi-AZ durability** — sub-millisecond reads, single-digit-ms writes, and *no risk of data loss on AZ failure*.

## TL;DR

- Think of it as "ElastiCache, but the data is durable." Multi-AZ transaction log replicates writes to a quorum before ack.
- Same Redis / Valkey API as ElastiCache; your client code doesn't change.
- Right when you want Redis as the **system of record**, not just a cache — feature flag stores, leaderboards that must survive failure, real-time scoring, low-latency session stores where eventual loss is unacceptable.
- More expensive than ElastiCache per GB (you're paying for the durability tier). Use ElastiCache for caches, MemoryDB for in-memory primaries.
- Like ElastiCache, Valkey is the cost-and-feature default in 2026.

## When to use it

- Feature flag / config stores where data loss isn't acceptable.
- Real-time leaderboards, scoring systems, geofencing where Redis data structures are the right model and the data is the source of truth.
- Low-latency session stores for apps where re-authenticating users on AZ failure is unacceptable.
- Microservices needing a fast shared state store with stronger durability than a cache.
- Workloads that are *currently* on Redis-as-system-of-record (often a pattern from on-prem) where you don't want to refactor onto DynamoDB.

## When NOT to use it

- Pure caching workloads — ElastiCache (Valkey/Redis OSS/Memcached) is much cheaper and sufficient.
- Relational / SQL workloads — RDS, Aurora.
- Document workloads at scale — DynamoDB.
- Workloads needing > a few hundred GB of in-memory state economically — disk-based stores are usually cheaper at that scale.

## Key concepts

**Cluster.** Up to 500 shards, each with a primary and up to 5 read replicas. Multi-AZ deployment spreads replicas across AZs.

**Engine.** **MemoryDB for Valkey** (recommended) or **MemoryDB for Redis OSS** (legacy). Both speak the Redis API.

**Durability model.** Writes are committed to a **multi-AZ transaction log** before the client receives an ack. A failover loses only in-flight transactions that hadn't been acked yet — not committed data. Compare to ElastiCache's async replication (where unreplicated writes can be lost on failover).

**Read consistency.** Primaries are linearizable; reads from replicas are eventually consistent (sub-second lag).

**Snapshots.** Daily snapshots to S3; PITR not available in the same way as DynamoDB but snapshots provide a recovery point.

**Auth.** **IAM authentication** (preferred), or AUTH token. TLS in transit required for IAM auth.

**Networking.** VPC-bound, same model as ElastiCache.

**Indexes / search.** MemoryDB supports Redis vector search and indexing extensions; useful for low-latency vector retrieval (small datasets) without standing up a separate vector DB.

## Pricing model

- **Per node-hour** by class (`db.r7g.xlarge`, `db.m8g.4xlarge`, etc.). Reserved Nodes discount available.
- **Write storage (multi-AZ transaction log)** — per GB-month of *unique* writes. This is the meaningful add over ElastiCache.
- **Snapshots** — included up to 100% of cluster memory; beyond that, per GB-month.
- **Data transfer** — same AWS rules.

MemoryDB is typically several times more expensive per GB than ElastiCache for the same memory footprint. The trade is durability: the value is in the writes you don't lose.

## Quotas & limits

- **Shards per cluster** — up to 500.
- **Replicas per shard** — up to 5.
- **Cluster nodes total** — up to 500.
- **Node memory** — up to 700+ GB per node on the largest classes.
- **Snapshot retention** — up to 35 days for automated; manual snapshots persist until deleted.
- **Connections per node** — high; use client connection pooling.

## Common pitfalls

- **Using MemoryDB as a cache.** It's expensive for that — ElastiCache is dramatically cheaper for cache workloads and sufficient for cache semantics.
- **Misreading the durability model.** Committed writes survive AZ failure; *in-flight* writes (not yet acked) don't. Design with the same idempotency disciplines you'd use against any distributed write store.
- **Single-shard cluster forever.** Single-shard clusters can't horizontal-scale writes. Plan shard count up front based on the write workload; resharding is supported but disruptive.
- **No client pool.** Connection storms can overwhelm a primary. Use a pooling client.
- **Snapshots as DR.** Snapshots are point-in-time; recovery loses everything between snapshots. For tight RPO, replicate or pair MemoryDB with a durable source (event log in Kinesis / Kafka).
- **Cross-Region.** MemoryDB cross-Region replication is limited — for true multi-Region, design at the app level or pair with a multi-Region durable system.
- **Treating it as Postgres.** It's still a key-value store at heart. Schema, query, and ops practices come from the Redis world, not SQL.

## Pairs well with

- [ElastiCache](elasticache.md) — for cache workloads where MemoryDB would be overkill.
- **Secrets Manager** — IAM auth tokens.
- **AWS Backup** — managed snapshot retention.
- **CloudWatch** — `EngineCPUUtilization`, `BytesUsedForMemory`, `Evictions`, replication-lag metrics.

## Pairs well with these repo pages

- [ElastiCache](elasticache.md) — sibling service with different durability profile.
- [DynamoDB](dynamodb.md) — the other "low-latency, durable" AWS database choice; different access model.

## Further reading

- [Amazon MemoryDB documentation](https://docs.aws.amazon.com/memorydb/).
- [MemoryDB for Valkey](https://aws.amazon.com/memorydb/valkey/).
- [MemoryDB durability and replication](https://docs.aws.amazon.com/memorydb/latest/devguide/durability.html).
- [Choosing between MemoryDB and ElastiCache](https://aws.amazon.com/blogs/database/measuring-database-performance-of-amazon-memorydb-for-redis/).
- [MemoryDB vector search](https://docs.aws.amazon.com/memorydb/latest/devguide/vector-search.html).
