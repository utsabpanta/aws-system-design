# Performance Efficiency

> **One-line summary.** Use compute, storage, network, and data resources efficiently — and keep using them efficiently as demand and technology change.

## TL;DR

- Measure first. The slow part is almost never the part you'd guess. Profile before optimizing.
- Pick the right primitive for the workload (compute family, storage class, database engine). The wrong primitive can't be tuned around.
- Caching and CDNs are the highest-leverage performance tools in the AWS toolkit — they offload work entirely rather than make it faster.
- Asynchronous beats synchronous for user-perceived performance whenever the work can be deferred. Acknowledge fast, do the slow thing in the background.
- Performance is not a one-time achievement. Demand changes, AWS ships new instance families, your data grows — re-evaluate quarterly.

## What the pillar is about

Performance Efficiency is the pillar that asks "are you getting the most out of what you're paying for?" It covers selection (right instance, right service, right database), review (re-evaluating as AWS evolves), monitoring (where time and dollars actually go), and trade-offs between performance and cost / consistency / complexity.

It overlaps heavily with [Cost Optimization](cost-optimization.md) — usually "more efficient" means "cheaper too." Where they diverge: a performance-tuned workload might use a more expensive resource (Graviton vs. x86, NVMe vs. EBS) because the per-unit cost is lower even though the unit price is higher.

## AWS's five design principles

1. **Democratize advanced technologies.** Use managed services to consume capabilities (ML inference, geospatial search, vector DB) without operating them. Don't run your own Elasticsearch cluster to support a single feature.
2. **Go global in minutes.** Multi-Region deployment is a CloudFront distribution and a Route 53 record, not a six-month project. Use it.
3. **Use serverless architectures.** Capacity matches load by definition; no overprovisioning, no idle.
4. **Experiment more often.** Cheap to spin up a new instance type, a new storage class, a new database engine — measure on real traffic instead of debating in a meeting.
5. **Consider mechanical sympathy.** Match the workload to the resource. CPU-bound goes on compute-optimized; memory-bound goes on memory-optimized; tail-latency-sensitive goes on Graviton with `taskset`/CPU pinning.

## Key practices

### Compute selection

- **Instance families.** General purpose (M), Compute (C), Memory (R/X), Storage (I/D), GPU (P/G). Match the family to the bottleneck.
- **Graviton (ARM) first** for most stateless workloads. ~20% better price/performance than x86 with no real downside other than the rebuild step.
- **Right-sizing.** Use Compute Optimizer recommendations rather than guessing. The default "we picked m5.xlarge because that's what we've always used" is the most common source of over-provisioning.
- **Serverless when the load is bursty or unknown.** Lambda + Fargate handle 0-to-N scaling that EC2 can't without overprovisioning headroom.
- **Spot for fault-tolerant batch.** EMR, Glue, EKS data plane, ECS — Spot can be 60–90% cheaper than on-demand, with the trade-off of 2-minute reclaim notices.

### Storage selection

The right storage primitive saves an order of magnitude:

- **S3** — object store for anything from images to logs to data lake tables. Storage classes (Standard / Intelligent-Tiering / IA / Glacier) match access pattern to cost.
- **EBS** — block storage for EC2. `gp3` is the default; `io2 Block Express` for high-IOPS workloads (databases). Don't run databases on `gp2` — `gp3` is cheaper *and* faster.
- **EFS** — NFS file storage, multi-AZ, autoscaling. Right for shared filesystems; wrong as a database substitute.
- **FSx** — Windows file shares (FSx for Windows), high-performance Linux (Lustre), enterprise NAS (NetApp, OpenZFS).
- **Instance store** — local NVMe attached to specific EC2 families (i, d, im, is). Microsecond latency, ephemeral. Use for cache or scratch, never for durable data.

### Database selection

The biggest performance lever in most systems:

- **Relational, transactional, < a few TB.** RDS or Aurora (Aurora for higher availability and read scale).
- **Relational, OLAP, > TB.** Redshift, or Athena on S3 with Parquet.
- **Key-value, predictable access pattern, single-digit-ms.** DynamoDB.
- **Cache.** ElastiCache (Redis/Valkey) or MemoryDB (Redis with durability).
- **Time-series.** Timestream, or InfluxDB / Prometheus.
- **Graph.** Neptune.
- **Search.** OpenSearch.
- **Streaming.** Kinesis Data Streams or MSK (Kafka).

The mismatch is the killer: doing search in a SQL DB with `LIKE '%foo%'`, doing time-series in DynamoDB, doing analytics on the OLTP primary. Pick the right primitive.

### Network performance

