# DynamoDB

> **One-line summary.** AWS's flagship NoSQL key-value and document database — single-digit-millisecond reads at any scale, fully managed, multi-AZ by default, no servers to operate.

## TL;DR

- The default NoSQL on AWS. Pay-per-request or provisioned-capacity, eventual or strong consistency per call, multi-AZ always, multi-Region (Global Tables) opt-in.
- **Multi-Region Strong Consistency (MRSC) Global Tables** (launched 2025) replicate synchronously across 3 Regions for **zero-RPO, 99.999% availability** with strongly-consistent global reads. Limitations: same-account only, no TTL, no LSIs.
- Predictable latency depends on **good key design** — pick a partition key with high cardinality and even access. Hot keys are the operational failure mode that bites every team eventually.
- DynamoDB Streams + Lambda is the native pattern for change-data-capture, fan-out, audit logs, search index sync.
- Single-table design is the AWS-recommended pattern for related entities — confusing at first, dramatically better than many tables once you internalize the access patterns.

## When to use it

- Key-value or document workloads with well-understood access patterns and tight latency SLOs.
- Multi-tenant SaaS where each tenant's data is keyed by tenant ID.
- Event/order/session stores with high write throughput.
- Workloads that need predictable, sub-10ms p99 reads at any scale.
- Multi-Region active-active with strong consistency requirements (MRSC Global Tables).
- Anywhere SQL JOINs and ad-hoc queries are *not* the access pattern.

## When NOT to use it

- Ad-hoc SQL analytics — use Redshift, Athena on S3, or Aurora.
- Highly relational data with complex JOIN-heavy access patterns — use RDS or Aurora.
- Workloads needing complex secondary access patterns you can't predict — Aurora PostgreSQL with indexes is more forgiving.
- Workloads that fundamentally need transactions across many entities — DynamoDB supports transactions up to 100 items, but if you need cross-aggregate transactions across thousands of items, Aurora is a better fit.

## Key concepts

**Table.** A collection of items. No fixed schema beyond the primary key.

**Primary key.**

- **Partition key (PK) only** — items are uniquely identified by PK.
- **Composite (PK + sort key, SK)** — items grouped by PK and ordered within by SK. The fundamental DynamoDB modeling tool.

**Items and attributes.** An item is a row; attributes are columns (typed: string, number, binary, set, list, map, bool, null). Items can have different attributes — the schema is per-item.

**Indexes.**

- **Local Secondary Index (LSI)** — alternate sort key on the same partition. Created at table creation, can't change later. Shares the partition's capacity.
- **Global Secondary Index (GSI)** — alternate PK and optional SK. Can be added/dropped any time. Has its own capacity. Eventually consistent unless using strongly-consistent read on the GSI explicitly (only available on LSIs, not GSIs).

**Read consistency.**

- **Eventually consistent reads** — default, cheaper. May not reflect a write that just succeeded.
- **Strongly consistent reads** — guaranteed to see the most recent successful write. 2× the cost of eventual.

**Capacity modes.**

- **On-Demand** — pay per request. Auto-scales instantly. ~7× more expensive per request than provisioned at equivalent steady-state usage. Right for spiky / new / unknown workloads.
- **Provisioned** — set RCU/WCU limits with auto-scaling. Cheaper at steady-state. Reserved Capacity gives a further discount.

**Transactions.** ACID across up to 100 items in `TransactWriteItems` / `TransactGetItems`. 2× the cost of standard requests. Use for cross-item invariants.

**Streams.** Change log of every item modification, retained 24 hours. Consumed by Lambda for CDC / fan-out / audit. The cleanest "react to DB change" pattern AWS offers.

**TTL.** Auto-expire items after a timestamp attribute passes. Background deletion — items may stick around for hours after expiry before they're actually removed (and you keep paying for storage until then).

**Global Tables.**

- **Standard (eventual consistency)** — async cross-Region replication, RPO seconds, no zero-RPO guarantee. Multi-active.
- **Multi-Region Strong Consistency (MRSC, 2025)** — synchronous cross-Region replication to at least one other Region before write returns. **Exactly 3 Regions** (either 3 full replicas or 2 replicas + 1 witness). 99.999% availability, zero-RPO global reads. Restrictions: same account only, no TTL, no LSIs.
- **Resiliency testing with FIS** for MRSC global tables (added January 2026).

**DynamoDB Accelerator (DAX)** — in-memory cache cluster in front of DynamoDB. Microsecond latency for cached reads. Eventually consistent; transparent to most SDK callers.

