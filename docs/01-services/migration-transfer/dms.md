# DMS (Database Migration Service)

> **One-line summary.** Managed database migration and continuous replication. Move databases (heterogeneous or homogeneous) to AWS with minimal downtime, plus managed schema conversion via the integrated DMS Schema Conversion.

## TL;DR
- Replicates data between sources and targets, including across engines (Oracle → Aurora PostgreSQL, SQL Server → Amazon RDS for SQL Server, MySQL → Aurora MySQL, Mongo / DynamoDB / Kinesis as sources or targets).
- **Two compute modes**: **Replication instances** (classic; you pick instance size) and **DMS Serverless** (auto-scales capacity, pay-per-use).
- **DMS Schema Conversion** is the integrated schema/code converter (replacing the older standalone AWS SCT for most workflows). Now includes **generative-AI-assisted conversion**.
- **CDC (Change Data Capture)** mode keeps the target in sync continuously — the canonical zero-downtime cutover pattern.
- ⚠️ **DMS Fleet Advisor is being discontinued on May 20, 2026.** Move off Fleet Advisor before that date; alternatives include AWS Transform (migration assessment) and direct DMS planning.

## When to use it
- Heterogeneous database migrations (different source / target engines).
- Homogeneous lift-and-shift (Oracle on-prem → Oracle on RDS / EC2).
- Continuous CDC replication for analytics pipelines (OLTP → S3 / Redshift / Kinesis).
- Zero-downtime cutover via CDC + final switchover window.
- Database consolidation (many sources → one target).
- Ongoing replication between environments (prod → preprod for analytics).

## When NOT to use it
- Migrations where you'd be better off with **AWS DataSync** (file-based) or native engine tools (`mysqldump`, `pg_dump`, AWS Backup).
- Tiny one-off migrations where setting up DMS is heavier than the alternative.
- Workloads where Zero-ETL integrations already cover the use case ([Redshift Zero-ETL from RDS / Aurora / DynamoDB](../database/redshift.md)).

## Key concepts

### Replication topology
- **Source** — the database being migrated from.
- **Target** — the destination database.
- **Endpoint** — DMS's reference to the source / target (connection config + credentials).
- **Replication instance / Serverless capacity** — runs the migration.
- **Replication task** — defines what tables / collections to migrate, migration type, transformations.

### Migration types
- **Full Load** — copy existing data once.
- **Full Load + CDC** — initial copy + continuous replication of changes (the zero-downtime pattern).
- **CDC only** — assume target has the data; just replicate ongoing changes.

### Compute modes
- **Replication instances** — pick instance class (`dms.r6i.large`, etc.). You manage capacity.
- **DMS Serverless** — AWS provisions / scales capacity based on workload. Pay per DCU-hour (DMS Capacity Unit). Best for variable or unknown workloads; not always cheaper at steady-high load.

### DMS Schema Conversion
- Integrated schema / code converter (replaces the older standalone **AWS Schema Conversion Tool (SCT)** for most use cases).
- Always serverless under DMS.
- **Generative-AI-assisted conversion** improves on rule-based conversion for complex stored procedures, triggers, and proprietary engine code.
- Output: converted SQL artifacts you review and apply to the target.

### Sources (broad list)
Oracle, MS SQL Server, PostgreSQL, MySQL, MariaDB, MongoDB, IBM Db2, SAP ASE, Amazon S3, Azure SQL Database, Google Cloud SQL, DocumentDB, IBM Informix, IBM Db2 for z/OS.

### Targets (broad list)
PostgreSQL (RDS / Aurora), MySQL (RDS / Aurora), Amazon Redshift, Amazon S3, DynamoDB, OpenSearch, Kinesis Data Streams, Kafka (MSK / self-managed), Neptune, DocumentDB.

### Transformations
Per-table / per-column transformations (rename, type coercion, filter rows) during migration.

### Validation
**Data validation** compares source and target row-by-row to ensure the migration was correct. Configurable per task.

### Premigration assessment
DMS analyzes the source schema and reports likely issues (unsupported features, large objects, foreign-key implications).

### DMS Fleet Advisor (discontinued 2026-05-20)
- Was a tool for discovering on-prem databases and assessing migration paths.
- **No longer available after 2026-05-20.**
- Migration alternatives: **AWS Transform** for AI-driven migration assessment, or manual planning.

## Pricing model

- **Replication instances** — per-instance-hour by class.
- **DMS Serverless** — per DCU-hour.
- **DMS Schema Conversion** — per source object converted.
- **Data transfer / storage** at standard AWS rates.

For one-off migrations, the per-hour cost adds up only over the migration window; for ongoing CDC replication, costs are continuous.

## Quotas & limits

- **Replication instances per account per Region**: 100 default.
- **Endpoints per account per Region**: 100 default.
- **Replication tasks per account per Region**: 600 default.
- **Tables per task**: thousands.
- **Concurrent serverless capacity**: bounded; auto-scales within limits.

## Common pitfalls

- **Full Load only when source is changing.** Without CDC, the target is stale by the time you cut over. Always Full Load + CDC for live sources.
- **No validation enabled.** "Looks done" is not done. Run validation; investigate every mismatch.
- **Schema Conversion ignored for cross-engine migrations.** Direct DMS without converted schema = type mismatches and broken queries. Convert first.
- **Replication instance too small.** Under-sized instances throttle; CDC lag accumulates. Right-size based on source change rate.
- **One huge task with thousands of tables.** Slow, hard to debug. Split into multiple tasks per logical group.
- **Source DB underestimated impact.** CDC reads from the source's redo / transaction logs; can add load. Monitor source health.
- **Fleet Advisor still in use after 2026-05-20.** Plan now.
- **Skipping Premigration Assessment.** Surprises mid-migration. Run the assessment, address findings.
- **Cross-Region replication without thinking about bandwidth.** Big migrations across Regions need a plan (Direct Connect helps).

## Pairs well with
- [RDS](../database/rds.md), [Aurora](../database/aurora.md), [Redshift](../database/redshift.md), [DynamoDB](../database/dynamodb.md), [DocumentDB](../database/documentdb.md), [Neptune](../database/neptune.md) — common targets.
- [S3](../storage/s3.md), [Kinesis](../analytics/kinesis.md), [MSK](../analytics/msk.md) — streaming-ETL targets.
- [DataSync](datasync.md) — file-based companion for non-database data.
- [MGN](mgn.md) — server-level migration (DMS handles databases, MGN the server).
- **AWS Transform** — newer AI-driven migration planning.

## Pairs well with these repo pages
- [MGN](mgn.md), [DataSync](datasync.md), [Migration Hub](migration-hub.md).

## Further reading
- [AWS DMS documentation](https://docs.aws.amazon.com/dms/).
- [DMS Schema Conversion](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_SchemaConversion.html).
- [DMS Serverless](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Serverless.html).
- [DMS Fleet Advisor discontinuation](https://aws.amazon.com/products/lifecycle/).
- [AWS Transform](https://aws.amazon.com/migration-hub/features/).
