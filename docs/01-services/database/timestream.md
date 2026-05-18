# Timestream

> **One-line summary.** AWS's managed time-series databases. **Two distinct flavors** — and the situation has shifted significantly in 2025–2026.

## Status

> ⚠️ **Amazon Timestream for LiveAnalytics is closed to new customers as of June 20, 2025.** Existing customers can continue using it (and add new linked accounts under an existing payer); AWS continues security/availability investments but is no longer the recommended new-customer choice. AWS is steering new workloads to **Amazon Timestream for InfluxDB**, the primary AWS time-series offering going forward.

## TL;DR
- Two services share the "Timestream" name. **Timestream for InfluxDB** is the current go-to: managed InfluxDB (2.x and 3.x) with multi-AZ, snapshots, and Advanced Metrics. **Timestream for LiveAnalytics** is the AWS-built engine — still running for existing customers but closed to new ones.
- For new time-series workloads on AWS in 2026, pick **Timestream for InfluxDB**.
- For non-Timestream alternatives: **CloudWatch** (for AWS operational metrics), **MSK / Kinesis + S3 + Athena** (for high-volume telemetry feeding analytics), **Amazon Managed Service for Prometheus** (for Kubernetes / app metrics in PromQL).
- The migration target for existing LiveAnalytics workloads is InfluxDB (AWS is shipping migration tooling).

## When to use it (Timestream for InfluxDB)
- IoT sensor telemetry at scale.
- Application metrics, observability data pipelines.
- DevOps / SRE workloads built on InfluxDB tooling (Telegraf, Grafana, Flux / InfluxQL).
- Workloads where InfluxDB's time-series-specific features (downsampling, retention policies, continuous queries) match the access pattern.
- Real-time decisioning over high-frequency time-series streams.

## When NOT to use it
- AWS operational metrics — use **CloudWatch** (Logs / Metrics / Application Signals).
- Kubernetes / app metrics ecosystem — **Amazon Managed Service for Prometheus** is usually a more natural fit.
- Tabular analytical workloads — **Redshift**, **Athena**, or **S3 Tables** with Iceberg.
- Workloads where time-series is one access pattern among many — consider **DynamoDB** with time-bucketed keys or **Aurora PostgreSQL with TimescaleDB extension**.

## Key concepts

### Timestream for InfluxDB
**Managed InfluxDB** — AWS runs the InfluxDB engine, OS, patching, backups. You get the InfluxDB API (line protocol, Flux, InfluxQL — and SQL on InfluxDB 3).

**Versions:**
- **InfluxDB 2.x** — original supported version; Flux query language and the v2 storage model.
- **InfluxDB 3 Core and Enterprise** — added late 2025. Columnar Apache Arrow / Parquet storage under the hood, SQL queries (in addition to Flux), much better high-cardinality and large-aggregation performance. **The recommended version for new workloads.**

**Deployment**: Single-AZ or Multi-AZ. Multi-AZ provides synchronous standby in another AZ with failover.

**Advanced Metrics** (added March 2026) — automatically publishes detailed operational metrics to CloudWatch for both Single-AZ and Multi-AZ instances.

**Backups.** Automated daily snapshots; restore creates a new instance.

**Networking.** VPC-bound; reach via VPC endpoint.

**Integrations.** Telegraf for ingest, Grafana / Chronograf for visualization, the full InfluxData ecosystem.

### Timestream for LiveAnalytics (existing customers only)
The AWS-built time-series engine. Two-tier storage: **memory store** (recent data, fast point queries) and **magnetic store** (older data, optimized for aggregation queries). Schemaless time-series with strong-typed columns; SQL-like query language.

Still supported; not the recommended new-customer choice as of 2026.

## Pricing model

### Timestream for InfluxDB
- **Instance** — per hour by class.
- **Storage** — per GB-month.
- **Backup storage** — per GB-month.
- **Data transfer** — same AWS rules.

### Timestream for LiveAnalytics (legacy / existing customers)
- **Ingestion** — per million write requests.
- **Storage (memory store, magnetic store, magnetic store reads, magnetic store writes)** — separate dimensions; tiering data old → magnetic is cheaper.
- **Queries** — per GB scanned.

## Quotas & limits

### Timestream for InfluxDB
- **Instance classes** — limited subset; check current docs.
- **Storage size** — multi-TB per instance, growing with newer instance options.
- **Concurrent connections** — instance-class dependent.
- **Backup retention** — up to 35 days for automated.

### Timestream for LiveAnalytics
- **Records per ingestion request**: 100.
- **Query result size**: 1 GB.
- **Active partitions, retention windows**: documented limits; very high for most workloads.

## Common pitfalls

- **Picking LiveAnalytics for new workloads.** It's closed to new customers and not the strategic AWS direction. Pick InfluxDB instead.
- **Treating any of this as a general-purpose database.** Time-series is a specific access pattern. Don't store dimensional / relational data here.
- **Single-AZ InfluxDB in production.** Multi-AZ is the right default for anything outside dev.
- **Underestimating cardinality.** High-cardinality tags (millions of distinct values) tank query performance and explode storage. InfluxDB 3 is much better than 2.x here, but design matters.
- **Skipping retention policies / downsampling.** Raw 1-second granularity for years is wasteful for most analyses. Downsample older data to coarser granularity.
- **Querying through the application synchronously for dashboards.** Use Grafana or a precomputed materialized view; don't hammer the time-series DB on every page render.
- **No migration plan for existing LiveAnalytics workloads.** While AWS continues to support LiveAnalytics, "still running" is not a strategy. Track AWS's migration tooling and plan a move.

## Pairs well with
- **Grafana** (Amazon Managed Grafana or self-hosted) — visualization.
- **Telegraf, OpenTelemetry collectors** — ingest from agents.
- **Kinesis Data Firehose** — high-volume ingestion buffer.
- **Lambda / EventBridge** — alarms triggered by query results.

## Pairs well with these repo pages
- [CloudWatch] (in [`observability/`](../observability/), forthcoming) — for AWS operational metrics, log aggregation.
- `docs/04-reference-architectures/iot-ingestion.md` (forthcoming) — IoT telemetry pipelines.
- `docs/04-reference-architectures/log-aggregation.md` (forthcoming).

## Further reading
- [Amazon Timestream documentation hub](https://docs.aws.amazon.com/timestream/).
- [Timestream for InfluxDB](https://docs.aws.amazon.com/timestream/latest/developerguide/timestream-for-influxdb.html).
- [Timestream for LiveAnalytics availability change](https://docs.aws.amazon.com/timestream/latest/developerguide/AmazonTimestreamForLiveAnalytics-availability-change.html).
- [InfluxDB 3 on AWS announcement](https://aws.amazon.com/blogs/database/amazon-timestream-for-influxdb-expanding-managed-open-source-time-series-databases-for-data-driven-insights-and-real-time-decision-making/).
