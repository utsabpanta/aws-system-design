# Kinesis (family)

> **One-line summary.** Four AWS-managed streaming services that share a heritage. **Kinesis Data Streams** (raw streams), **Amazon Data Firehose** (managed delivery to S3 / Redshift / OpenSearch / Splunk), **Amazon Managed Service for Apache Flink** (formerly Kinesis Data Analytics — stream processing), and **Kinesis Video Streams** (media streams).

## TL;DR
- The Kinesis family has been **renamed in pieces**:
  - **Kinesis Data Analytics → Amazon Managed Service for Apache Flink** (August 2023). The legacy **SQL-application flavor was discontinued on January 27, 2026** — migrate to Managed Apache Flink Studio.
  - **Kinesis Data Firehose → Amazon Data Firehose** (February 2024). Same service, broader brand to reflect non-Kinesis sources.
  - **Kinesis Data Streams** and **Kinesis Video Streams** keep the Kinesis name.
- **Pick by job:**
  - **Data Streams** — when you need a Kafka-like ordered, replayable stream you process yourself.
  - **Data Firehose** — when you just want to land streaming data in S3 / Redshift / OpenSearch / Splunk with managed delivery and format conversion.
  - **Managed Apache Flink** — when you need stateful stream processing (windowed aggregations, joins, complex event processing).
  - **Video Streams** — when the data is video / audio / time-series media.
- For large-scale Kafka workloads, **MSK** (Managed Streaming for Kafka) is the AWS-native alternative to Data Streams.

## When to use which

| Need | Use |
|---|---|
| Raw stream, custom consumer, replay window, key-based partitioning | **Kinesis Data Streams** |
| Land streaming data in S3 / Redshift / OpenSearch / Splunk without code | **Amazon Data Firehose** |
| Stateful stream processing (windows, joins, complex event patterns) | **Amazon Managed Service for Apache Flink** |
| Live and recorded video / audio streams | **Kinesis Video Streams** |
| Open-source Kafka API surface, very high scale | **MSK** (see [`msk.md`](msk.md)) |

---

## Kinesis Data Streams

**What it is:** ordered, partitioned, replayable streams. Producers `PutRecord(s)`; consumers read by shard. 24-hour default retention, extendable up to 365 days.

**Capacity modes:**
- **Provisioned** — pay per shard-hour. Each shard handles 1 MB/s in, 2 MB/s out (enhanced fan-out raises read).
- **On-demand** — auto-scale, pay per GB written + read. Right for spiky / unknown traffic.

**Consumers:**
- **Shared throughput consumers** (classic) — multiple consumers share the 2 MB/s per shard.
- **Enhanced fan-out (EFO) consumers** — dedicated 2 MB/s per consumer per shard, push-based. The right default for multiple downstream readers.
- **Lambda event-source mapping** — managed poller; scales Lambda by shard count and batches.
- **Kinesis Client Library (KCL)** — Java / multi-language library for stateful, checkpointed consumers.

**Use cases:** event sourcing, audit log distribution, CDC, IoT ingestion, real-time aggregation pipelines.

**Pitfalls:** hot shards (uneven partition keys), over-provisioned shards (use on-demand for variable load), too-small retention (24 h default can lose data during a downstream outage).

---

## Amazon Data Firehose

**What it is:** the "just deliver this stream to somewhere downstream" service. You configure source + destination + optional transformation; AWS handles batching, retries, and delivery.

**Sources:** **20+ supported**, including Kinesis Data Streams, MSK / MSK Serverless, CloudWatch Logs, IoT Core, SNS, EventBridge, direct PUT via SDK, and partner sources (Datadog, etc.).

**Destinations:** S3, Redshift, OpenSearch Service / Serverless, Splunk, Datadog, Snowflake, generic HTTP endpoints, and more.

**Transformations:**
- **Lambda transformation** — run a Lambda on each record (or batch) to reshape before delivery.
- **Format conversion** — JSON → Parquet / ORC at write time (with a Glue Catalog schema).
- **Dynamic partitioning** — partition by record content (`/year/month/day/` from a field in each record).

**Encryption:** SSE-S3 / SSE-KMS at the destination; TLS in transit.

**Pricing:** per GB ingested + per record transformed (Lambda) + format conversion fee.

**Use cases:** CloudTrail / VPC Flow Log delivery to S3 in Parquet, log aggregation to Splunk / Datadog, IoT telemetry to S3 + OpenSearch.

**Pitfalls:** buffer size / interval determines latency-vs-cost; too-small buffers spawn too many S3 objects; too-large buffers add latency.

---

## Amazon Managed Service for Apache Flink

