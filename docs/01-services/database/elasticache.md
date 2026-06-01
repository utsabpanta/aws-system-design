# ElastiCache

> **One-line summary.** Managed Redis OSS, Valkey, and Memcached clusters. The default in-memory cache layer on AWS.

## TL;DR

- Three engines: **Valkey** (open-source Redis fork, the new cost-and-feature default), **Redis OSS** (legacy), and **Memcached** (simpler, multi-threaded, no persistence or replication).
- **Valkey is the cost winner in 2026** — roughly **20% cheaper on node-based clusters and 33% cheaper on Serverless** than Redis OSS, with API compatibility and managed in-place upgrades. Real production migrations (Snap, Pinterest, MaiCoin) have shown 60%+ cost reductions.
- **ElastiCache Serverless** scales capacity per request without you picking node sizes — best for spiky / unpredictable workloads. Pay per ECPU and per GB-stored.
- Redis OSS 4 / 5 entered Extended Support pricing in February 2026 — an 80% premium that doubles to 160% by year 3 of Extended Support. If you're on those versions, the cost case for migrating to Valkey is now compelling.
- The biggest operational mistakes are using ElastiCache as a primary datastore (it's a cache), not setting eviction policy correctly, and ignoring memory-pressure metrics until the cluster OOMs.

## When to use it

- Application-level caching in front of databases (DynamoDB, RDS, Aurora, OpenSearch).
- Session storage for web apps.
- Rate limiting, leaderboards, counters, geo queries (Redis data structures).
- Pub/sub (Redis Streams or Pub/Sub) for fan-out within the AWS account.
- Anywhere "in-memory key-value with optional persistence" is the right shape.

## When NOT to use it

- Durable system-of-record storage — even with Redis AOF persistence, treat ElastiCache as a cache, not a primary database. For durable Redis, use **MemoryDB** (see [`memorydb.md`](memorydb.md)).
- Workloads needing sub-millisecond latency *and* durability — MemoryDB is the answer.
- Multi-cloud / portability requirements — Valkey is open-source-friendly, but if you need to run the same store on-prem too, factor that in.
- Search / analytics workloads — use OpenSearch or DynamoDB respectively.

## Key concepts

**Engines.**

- **Valkey** — open-source BSD-licensed Redis fork led by Linux Foundation (Linux, AWS, Google, Oracle, others). API-compatible with Redis 7.x; community now adds features faster than Redis OSS. AWS's recommended default for new caches in 2026.
- **Redis OSS** — Redis Labs' open-source distribution. AWS still supports it; Extended Support is paid for older versions.
- **Memcached** — multi-threaded, partitioned, no replication, no persistence. Right when you specifically want simple, sharded, in-memory cache with no replication overhead.

**Deployment models.**

- **Cluster mode disabled (CME-disabled)** — one shard, optional replicas. Up to 5 read replicas. Capped at one shard's memory.
- **Cluster mode enabled (CME)** — multiple shards (up to 500), each with optional replicas. Horizontal scale. Client must be cluster-aware.
- **Serverless** — opaque capacity; pay per ECPU (request) and per GB-stored. Auto-scales storage and throughput. No node sizing decisions.

**Multi-AZ.** Enable for production. Primary in one AZ, replicas in other AZs. Automatic failover.

**Persistence (Redis OSS / Valkey).** Optional. AOF (append-only file) replays writes on restart. Cheaper to design assuming the cache can be cold-started (warm-up logic in the app) than to lean on persistence.

**Cluster networking.** Lives in your VPC; clients reach it via VPC routing. No public endpoint.

**Auth.** **AUTH token** (Redis legacy), **IAM authentication** (newer, integrates with IAM roles), **encryption in transit (TLS)** required for IAM auth.

**Backups.** Snapshots to S3. Restore creates a new cluster.

**Migration from Redis OSS to Valkey** — managed in-place upgrade. Existing Redis OSS reserved nodes automatically apply to Valkey nodes in the same instance family and Region. Blue/green upgrade path is also supported.

**Eviction policies.** `noeviction` (errors on full memory), `allkeys-lru` (evict any LRU), `volatile-lru` (evict LRU among TTLed keys), and several others. **`noeviction` in a cache is almost always wrong** — it converts a cache miss into an app error. Pick an LRU policy unless you have a strong reason otherwise.

## Pricing model

- **Node-based** — per node-hour by class (`cache.t4g.medium`, `cache.r7g.xlarge`, etc.). RIs / Savings Plans discount apply.
- **Serverless** — per **ECPU** (ElastiCache Processing Unit) for requests and per **GB-hour** for stored data.
- **Backups** — included up to 100% of cluster memory; beyond that, per GB-month.
- **Data transfer** — same AWS rules; cross-AZ between replicas is free for replication, not for client traffic.
- **Extended Support (Redis OSS v4 / v5)** — 80% premium in years 1-2 of Extended Support; 160% in year 3. Strong financial motivator to upgrade or migrate to Valkey.

The big 2026 economic story: at small scale, **Valkey Serverless** is cheaper than Valkey nodes and dramatically cheaper than the same workload on Redis OSS nodes. At very large steady-state scale, Valkey provisioned with Reserved Capacity is the cost winner.

## Quotas & limits

- **Nodes per cluster** — engine and cluster-mode dependent.
- **Shards per cluster (CME)** — up to 500 (typical limits much lower; check current docs).
- **Node memory** — depends on instance class; up to 700+ GB on largest classes.
- **Serverless cluster max data size** — generous (multi-TB).
- **Connections per node** — high (10k+); right-sized node + connection pooling on the client side rarely makes this a limit.
- **Backup retention** — up to 35 days for automated; manual snapshots persist until deleted.

## Common pitfalls

- **Treating ElastiCache as durable storage.** Use **MemoryDB** if you need Redis API + durability. ElastiCache is a cache; design the app for cache-miss paths.
- **`noeviction` in production.** Memory fills → writes start failing. Pick `allkeys-lru` (cache) or `volatile-lru` + explicit TTLs (mixed).
- **No TTL on cached items.** Stale forever, eventually evicted at random. Set TTLs proportional to the data's freshness needs.
- **Hot key.** A single key everyone reads becomes a CPU bottleneck on its shard. Mitigations: replicate hot keys across multiple keys, use Redis Cluster slot pre-splitting, or move the hot computation to a downstream layer.
- **Cache stampede on cold start.** When the cache is empty, every request hits the DB. Mitigate with request coalescing, staggered TTLs (TTL + jitter), and warming during deploy.
- **Memcached for replicated workloads.** Memcached has no replication. AZ failure = lose that partition. Use Redis / Valkey for any workload that can't tolerate that.
- **Cross-VPC access.** ElastiCache clusters are VPC-bound — peering or Transit Gateway is required for cross-VPC access. Plan the topology upfront.
- **Ignoring Redis OSS Extended Support cost.** v4 and v5 are now 80–160% premium. Migrate to a current Redis OSS version or to Valkey.
- **Serverless for predictable steady-state load.** Node-based + RIs is cheaper above ~50% steady utilization.

## Pairs well with

- [DynamoDB](dynamodb.md) — cache layer in front of DynamoDB tables.
- [RDS](rds.md) / [Aurora](aurora.md) — read-through cache for read-heavy SQL workloads.
- **AWS Backup** — managed snapshots.
- **Secrets Manager** — auth tokens.
- **CloudWatch Metrics** — `DatabaseMemoryUsagePercentage`, `Evictions`, `CacheHitRate`.

## Pairs well with these repo pages

- [MemoryDB](memorydb.md) — for the same Redis API with multi-AZ durability.
- `docs/02-patterns/caching-strategies.md` (forthcoming) — how to design cache invalidation that doesn't lie.

## Further reading

- [Amazon ElastiCache documentation](https://docs.aws.amazon.com/elasticache/).
- [Valkey on ElastiCache](https://aws.amazon.com/elasticache/valkey/).
- [Migrating from Redis OSS to Valkey](https://aws.amazon.com/blogs/database/maicoin-case-study-blue-green-upgrade-from-amazon-elasticache-redis-to-valkey/).
- [ElastiCache Serverless](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/Whatis-Serverless.html).
- ["Caching challenges and strategies", Amazon Builders' Library](https://aws.amazon.com/builders-library/caching-challenges-and-strategies/).
