# MSK (Managed Streaming for Apache Kafka)

> **One-line summary.** Managed **Apache Kafka** clusters. Standard Kafka API, AWS-operated brokers, with **MSK Serverless** as the no-cluster-sizing option.

## TL;DR
- The right choice when your workload depends on the **Kafka API** (open-source clients, Kafka Connect, ksqlDB, Flink Kafka connectors) and you don't want to operate brokers.
- Two flavors: **MSK Provisioned** (you pick instance type and count, persistent storage size, Kafka version) and **MSK Serverless** (no broker sizing — auto-scales).
- For workloads that don't strictly need the Kafka API, **Kinesis Data Streams** is operationally simpler and tightly integrated with AWS. For Kafka-bound workloads, MSK is the path.
- **IAM auth** for Kafka API access (in addition to SASL/SCRAM, mTLS) — eliminates Kafka-specific credential management for many use cases.
- **MSK Connect** runs managed Kafka Connect plugins (Debezium, S3 sink, Elasticsearch sink, etc.) so you don't manage Connect workers.

## When to use it
- Workloads that depend on the Kafka client / ecosystem (Kafka Streams, Flink Kafka connector, Kafka Connect, ksqlDB, Confluent components).
- Migrating from self-managed or on-prem Kafka.
- Very high-throughput streaming (gigabytes/sec sustained) where Kinesis on-demand pricing becomes expensive.
- Multi-team event platforms standardized on Kafka semantics (partitions, consumer groups, offsets).

## When NOT to use it
- New AWS-native streaming where Kafka isn't a requirement — **Kinesis Data Streams** is simpler and cheaper at small scale.
- "Just land streaming data in S3" — **Amazon Data Firehose**.
- Pub/sub fanout to a known set of subscribers — **SNS + SQS** or **EventBridge**.

## Key concepts

### MSK Provisioned
- **Cluster** with broker instances (`kafka.m7g.large`, `kafka.m7g.4xlarge`, etc.; Graviton broadly supported).
- **Brokers** spread across multiple AZs (1–6 brokers per AZ; 2 or 3 AZs typical).
- **Storage** — per-broker EBS volumes; size at creation, expand later.
- **Kafka versions** — AWS tracks open-source Kafka releases (3.x family in 2026); upgrade with maintenance window.
- **Tiered storage** — older log segments transparently offloaded to S3-backed tier; cheaper long retention.

### MSK Serverless
- No broker sizing. Just create a cluster, create topics, write/read.
- Auto-scales partitions, throughput, storage.
- **IAM auth only** (no SASL/SCRAM / mTLS on Serverless).
- Per-cluster + per-partition + per-GB pricing; good for spiky / unknown load.

### Authentication
- **IAM authentication** (recommended for AWS-native workloads) — Kafka clients authenticate using SigV4; topic-level permissions via IAM.
- **SASL/SCRAM** — username/password stored in Secrets Manager.
- **mTLS** — client certs via ACM Private CA.
- **Unauthenticated** — only for closed VPC, internal-only clusters.

### Encryption
TLS in transit (mandatory for IAM and SASL); KMS at rest. Inter-broker TLS optional but recommended.

### MSK Connect
Managed **Kafka Connect** — runs source / sink connectors as managed AWS workers. Plugin support for Debezium (CDC), S3 sink, OpenSearch sink, JDBC source/sink, MongoDB, MQTT, Salesforce, etc. Eliminates running your own Connect worker fleet.

### Schema Registry integration
**AWS Glue Schema Registry** integrates with MSK clients for Avro / JSON Schema / Protobuf — producers register schemas; consumers validate.

### Observability
**Open Monitoring with Prometheus** — JMX and node exporters on each broker; scrape with self-managed Prometheus or **Amazon Managed Service for Prometheus**.

CloudWatch metrics for cluster, broker, topic, partition level.

### Networking
Brokers in your VPC. Reachable via standard Kafka bootstrap brokers list. Public access optional (Provisioned only, with caveats).

## Pricing model

### MSK Provisioned
- **Per broker-hour** by instance class.
- **Storage** — per GB-month EBS.
- **Tiered storage** — per GB-month for S3-backed tier (cheaper).
- **Data transfer** — same AWS rules (cross-AZ replication and client traffic billed).

### MSK Serverless
- **Per cluster-hour**.
- **Per partition-hour** beyond included quota.
- **Per GB written / read**.

### MSK Connect
- **Per worker-hour** for connector capacity.

MSK Provisioned with Reserved Instances + tiered storage for old segments + Graviton brokers is the cost-optimized production pattern for large Kafka workloads. MSK Serverless is better for spiky or new workloads.

## Quotas & limits

- **Brokers per cluster (Provisioned)**: 30 default (raisable).
- **Storage per broker**: up to 16 TiB.
- **Partitions per cluster (Provisioned)**: 6,000+ (instance-class dependent; recent brokers handle more).
- **Throughput per cluster (Serverless)**: GBs/sec aggregate; auto-scales.
- **Connectors per MSK Connect cluster**: bounded; check current docs.
- **Tiered storage retention**: years (vs hot-tier days–weeks).

## Common pitfalls

- **Brokers across only one AZ.** AZ failure = quorum loss. Always multi-AZ.
- **No tiered storage on long-retention topics.** Hot-tier EBS for years of retention is much more expensive than tiered storage to S3.
- **Skipping IAM auth.** SASL/SCRAM passwords stored anywhere are weaker than IAM-issued short-lived credentials.
- **Over-partitioning.** Partition count is hard to reduce; pick deliberately. Default of "lots of partitions to leave room for parallelism" can hurt at scale.
- **Self-managed Kafka Connect.** MSK Connect removes the cluster-management burden; use it.
- **Public-access cluster.** Risk surface; almost always wrong for production. Stay private; reach via VPC peering / Transit Gateway / PrivateLink.
- **No monitoring beyond CloudWatch defaults.** Kafka-specific JMX metrics matter (under-replicated partitions, consumer lag). Enable Open Monitoring with Prometheus.
- **Forgetting Kafka version upgrades.** AWS supports specific versions; older ones lose support over time.

## Pairs well with
- [Kinesis](kinesis.md) — alternative streaming platform; sometimes paired (Data Firehose can read from MSK).
- [Glue](glue.md) — Schema Registry, Glue Streaming jobs read from MSK.
- **MSK Connect** — managed connectors for Debezium, S3 sink, etc.
- [Managed Apache Flink](kinesis.md) — Flink jobs that source/sink Kafka topics.
- [EventBridge Pipes](../integration-messaging/pipes.md) — MSK is a supported source.
- **Amazon Managed Service for Prometheus + Grafana** — Kafka-native observability.

## Pairs well with these repo pages
- [Kinesis](kinesis.md), [Glue](glue.md), [Lambda](../compute/lambda.md).
- `docs/04-reference-architectures/streaming-etl-kinesis.md` (forthcoming).

## Further reading
- [Amazon MSK documentation](https://docs.aws.amazon.com/msk/).
- [MSK Serverless](https://docs.aws.amazon.com/msk/latest/developerguide/serverless.html).
- [MSK Connect](https://docs.aws.amazon.com/msk/latest/developerguide/msk-connect.html).
- [IAM auth for MSK](https://docs.aws.amazon.com/msk/latest/developerguide/iam-access-control.html).
- [MSK tiered storage](https://docs.aws.amazon.com/msk/latest/developerguide/msk-tiered-storage.html).