**What it is:** managed **Apache Flink** for stateful stream processing. Renamed from Kinesis Data Analytics in August 2023.

**Three flavors:**
- **Apache Flink applications** — your Flink JAR (Java / Scala / Python) on AWS-managed Flink. Recent Flink versions tracked.
- **Apache Flink Studio** — managed Flink notebooks with Zeppelin; interactive development on streams. **Recommended migration target for the discontinued Kinesis Data Analytics for SQL.**
- (Discontinued) **Kinesis Data Analytics for SQL** — separate SQL-only product. **Discontinued Jan 27, 2026.** New apps blocked since Oct 15, 2025; existing apps deleted at the discontinuation date.

**Sources / sinks:** Kinesis Data Streams, MSK / Kafka, S3, OpenSearch, Firehose, custom Flink connectors.

**Use cases:** windowed aggregations, joins between streams, anomaly detection, real-time enrichment pipelines, CEP (complex event processing).

**Pricing:** per KPU-hour (Flink Kinesis Processing Unit = 1 vCPU + 4 GB RAM, similar to a Flink slot). Storage and durable state extra.

**Pitfalls:** stateful Flink jobs need careful state-size management; checkpoints can be slow on large state; choose RocksDB vs heap state per workload.

---

## Kinesis Video Streams

**What it is:** ingest, store, and process **video and time-series media** (audio, depth data, RADAR) from devices.

**Two flavors:**
- **Video Streams** — durable storage and time-indexed retrieval of recorded video.
- **WebRTC ingestion** — low-latency peer-to-peer video signaling via WebRTC; the right shape for two-way video, security cameras, video doorbells.

**Integrations:** Rekognition Video for ML inference on streams; SageMaker for custom models; HLS/DASH playback URLs for clients.

**Pricing:** per-GB ingested + storage + GB retrieved + WebRTC channel hours.

**Use cases:** smart cameras, video doorbells, retail analytics from in-store cameras, telemedicine, drone telemetry.

**Pitfalls:** GBs grow fast for high-resolution streams — retention policy is critical; WebRTC channels add per-hour cost regardless of usage.

---

## Pricing summary

| Service | Primary cost |
|---|---|
| Kinesis Data Streams (provisioned) | per shard-hour + per GB in/out |
| Kinesis Data Streams (on-demand) | per GB written + per GB read |
| Amazon Data Firehose | per GB ingested + Lambda invocations + format conversion |
| Managed Apache Flink | per KPU-hour + durable state storage |
| Kinesis Video Streams | per GB ingested + storage + retrieval + WebRTC hours |

## Common pitfalls across the family

- **Picking Data Streams when Firehose would do.** If you just want to land data in S3 / Redshift, Firehose is operationally simpler and often cheaper.
- **Using deprecated Kinesis Data Analytics for SQL after Jan 27, 2026.** Apps are deleted at that date. Migrate to Managed Apache Flink Studio.
- **Confusing the renames in docs / IaC.** Older Terraform / CDK code references the old names; AWS keeps both for compatibility but new docs and pricing pages use the new names.
- **Hot partition keys (Data Streams).** A skewed `PartitionKey` choice = one shard does all the work. Distribute evenly.
- **No retention plan (Video Streams).** Storage costs run away on high-resolution streams.

## Pairs well with
- [S3](../storage/s3.md), [Redshift](../database/redshift.md), [OpenSearch](opensearch.md) — common Firehose destinations.
- [Lambda](../compute/lambda.md) — Data Streams consumer and Firehose transformer.
- [MSK](msk.md) — alternative streaming platform with Kafka semantics.
- [Glue](glue.md) — Catalog for Firehose format conversion; Glue Streaming jobs.
- [Rekognition / SageMaker](../ml-ai/) (forthcoming) — ML on Video Streams.

## Pairs well with these repo pages
- [MSK](msk.md), [Glue](glue.md), [Athena](athena.md), [Redshift](../database/redshift.md), [OpenSearch](opensearch.md).
- `docs/04-reference-architectures/streaming-etl-kinesis.md` (forthcoming).

## Further reading
- [Kinesis Data Streams documentation](https://docs.aws.amazon.com/streams/).
- [Amazon Data Firehose documentation](https://docs.aws.amazon.com/firehose/).
- [Amazon Managed Service for Apache Flink](https://docs.aws.amazon.com/managed-flink/).
- [Kinesis Data Analytics for SQL discontinuation notice](https://docs.aws.amazon.com/kinesisanalytics/latest/dev/discontinuation.html).
- [Kinesis Video Streams documentation](https://docs.aws.amazon.com/kinesisvideostreams/).
