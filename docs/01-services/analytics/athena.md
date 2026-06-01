# Athena

> **One-line summary.** Serverless SQL on top of data in S3 (and other federated sources). Pay per TB scanned; no cluster to manage.

## TL;DR

- The right answer for ad-hoc / on-demand analytical SQL over data lakes — especially Parquet / ORC / Iceberg files in S3.
- **Two engines:** **Athena SQL** (Trino-based; the default, query data with standard SQL) and **Athena for Spark** (managed Spark notebooks for code-first analytics).
- Pricing is **per TB scanned** by default — making columnar formats (Parquet) and **partitioning** the load-bearing optimizations. A query against partitioned Parquet costs orders of magnitude less than the same query against unpartitioned JSON.
- **Federated queries** let one SQL query span S3, RDS, Aurora, DynamoDB, Redshift, OpenSearch, MSK, and dozens of partner data sources via connectors.
- **Apache Iceberg** and **S3 Tables** are first-class — Athena reads (and writes) them natively.

## When to use it

- Ad-hoc analytical queries over data lake / S3 (logs, exports, raw data).
- BI tools (QuickSight, Tableau, Looker) querying S3 without a warehouse.
- One-off investigations / forensics over CloudTrail, VPC Flow Logs, ELB logs.
- Spark notebooks for code-driven analytics (Athena for Spark).
- Federated SQL across multiple data sources without ETL.

## When NOT to use it

- High-throughput, low-latency point lookups — that's a key-value store.
- Sustained heavy BI dashboards with consistent traffic — **Redshift** or **Athena Provisioned Capacity** is cheaper at steady state.
- Transactional workloads — Athena is read-mostly analytics; it can write to Iceberg / S3 Tables but isn't an OLTP engine.
- Tiny datasets where the per-query overhead dominates — sometimes a local DuckDB / SQLite is simpler.

## Key concepts

**Workgroup.** A way to isolate query history, results location, cost controls, and engine choice per team or use case.

**Data catalog.** Athena uses **AWS Glue Data Catalog** by default (formerly its own catalog). Tables defined in Glue are queryable by Athena, EMR, Redshift Spectrum, and Lake Formation alike.

**Query result location.** All Athena query results land in an S3 bucket you configure. Plan its lifecycle policy or it accumulates forever.

**Athena SQL engine versions.** Trino-based. AWS publishes engine versions; opt in to new versions per workgroup.

**Athena for Spark.** Serverless Spark notebooks; pay per DPU-hour. PySpark / Scala notebooks against the same Glue Data Catalog tables.

**Capacity modes:**

- **On-demand** (default) — per-TB-scanned pricing.
- **Provisioned Capacity** (Athena Capacity Reservations) — reserve DPUs by the hour for predictable workloads; pay flat hourly even with idle capacity. Cheaper at sustained heavy use.

**Partitioning.** Subdirectory-based partition keys (`/year=2026/month=05/day=18/`) let Athena prune to just the relevant directories. **Partition projection** removes the need to register partitions in Glue at all — Athena computes them from a template.

**File formats.**

- **Parquet / ORC** — columnar; column pruning + compression. The right default for analytics.
- **Apache Iceberg** / **S3 Tables** — table format on top of Parquet with ACID transactions, schema evolution, time travel.
- **JSON / CSV** — row-oriented, no column pruning. Convert to Parquet for production.

**Federated queries.** Run a single SQL query that joins S3, RDS, Aurora, DynamoDB, Redshift, OpenSearch, MSK / Kafka, and 30+ partner sources via Lambda-backed connectors. The connector framework also lets you build your own.

**CTAS (Create Table As Select).** Materialize a query result into a new table (Parquet by default). The cheap way to convert ad-hoc query results into reusable assets.

**Apache Iceberg writes.** Athena can write to Iceberg tables — `INSERT`, `UPDATE`, `DELETE`, `MERGE`, time-travel queries.

**Encryption.** S3-level + result-level KMS encryption.

## Pricing model

- **On-demand** — $5 per TB scanned (after compression). Result data not double-charged.
- **Provisioned Capacity** — per DPU-hour reservation, regardless of usage.
- **Federated queries** — Lambda invocations for the connector + S3 scan + standard Athena per-TB.
- **Athena for Spark** — per DPU-hour for notebooks.
- **Storage** — standard S3 rates for source data and query results.

The optimization most teams skip until the bill arrives: **switch from JSON to Parquet** (often 10× cheaper queries because of compression + column pruning), then **partition** (another 10–100× depending on query shape).

## Quotas & limits

- **Concurrent DML queries**: workgroup-dependent, defaults around 20-25 (raisable).
- **Query timeout**: 30 minutes default.
- **Max query results size**: 10 MB streamed inline; larger via S3 result file.
- **Federated connector concurrency**: bounded by Lambda concurrency.
- **Workgroups per account per Region**: 1,000.

## Common pitfalls

- **`SELECT * FROM huge_json_table`** with no `WHERE` against partition columns — full-scan, terabytes, hundreds of dollars per query.
- **No partitioning.** Even simple time-based partitioning cuts scans dramatically.
- **JSON / CSV in production data lakes.** Convert to Parquet via Glue / Firehose / Spark.
- **Forgotten query result bucket.** Accumulates forever without a lifecycle policy.
- **One workgroup for everyone.** No cost attribution, no query-quota isolation. Per-team workgroups + cost controls.
- **Federated query against a primary DB.** The connector hits the live database; high-volume joins can take it down. Use a replica or extracted table.
- **`SELECT *` when you only need three columns.** Parquet's columnar power is wasted; pay for all columns. Project explicitly.
- **No Iceberg / S3 Tables for high-churn data lakes.** Mutable data on plain Parquet means rewriting partitions on every update; Iceberg's ACID makes this manageable.

## Pairs well with

- [S3](../storage/s3.md), **S3 Tables** — primary data location.
- [Glue](glue.md) — catalog + ETL to convert formats.
- [Lake Formation](lake-formation.md) — fine-grained permissions.
- **QuickSight, Tableau, Looker** — BI front-ends.
- [Lambda](../compute/lambda.md) — federated query connectors.
- [Redshift](../database/redshift.md) — for the "queries that justify a warehouse" half of workloads.

## Pairs well with these repo pages

- [Glue](glue.md), [Lake Formation](lake-formation.md), [Redshift](../database/redshift.md), [S3](../storage/s3.md).
- `docs/04-reference-architectures/data-lake-on-s3.md` (forthcoming).

## Further reading

- [Amazon Athena documentation](https://docs.aws.amazon.com/athena/).
- [Athena for Spark](https://docs.aws.amazon.com/athena/latest/ug/notebooks-spark.html).
- [Athena federated query](https://docs.aws.amazon.com/athena/latest/ug/connect-to-a-data-source.html).
- [Athena Provisioned Capacity](https://docs.aws.amazon.com/athena/latest/ug/capacity-management.html).
- [Apache Iceberg in Athena](https://docs.aws.amazon.com/athena/latest/ug/querying-iceberg.html).