- **CloudFront** for any user-facing content. Edge TLS termination + cache offload reduces both latency and origin load.
- **Global Accelerator** when you need the AWS backbone but not caching (anycast IPs, TCP/UDP, regional failover).
- **VPC Endpoints** for AWS services in private subnets — avoids NAT egress, lower latency, traffic stays on the AWS network.
- **Placement groups** (cluster, partition, spread) for EC2 workloads where instance-to-instance latency matters.
- **Enhanced Networking (SR-IOV) / Elastic Fabric Adapter** for HPC and tightly-coupled distributed workloads.

### Caching layers

The fastest request is the one you don't serve. Layered caches typical of any production system:

1. **Browser cache** (HTTP `Cache-Control`).
2. **CDN cache** (CloudFront).
3. **Application cache** (ElastiCache / MemoryDB / in-process).
4. **Database query cache** (ElastiCache as lookaside, Aurora cluster cache).
5. **OS page cache** (free, you usually don't need to tune it).

See [`docs/02-patterns/caching-strategies.md`](../02-patterns/caching-strategies.md) for cache patterns and invalidation strategies.

### Async, batch, prefetch

- **Async over sync.** A 200 ms HTTP request that enqueues to SQS and ACKs feels instant; the 30-second background job is invisible. Use SQS, Step Functions, EventBridge for fire-and-forget work.
- **Batch over per-item.** DynamoDB `BatchWriteItem`, S3 `ListObjectsV2` paginated, Kinesis `PutRecords`. Per-request overhead dominates per-item cost; batches amortize it.
- **Prefetch on read patterns.** If you'll need objects A, B, C in sequence, fetch them in parallel.

### Observability for performance

- **CloudWatch Metrics** for system-level (CPU, memory, queue depth, IOPS).
- **CloudWatch Logs Insights** for log-derived metrics (p99 of a custom log field).
- **X-Ray / OpenTelemetry** for distributed traces — where time actually goes across services.
- **CloudWatch Application Signals** for auto-instrumented USE/RED metrics without manual instrumentation work.

Performance work without a profile is guessing. Profile first.

## AWS services that support this pillar

- **Compute Optimizer, Trusted Advisor** — right-sizing recommendations.
- **Auto Scaling** — capacity matching demand.
- **CloudFront, Global Accelerator** — edge and routing performance.
- **ElastiCache, MemoryDB** — in-memory caching.
- **S3 Intelligent-Tiering** — automatic storage class transitions.
- **DynamoDB Adaptive Capacity, On-Demand** — handles uneven access patterns.
- **Aurora Auto Scaling read replicas** — read scaling for relational workloads.
- **EC2 Graviton (M7g, C7g, R7g, …)** — ARM-based price/performance.
- **Lambda, Fargate, App Runner** — serverless compute.
- **Kinesis, MSK, SQS, Step Functions** — asynchronous coupling.
- **CloudWatch, X-Ray, Application Signals** — measurement.

## Common anti-patterns

- **"It's slow, let's add a cache."** Without measurement, the cache will be put in the wrong place and the real bottleneck stays.
- **One database for everything.** OLTP + OLAP + search + queue in one Postgres → all four are mediocre.
- **Sync everything.** Calling a third-party API synchronously in a user-facing request path. One vendor's slow day becomes your slow day.
- **Default instance families forever.** AWS ships a new instance family every year that's faster and cheaper than the current default. Re-evaluate annually at least.
- **N+1 in any form.** N database queries per request, N S3 calls per request, N retry loops per request. Batch or join.
- **Premature optimization.** Most "performance" work doesn't move a customer-visible metric. Set the SLO first; only optimize what's missing it.
- **Ignoring the tail.** A median latency of 20 ms with a p99 of 5 seconds will feel broken under load even though "the average is fine."

## Pairs well with

- [Cost Optimization](cost-optimization.md) — same underlying tools, different lens.
- [Reliability](reliability.md) — performance regressions are reliability events when they breach SLOs.
- `docs/02-patterns/caching-strategies.md`, `read-replicas-vs-caching.md`, `data-partitioning-sharding.md`.

## Further reading

- AWS Well-Architected Framework — Performance Efficiency pillar whitepaper.
- *Systems Performance: Enterprise and the Cloud*, Brendan Gregg — definitive book on measuring and tuning system performance.
- *The Datacenter as a Computer*, Barroso, Hölzle, Ranganathan — Google's classic on warehouse-scale efficiency.
- AWS Compute Optimizer documentation.
- Amazon Builders' Library — "Tuning AWS Java SDK HTTP request settings", "Performance issues by AWS" essays.
