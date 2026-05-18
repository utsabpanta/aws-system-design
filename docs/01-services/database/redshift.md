# Redshift

> **One-line summary.** AWS's columnar petabyte-scale data warehouse. Postgres-compatible SQL surface; massively parallel execution under the hood.

## TL;DR
- The right answer for "I have tens of TB to PB of structured data and I need fast SQL analytics over it." Not a transactional database.
- Two compute models: **Provisioned clusters** (`ra3` instances with managed storage, separating compute from storage) and **Redshift Serverless** (capacity in **RPUs**, scales automatically, no node management).
- **Spectrum** queries data sitting in S3 (Parquet, ORC, Iceberg, S3 Tables) without loading it — pay per TB scanned. **Zero-ETL** integrations pull data continuously from RDS, Aurora, DynamoDB, and SaaS sources without you running ETL jobs.
- **AQUA, RA3 managed storage, materialized views with auto-refresh, and result caching** are the load-bearing features that distinguish modern Redshift from the cluster-shaped warehouse it used to be.
- The most common mistake: treating Redshift as a transactional DB. It's not — small updates and deletes are slow; design for batch ingest + analytical query.

## When to use it
- Data warehouse for BI tools (QuickSight, Tableau, Looker, Power BI).
- Ad-hoc analytical SQL over many terabytes of historical data.
- ETL output / curated marts for analytics.
- Joining warehoused data with data lake (via Spectrum) and operational stores (via Zero-ETL).
- Workloads where Postgres SQL semantics (CTEs, window functions, stored procedures) matter to the analyst team.

## When NOT to use it
- Transactional OLTP — RDS / Aurora / DynamoDB.
- Low-latency point lookups — too much overhead per query; warm a cache or use OpenSearch / DynamoDB instead.
- Workloads where you'd rather pay per query and never run a cluster — **Athena over S3** with Parquet/Iceberg is much cheaper for occasional analytical queries.
- Streaming ingest at sub-second latency to a queryable layer — Kinesis + Firehose + S3 / OpenSearch fits better, with Redshift downstream.

## Key concepts

**Provisioned cluster.** Nodes (RA3 family — `ra3.xlplus`, `ra3.4xlarge`, `ra3.16xlarge`) with **Redshift Managed Storage (RMS)** — storage is decoupled from compute and tiered between SSD and S3 automatically. Scale compute independently of storage.

**Redshift Serverless.** No nodes. Capacity in **Redshift Processing Units (RPUs)** — set a base and max, auto-scales. Pay per RPU-second when queries run. Right for variable or unpredictable workloads.

**Distribution and sort keys.**
- **Distribution style** — `AUTO`, `KEY`, `EVEN`, `ALL`. `KEY` colocates rows sharing a distribution-key value on the same node (good for joins on that key). `ALL` replicates a small dimension table to every node (good for star joins).
- **Sort key** — physical ordering of rows on disk. Compound sort keys serve range scans; **interleaved** sort keys are mostly legacy.
- **AUTO** for both is the right default in 2026 — Redshift's auto-table-design improvements catch most cases.

**Workload management (WLM).** Auto WLM dynamically assigns memory and concurrency to query queues. Manual WLM exists for cases where you need explicit guarantees.

**Materialized views.** Precompute joins and aggregates; **auto-refresh** keeps them up to date. Massive performance lever for repeated analytical queries.

**Result caching.** Identical queries on unchanged data return from cache in milliseconds.

**AQUA (Advanced Query Accelerator).** Hardware-accelerated query layer for `LIKE`, `SIMILAR TO`, and aggregations in scan-heavy queries. Enabled by default on supported `ra3` instances.

**Spectrum.** Query S3 directly without loading. External tables map to S3 paths or Glue Catalog tables. Supports Parquet, ORC, JSON, Avro, **Apache Iceberg**, and **S3 Tables** (the managed Iceberg variant — see [`storage/s3.md`](../storage/s3.md)).

**Zero-ETL.** Continuous, managed pipelines from operational stores into Redshift — currently RDS MySQL, Aurora MySQL, Aurora PostgreSQL, DynamoDB, and several SaaS sources (Salesforce, SAP, ServiceNow, Zendesk, etc.). No ETL job to write or operate.

