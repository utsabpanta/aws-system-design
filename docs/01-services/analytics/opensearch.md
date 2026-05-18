# OpenSearch Service

> **One-line summary.** Managed **OpenSearch** (the open-source Elasticsearch fork) for search, log analytics, and vector search. Two deployment models: **OpenSearch Service** (provisioned clusters) and **OpenSearch Serverless** (no nodes, capacity in OCUs).

## TL;DR
- Use it for **search** (full-text, fuzzy, faceted), **log analytics** (centralized log search), and increasingly for **vector similarity search** (k-NN / HNSW) powering RAG and recommendation.
- **OpenSearch Serverless** uses **OpenSearch Compute Units (OCUs)** — billed per OCU-hour for indexing and search. Minimum 2 OCUs (or 1 OCU dev/test); auto-scales. Three **collection types**: time-series, search, and vector.
- **Provisioned clusters** still the right choice for sustained-high-load search or specialized cluster configurations (custom plugins, specific Elasticsearch-compatibility versions).
- **UltraWarm + Cold storage** tier old log indices off hot nodes to S3-backed nodes — orders of magnitude cheaper for long retention.
- The biggest pitfall is **shard explosion** on log-style workloads — daily indices with too many shards each create cluster-wide stress.

## When to use it
- Application search (e.g., e-commerce site search).
- Log aggregation and search at scale (CloudWatch Logs → Firehose → OpenSearch).
- Observability dashboards (OpenSearch Dashboards, formerly Kibana).
- Vector search for RAG, semantic search, recommendation.
- Security analytics (SIEM-style use cases — though dedicated SIEMs may fit better).

## When NOT to use it
- OLTP / transactional workloads — relational / KV stores.
- Analytical SQL over big data lakes — **Athena** + S3.
- High-cardinality time-series at extreme scale — **Timestream for InfluxDB** or specialized TSDBs.
- Tiny workloads where running even a small cluster (or 2-OCU minimum Serverless) is overkill — sometimes pgvector or a managed Pinecone tier is enough.

## Key concepts

### Deployment models

**OpenSearch Service (provisioned).**
- Cluster with data nodes, optional dedicated master nodes, optional UltraWarm + Cold nodes.
- Multi-AZ deployment (3 AZs typical for production).
- Instance types `r6g.large.search`, etc. (Graviton broadly supported).
- Storage on EBS (`gp3` default) or instance store (`i3.search`).
- Auto-Tune for query / JVM tuning.
- **Multi-AZ with Standby** — synchronous replication to a standby in a separate AZ for higher availability.

**OpenSearch Serverless.**
- No nodes. Capacity in **OCUs** (OpenSearch Compute Units; ~1 vCPU + 6 GB RAM + 120 GB storage each; half-OCU minimum).
- **Three collection types** with different optimizations:
  - **Time-series** — log / metrics analytics with time-based indices.
  - **Search** — application search.
  - **Vector** — vector similarity (k-NN / HNSW).
- **Vector Acceleration OCUs** — GPU-accelerated OCUs for fast HNSW index construction at large vector datasets.
- Per-OCU-hour pricing. Minimum 2 OCUs (1 indexing + 1 search, with HA replicas); dev/test mode allows 1 OCU.
- Storage on S3 (billed per GB-month).

### Versions
- **OpenSearch** open-source releases (current 2.x family in 2026; 3.x preview).
- **Legacy Elasticsearch** 7.x cluster support continues for migration scenarios; new clusters use OpenSearch.

### Storage tiers (provisioned)
- **Hot** — full-feature, EBS / instance store.
- **UltraWarm** — S3-backed, cheaper, read-optimized; queryable with slightly higher latency. Right for old log indices.
- **Cold** — frozen on S3; "rehydrate" before querying. Cheapest tier.

### Snapshots
Automated snapshots to S3 every hour by default; manual snapshots to your S3 bucket.

