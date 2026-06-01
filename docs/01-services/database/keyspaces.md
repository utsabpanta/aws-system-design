# Keyspaces (for Apache Cassandra)

> **One-line summary.** Serverless, Cassandra-compatible wide-column store. Speaks CQL; pay per request (on-demand) or per provisioned capacity. Multi-AZ, single- or multi-Region.

## TL;DR

- The right service when you have an existing Cassandra workload (or app code written for Cassandra) and want it managed on AWS without operating a Cassandra ring.
- Speaks the CQL wire protocol — most Cassandra drivers and tools work unchanged. AWS has not implemented every CQL feature; verify against the [supported APIs list](https://docs.aws.amazon.com/keyspaces/latest/devguide/cassandra-apis.html).
- **On-demand** capacity mode for spiky / unknown workloads; **provisioned** mode with autoscaling for steady workloads (much cheaper at scale).
- For *new* wide-column workloads on AWS, DynamoDB is usually a better default — cheaper, more deeply integrated, broader feature set.
- Multi-Region replication via Keyspaces' built-in multi-Region replication (eventual consistency across Regions, similar to DynamoDB Global Tables Standard).

## When to use it

- Existing Cassandra apps lifting to AWS without rewriting against DynamoDB.
- Workloads built against the CQL surface (open-source Cassandra drivers, ORMs that expect Cassandra) that the team doesn't want to refactor.
- Cassandra-shaped workloads (wide rows, time-series at scale, IoT telemetry) that have proven the model.

## When NOT to use it

- New workloads on AWS where you have a free choice — try DynamoDB first.
- Workloads needing strongly-consistent multi-Region writes — DynamoDB MRSC Global Tables fits better.
- Workloads that depend on Cassandra features Keyspaces doesn't implement.
- Workloads where per-request pricing math doesn't beat well-tuned DynamoDB provisioned with Reserved Capacity.

## Key concepts

**Keyspace.** Cassandra's "database" — a container of tables.

**Table.** Wide-column table with a partition key (PK), optional clustering keys (CK), and arbitrary regular columns. Partition keys distribute data; clustering keys order rows within a partition.

**Capacity modes.**

- **On-demand** — pay per request (read / write request units, similar shape to DynamoDB On-Demand). Auto-scales. Right for spiky / new workloads.
- **Provisioned** — set RCU/WCU with auto-scaling. Cheaper at sustained load.

**Consistency.** `LOCAL_ONE`, `LOCAL_QUORUM`, `ONE`, `QUORUM`, etc. The default `LOCAL_QUORUM` gives strong consistency within the Region.

**Multi-Region replication.** Add replicas in additional Regions; replication is asynchronous, multi-active, similar in spirit to DynamoDB Global Tables Standard. No strongly-consistent multi-Region mode (unlike DynamoDB MRSC).

**Backups.** Continuous backups, PITR within a retention window. AWS Backup integration for vault locking and cross-account retention.

**TTL.** Per-row or per-column TTL, with the same caveat as DynamoDB — deletes are background-processed.

**Drivers.** Open-source Cassandra drivers (Java, Python, Go, Node, etc.) — connect via SigV4 plugin (recommended) or username/password.

## Pricing model

- **On-demand** — per million read/write request units. Read units cost less for `LOCAL_ONE` than `LOCAL_QUORUM`.
- **Provisioned** — RCU/WCU per hour with autoscaling; Reserved Capacity discount available.
- **Storage** — per GB-month.
- **Backups (PITR)** — per GB-month.
- **Multi-Region replication** — billed as replicated WCUs in each replica Region.
- **Data transfer** — same AWS rules; cross-Region replication billed as data transfer.

The economic comparison vs DynamoDB depends on workload shape. DynamoDB tends to win on integration cost and feature breadth; Keyspaces wins when the app is already CQL.

## Quotas & limits

- **Row size**: 1 MB.
- **Partition size**: 1 MB sustained / 3 MB peak per partition (rate-limited by partition).
- **Tables per keyspace**: 5,000 default.
- **Provisioned capacity**: high; check current docs.
- **CQL surface**: Keyspaces does **not** implement every Cassandra feature — known gaps include certain LWT semantics, materialized views, secondary indexes (Keyspaces has limited support), counter columns (with caveats), and some configuration knobs Cassandra exposes.

## Common pitfalls

- **Reaching for Keyspaces over DynamoDB for greenfield work.** DynamoDB is usually cheaper, more deeply AWS-integrated, and faster-evolving for new features.
- **Assuming full Cassandra compatibility.** Verify your CQL queries, materialized views, and consistency-level usage against the supported APIs list.
- **Hot partitions.** Same problem as DynamoDB — a single hot PK throttles regardless of provisioned capacity. Design for high cardinality.
- **Large partitions.** Cassandra-style data modeling can produce huge partitions (millions of rows under one PK) — Keyspaces enforces partition size limits more strictly. Plan partition sizing carefully.
- **`QUORUM` reads everywhere.** Reads cost more than `LOCAL_ONE` and `LOCAL_QUORUM`; pick the weakest consistency that satisfies your invariants.
- **On-demand for steady workloads.** Cheaper to provision + RC for predictable patterns.
- **No DR plan.** Multi-Region replication needs to be configured; it's not automatic.
- **Tooling differences.** Some Cassandra ops tools (nodetool, repair, compaction) don't apply — Keyspaces is serverless. Operational habits from on-prem Cassandra need adjustment.

## Pairs well with

- **AWS DMS** — migrate from on-prem Cassandra (with caveats; verify schema compatibility).
- **AWS Backup** — PITR + vault-locked retention.
- **Secrets Manager** — credentials (or use IAM-based SigV4 auth).
- **CloudWatch** — request metrics, throttle counts, partition heat metrics.

## Pairs well with these repo pages

- [DynamoDB](dynamodb.md) — the recommended-first NoSQL on AWS for greenfield workloads.
- [Aurora](aurora.md) / [RDS](rds.md) — when the data actually wants to be relational.

## Further reading

- [Amazon Keyspaces documentation](https://docs.aws.amazon.com/keyspaces/).
- [Supported Cassandra APIs](https://docs.aws.amazon.com/keyspaces/latest/devguide/cassandra-apis.html).
- [Keyspaces multi-Region replication](https://docs.aws.amazon.com/keyspaces/latest/devguide/multiRegion-replication.html).
- [Migrating from Cassandra to Keyspaces](https://docs.aws.amazon.com/keyspaces/latest/devguide/migration.html).