**Backups.**

- **On-demand backup** — manual snapshot.
- **PITR (point-in-time recovery)** — continuous backups, restore to any second in the last 35 days.
- **AWS Backup** — managed retention, cross-Region copy, vault lock.

**Export to S3** — full-table or incremental snapshot to S3 in DynamoDB JSON or Ion format. Doesn't consume table RCU. Used for analytics (Athena, Glue, Redshift Spectrum).

## Pricing model

- **On-Demand** — per million read/write request units.
- **Provisioned** — RCU/WCU per hour, with Reserved Capacity discounts (1- or 3-year).
- **Storage** — per GB-month.
- **Streams** — per million reads from the stream.
- **Global Tables** — write replication is billed per **replicated WCU** in each replica Region.
- **PITR** — per GB-month of continuous backup.
- **DAX** — node-hours per cluster, like EC2.
- **Data transfer** — same AWS rules; cross-Region replication for Global Tables billed as data transfer.

Two enormous cost levers:

1. **Provisioned + Reserved + auto-scaling** instead of On-Demand for predictable workloads (~7× cheaper).
2. **Eventual consistency** when strong isn't required (~½ the cost).

## Quotas & limits

- **Item size**: 400 KB max.
- **Tables per Region**: 2,500 default.
- **GSIs per table**: 20 (raisable to 50).
- **LSIs per table**: 5 (immutable after table creation).
- **Transactions**: 100 items, 4 MB total.
- **BatchGetItem / BatchWriteItem**: 100 / 25 items.
- **On-demand peak throughput**: instantly scales to recent peak × 2, or to any specified peak; for fresh tables, requests beyond initial peak get throttled.
- **MRSC Global Tables**: exactly 3 Regions; same-account only; no TTL or LSIs.

## Common pitfalls

- **Hot partition keys.** A single hot key throttles regardless of provisioned capacity (DynamoDB partitions are bounded). Spread access — random suffix, hash prefix, time bucketing.
- **Scan in production.** `Scan` reads the whole table; almost always wrong. Use `Query` against a PK and (optionally) SK range; create a GSI if you need a different access pattern.
- **No back-of-the-envelope for capacity.** "We'll use On-Demand" works until the bill arrives. Estimate RCU/WCU early; switch to Provisioned for steady workloads.
- **Strong consistency everywhere.** Strong reads cost 2× and aren't needed for most reads. Default to eventual; mark strong where the invariant requires it.
- **GSI projection too narrow.** A GSI that doesn't project the needed attributes forces a second table read per item. Project the attributes you actually need.
- **Single-table design done wrong.** Without a clear access-pattern map, single-table design becomes an undebuggable mess. Document the patterns, label items with a `type` attribute, use composite SKs.
- **DynamoDB as your search engine.** Substring search, fuzzy search, faceted search — these are OpenSearch problems, not DynamoDB problems.
- **Cross-region multi-active with eventual Global Tables and "we need strong consistency."** Eventually consistent. Use MRSC if you can live with its restrictions, otherwise architect around the eventual model.
- **TTL as a hard deadline.** TTL deletes are background-processed; an item may live hours past its expiry. Don't rely on TTL for security-sensitive expiration.

## Pairs well with

- **DynamoDB Streams + Lambda** — change-data-capture, fan-out, audit.
- **DAX** — microsecond cache layer.
- **EventBridge Pipes** — streams → SQS / SNS / Step Functions / API destinations with filtering and transformation.
- **AWS Backup** — vault-locked retention.
- **OpenSearch** — for the search queries DynamoDB can't.
- **Athena / Glue / Redshift Spectrum** — analytics on exported snapshots.

## Pairs well with these repo pages

- [RDS](rds.md) / [Aurora](aurora.md) — the SQL alternatives.
- [ElastiCache](elasticache.md) — when DAX isn't a fit or you need Redis-style data structures.
- `docs/02-patterns/idempotency.md` (forthcoming) — DynamoDB conditional writes are a clean idempotency primitive.

## Further reading

- [Amazon DynamoDB documentation](https://docs.aws.amazon.com/dynamodb/).
- [DynamoDB Best Practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html).
- [Multi-Region Strong Consistency Global Tables](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/V2globaltables_HowItWorks.html).
- [DynamoDB Streams](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Streams.html).
- "The DynamoDB Book", Alex DeBrie — the canonical single-table-design reference.