### Networking & auth
- VPC-attached (recommended) or public endpoint (rarely the right choice).
- Fine-grained access control (FGAC) — user / role-based access including index-level / document-level / field-level.
- **IAM authentication** for AWS-native callers.
- Cognito integration for OpenSearch Dashboards user auth.

### Index lifecycle management (ISM)
Define lifecycle policies (rollover, shrink, force-merge, move to UltraWarm / Cold, delete). The right way to manage time-series log indices.

### Vector search
- **k-NN plugin** — exact and approximate (HNSW, IVF) nearest-neighbor search.
- **Hybrid search** — combine vector and lexical (BM25) scoring.
- Integrates with **Bedrock** / SageMaker for embedding generation pipelines.

### CloudWatch Logs streaming
Subscriptions stream log groups to OpenSearch via Firehose for centralized search.

## Pricing model

### Provisioned
- **Per instance-hour** by class. Reserved Instances available.
- **EBS storage** for hot tier (per GB-month + per provisioned IOPS).
- **UltraWarm / Cold** — per GB-month, much cheaper than hot.
- **Data transfer** — same AWS rules.
- **Multi-AZ with Standby** — third replica of the data nodes (a third "AZ slice").

### Serverless
- **Per OCU-hour** for indexing, search, and Vector Acceleration OCUs (where used).
- **Storage** — per GB-month on S3.
- **Minimum 2 OCUs per collection** (or 1 OCU in dev/test mode).

The economic argument: Serverless wins for spiky / unknown loads, where the always-on minimum doesn't matter much; Provisioned wins for sustained heavy workloads with Reserved Instances.

## Quotas & limits

- **Domains per account per Region (provisioned)**: 100 default.
- **Nodes per cluster**: high (200+); shard / partition limits dominate practical scale.
- **Shards per cluster**: 100,000+ but practical limit much lower (~1,000-10,000) for healthy clusters.
- **Collections per Region (Serverless)**: 50 default.
- **Vector dimensions per index**: up to 16,000.

## Common pitfalls

- **Shard explosion.** A cluster with hundreds of indices × tens of shards each = tens of thousands of shards = cluster instability. Plan shard count per index based on data size (target ~30-50 GB per shard).
- **Daily indices with default shard count.** Default 5 shards × 365 days = 1,825 shards/year for one log type. Use ISM rollover + appropriate sharding strategy.
- **Public-access cluster.** Risk surface. Use VPC + FGAC.
- **No snapshot strategy.** Automated snapshots are within the same Region; for DR, cross-Region snapshot copy.
- **Hot data only.** Old log indices on hot tier are 10-100× more expensive than UltraWarm equivalents.
- **Skipping FGAC.** All-or-nothing access. FGAC is the right default for multi-tenant clusters.
- **OpenSearch Dashboards (Kibana) as the only access UI.** Plan a programmatic-access story for ops automation.
- **Vector indexing on Provisioned without GPU acceleration.** Large vector datasets benefit from Vector Acceleration OCUs on Serverless.

## Pairs well with
- [Amazon Data Firehose](kinesis.md) — log delivery into OpenSearch.
- [CloudWatch Logs](../observability/) (forthcoming) — log subscription source.
- [Bedrock](../ml-ai/) (forthcoming) — embeddings for vector search; RAG pipelines.
- [Cognito](../security-identity/cognito.md) — auth for Dashboards.
- **Logstash / Fluent Bit / Fluentd** — log shippers.
- [Lambda](../compute/lambda.md) — query handlers, lifecycle automation.

## Pairs well with these repo pages
- [Kinesis](kinesis.md), [QuickSight](quicksight.md).
- `docs/04-reference-architectures/log-aggregation.md` (forthcoming).

## Further reading
- [Amazon OpenSearch Service documentation](https://docs.aws.amazon.com/opensearch-service/).
- [OpenSearch Serverless overview](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless.html).
- [k-NN / vector search](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/knn.html).
- [Index State Management (ISM)](https://opensearch.org/docs/latest/im-plugin/ism/index/).
- [UltraWarm storage](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/ultrawarm.html).