**Data sharing.** Read-only sharing of tables across clusters and accounts without copying. Producer cluster owns the data; consumer cluster reads it.

**Backup.** Continuous incremental backups to S3; cluster snapshots cross-Region copy. AWS Backup integration.

**Concurrency Scaling.** Auto-add transient clusters to absorb concurrent-query spikes. Cost-effective for bursty BI workloads — included free up to one hour per day per main cluster.

## Pricing model

- **Provisioned `ra3` nodes** — per node-hour, with Reserved Instance discounts.
- **Redshift Managed Storage** — per GB-month, decoupled from compute.
- **Redshift Serverless** — per RPU-second when queries are running. No charge when idle.
- **Spectrum** — per TB scanned, similar to Athena.
- **Concurrency Scaling** — first hour per day per cluster is free, then per-second.
- **Data transfer** — same AWS rules.
- **Data sharing** — free; consumer doesn't pay for storage of shared data.

The cost lever for serverless vs provisioned: **bursty / unpredictable workloads** favor Serverless; **steady, high-utilization workloads** favor provisioned with RIs.

## Quotas & limits

- **Cluster nodes**: provisioned cluster sizes range from 2 to 128 `ra3` nodes (engine-dependent).
- **Tables per cluster**: high (10,000+).
- **Concurrent queries**: bounded by WLM configuration; Concurrency Scaling absorbs overflow.
- **Spectrum scan**: subject to Athena-style per-Region scan rate quotas.
- **Result-set size**: high but constrained by client/driver buffers — use UNLOAD to S3 for very large extracts.

## Common pitfalls

- **Treating Redshift as transactional.** Single-row updates / deletes are slow; vacuum & analyze are required maintenance. Design for batch ingest (COPY from S3) and analytical queries.
- **Provisioned cluster when serverless fits.** Variable / new workloads under uncertain load benefit from Serverless; you don't waste compute idle.
- **Cross-Region COPY from on-prem.** S3-based COPY is the fast path; sending row-by-row INSERTs over the wire is dramatically slower.
- **No materialized views.** Repeated heavy aggregations should be precomputed.
- **Distribution / sort key set wrong.** AUTO handles most cases now; for hot tables with known access patterns, explicit KEY distribution + compound sort key matters.
- **Spectrum without Parquet/Iceberg.** JSON / CSV at scale costs more (scans more bytes) and is slower. Convert to Parquet (Glue, AWS DMS, Lambda) before querying through Spectrum.
- **Not turning on Concurrency Scaling.** Bursty BI workloads queue without it; with it, the queue is invisible.
- **Stale stats.** ANALYZE keeps the planner accurate; auto-analyze covers most cases but big bulk loads should trigger an explicit ANALYZE.
- **Public-access cluster.** Production clusters live in private subnets, reached via VPC peering / endpoints / Direct Connect, not via public endpoint.

## Pairs well with
- **S3 + Glue Catalog + Iceberg / S3 Tables** — lake-first architecture, Redshift queries it via Spectrum.
- **DMS, Zero-ETL** — continuous ingest from operational stores.
- **QuickSight, Tableau, Looker, Power BI** — BI front-ends.
- **EventBridge + Lambda** — orchestrate batch loads on schedules / events.
- **AWS Backup** — vault-locked cross-Region retention.

## Pairs well with these repo pages
- [S3](../storage/s3.md) — the data lake underneath Spectrum.
- [DynamoDB](dynamodb.md) — Zero-ETL source.
- [Aurora](aurora.md) / [RDS](rds.md) — Zero-ETL sources.
- `docs/04-reference-architectures/data-warehouse-redshift.md` (forthcoming).
- `docs/04-reference-architectures/data-lake-on-s3.md` (forthcoming).

## Further reading
- [Amazon Redshift documentation](https://docs.aws.amazon.com/redshift/).
- [Redshift Serverless](https://docs.aws.amazon.com/redshift/latest/mgmt/serverless-whatis.html).
- [Redshift Spectrum](https://docs.aws.amazon.com/redshift/latest/dg/c-using-spectrum.html).
- [Redshift Zero-ETL integrations](https://docs.aws.amazon.com/redshift/latest/mgmt/zero-etl-using.html).
- [Redshift best practices](https://docs.aws.amazon.com/redshift/latest/dg/best-practices.html).
