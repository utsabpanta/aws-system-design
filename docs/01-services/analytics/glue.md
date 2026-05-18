# Glue

> **One-line summary.** Serverless data integration — ETL/ELT jobs, schema discovery, and the shared **Data Catalog** that Athena, EMR, Redshift Spectrum, Lake Formation, and partners all read from.

## TL;DR
- Three things in one service: **Data Catalog** (a Hive-compatible metastore), **Crawlers** (auto-discover schemas in S3 / databases), and **Jobs / Workflows** (serverless Spark + Python ETL).
- The **Glue Data Catalog** is *the* AWS metadata layer. Athena, EMR, Redshift Spectrum, Lake Formation, S3 Tables, and dozens of partners read from it.
- Jobs run on Spark (Scala / PySpark / SparkSQL) or Python ("Python Shell"). Recent versions (Glue 4.x / 5.x) sit on modern Spark and add **Glue Studio** as the visual job builder.
- **DPU-second** pricing — pay for what you actually use. **Glue Data Quality** adds managed quality checks; **Glue DataBrew** adds a low-code transformation UI.
- The biggest cost mistake is leaving job concurrency / DPU counts at defaults — right-size based on your data.

## When to use it
- Build the catalog for a data lake (S3 + Glue + Athena is the canonical pattern).
- Serverless Spark ETL when you don't want to run an EMR cluster.
- Schema discovery / inference on incoming data (CSV / JSON / Parquet drops in S3).
- ELT into Redshift or Snowflake from S3-based sources.
- Pipelines orchestrated via Glue Workflows or Step Functions / EventBridge.

## When NOT to use it
- Long-running, custom Spark workloads with non-Glue dependencies — use **EMR** or **EMR Serverless**.
- Stream processing — use **Managed Service for Apache Flink** (formerly Kinesis Data Analytics).
- Tiny one-off transforms — sometimes a Lambda is simpler.
- Airflow-orchestrated pipelines — use **MWAA** for the orchestration; Glue can still be the executor.

## Key concepts

### Glue Data Catalog
A managed Hive-compatible metastore. Databases, tables, partitions, columns, and connection definitions. Used by Athena, EMR, Redshift Spectrum, Lake Formation, Spark, Trino, Presto, Snowflake (via connector), etc.

- **Database** — namespace.
- **Table** — schema + S3 location (or database connection).
- **Partition** — sub-directory / per-key slice.
- **Connection** — credentials / endpoint for JDBC / Kafka / MongoDB sources.

### Crawlers
Scan a data source (S3 path, JDBC database, MongoDB) and infer schema, then register tables and partitions in the Data Catalog. Schedule them or run on demand. Useful for the "new files keep landing in S3" pattern.

### Jobs
Serverless code execution:
- **Spark jobs** — PySpark / Scala / SparkSQL on Glue's managed Spark (recent: Glue 4.x / 5.x; tracks Apache Spark releases).
- **Python Shell jobs** — small Python scripts (no Spark cluster).
- **Ray jobs** — distributed Python on Ray.
- **Streaming jobs** — Spark Structured Streaming sources from Kinesis / MSK / Kafka.

### Glue Studio
Visual job builder for the "drag-and-drop ETL" use case. Generates the underlying PySpark code; you can drop into code mode at any point.

### Workflows
Glue's built-in orchestration — chain crawlers + jobs + triggers (schedule, event, conditional). Simpler than Step Functions for data-pipeline-only flows; less general.

### Data Quality
Managed data-quality checks. Define rules (column not null, value in range, freshness threshold) via the **DQDL** DSL or autogenerate from data profile. Failures emit findings to CloudWatch / EventBridge.

### DataBrew
Low-code visual data preparation tool. Profile data, define cleaning recipes, run as Glue jobs.

### Glue connections
Stored connection definitions (JDBC, JDBC + Secrets Manager, MongoDB, Kafka). Jobs reference connections by name; credentials don't live in job code.

### Glue Schema Registry
Schema versioning for streaming data (Avro / JSON / Protobuf). Producers register schemas; consumers validate. Integrated with MSK, Kinesis, and the Kafka client.

## Pricing model

- **Spark jobs** — per DPU-second. A DPU = 4 vCPU + 16 GB RAM.
- **Python Shell jobs** — per smaller unit (1/16 DPU equivalent).
- **Ray jobs** — per DPU-second.
- **Crawlers** — per DPU-second.
- **Data Catalog** — per 100K objects stored + per 1M requests (cheap; first 1M objects free).
- **Data Quality** — per DPU-second for evaluations.
- **DataBrew** — per session-hour + per node-hour for executions.

The dominant cost is usually job DPU-seconds. Right-size DPUs and prune unused jobs.

## Quotas & limits

- **Tables per database**: 1 million.
- **Concurrent job runs**: per account / per job, raisable.
- **Job timeout**: configurable; default 48 hours.
- **DPU count per job**: configurable; up to 100 default (raisable).
- **Crawler concurrency**: bounded.
- **Glue Spark workers**: G.1X / G.2X / G.4X / G.8X size options, plus FlexExecution for cost-sensitive flexible-timing workloads.

## Common pitfalls

- **Over-provisioned DPUs.** Default 10 DPUs for a small job is wasted money. Profile small to start; right-size with Glue's job-metrics dashboard.
- **Crawlers run too often.** Crawlers scan; expensive on huge buckets. Schedule them based on actual change patterns; consider partition projection on Athena to avoid crawler dependence.
- **Glue 2.x / 3.x for new jobs.** Use the current Glue version (4.x / 5.x) for newer Spark features and better performance.
- **Hard-coded credentials in job code.** Use Glue connections with Secrets Manager.
- **No Data Quality.** Garbage data flows downstream silently. Add quality checks at ingest.
- **Glue Workflows for everything orchestrated.** They're fine for Glue-only flows; for cross-service orchestration use Step Functions.
- **Glue jobs that ignore bookmarks.** Bookmarks track processed data so a job can skip already-processed input. Without them, jobs re-process everything every run.
- **Custom Python deps not packaged correctly.** Glue's `--additional-python-modules` / extra files arguments are how you ship dependencies; rolling your own often breaks.

## Pairs well with
- [Athena](athena.md) — primary catalog consumer.
- [S3](../storage/s3.md), **S3 Tables** — data lake storage.
- [EMR](emr.md) — alternative compute for heavier Spark workloads.
- [Lake Formation](lake-formation.md) — fine-grained permissions on Catalog.
- [Step Functions](../integration-messaging/step-functions.md) — orchestrate Glue jobs in larger flows.
- [Kinesis / MSK](kinesis.md) — streaming sources for Glue Streaming jobs.

## Pairs well with these repo pages
- [Athena](athena.md), [Lake Formation](lake-formation.md), [EMR](emr.md), [Redshift](../database/redshift.md).
- `docs/04-reference-architectures/batch-etl-glue.md`, `docs/04-reference-architectures/data-lake-on-s3.md` (forthcoming).

## Further reading
- [AWS Glue documentation](https://docs.aws.amazon.com/glue/).
- [Glue Data Catalog](https://docs.aws.amazon.com/glue/latest/dg/components-overview.html#data-catalog-intro).
- [Glue Studio](https://docs.aws.amazon.com/glue/latest/ug/what-is-glue-studio.html).
- [Glue Data Quality](https://docs.aws.amazon.com/glue/latest/dg/glue-data-quality.html).
- [Glue Schema Registry](https://docs.aws.amazon.com/glue/latest/dg/schema-registry.html).
