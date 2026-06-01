# DocumentDB

> **One-line summary.** MongoDB-compatible document database with the Aurora-style distributed storage layer underneath.

## TL;DR

- Speaks the MongoDB wire protocol (currently 5.0 compatibility tier) — your MongoDB drivers and tools (mongosh, mongoexport, ODMs) mostly just work.
- It is **not MongoDB**; AWS reimplemented the protocol on top of its own engine and the Aurora storage layer. Some MongoDB features aren't supported, and behavior in edge cases differs.
- Up to 15 read replicas, multi-AZ storage, up to 64 TiB of storage, automatic failover in seconds.
- Right for "we have MongoDB and we want it managed on AWS without standing up our own cluster." Not necessarily the right answer for a greenfield document workload — **DynamoDB** is usually cheaper and scales further.
- Don't use it as your first NoSQL on AWS unless you specifically need the MongoDB API.

## When to use it

- Lifting and shifting existing MongoDB applications to AWS without rewriting against DynamoDB.
- Document workloads where the team already speaks Mongo and the application is MongoDB-API-bound.
- Workloads that fit the MongoDB feature subset DocumentDB supports.

## When NOT to use it

- Greenfield document workloads on AWS — try **DynamoDB** first; it's cheaper, scales further, and integrates more deeply with the rest of AWS.
- Workloads needing a MongoDB feature DocumentDB doesn't implement (some aggregation operators, change-streams nuances, certain index types). Verify your usage against the [compatibility matrix](https://docs.aws.amazon.com/documentdb/latest/developerguide/mongo-apis.html).
- Workloads that need horizontal write scale across many writers — DocumentDB is single-writer like Aurora.
- Time-series or analytics — Timestream for InfluxDB or Redshift fits better.

## Key concepts

**Cluster.** One writer + up to 15 readers, on top of the Aurora-style distributed storage layer (6 copies across 3 AZs). Cluster has writer and reader endpoints.

**Compatibility.** Currently MongoDB 5.0 wire protocol (with prior 3.6 / 4.0 / 5.0 tiers AWS shipped over time). Some MongoDB features are unsupported or behave differently. Test with your actual workload — *especially* aggregation pipelines and change streams — before committing.

**Storage.** Multi-AZ, auto-grows up to 64 TiB.

**Backups.** Continuous backups, PITR within retention window. AWS Backup integration for vault-locked / cross-Region.

**Elastic clusters** — DocumentDB's sharded variant. Distributes data across shards for write scale beyond a single writer. Has its own constraints; not a transparent superset of a non-elastic cluster.

**Global Clusters.** Cross-Region read replicas with managed failover, similar to Aurora Global Database. RPO seconds; RTO minutes on planned failover.

**Indexes, queries, transactions.** Most common MongoDB index types supported; transactions supported up to defined limits.

**Security.** TLS in transit, KMS encryption at rest, IAM-managed authentication (in addition to MongoDB native auth).

## Pricing model

- **Instance** — per second by class (`db.r6g.large`, `db.r7g.xlarge`, etc.). RIs available.
- **Storage** — per GB-month of actual data stored.
- **I/O** — per million requests against the storage layer.
- **Backup storage** — included up to 100% of cluster.
- **Data transfer** — same AWS rules.

DocumentDB is typically **more expensive than DynamoDB** for equivalent workloads when DynamoDB fits — the pricing reflects the "managed Aurora-style cluster for MongoDB API" cost structure, not a serverless per-request model.

## Quotas & limits

- **Readers per cluster**: 15.
- **Cluster storage**: up to 64 TiB.
- **Instance classes**: limited subset of EC2 families.
- **MongoDB API coverage**: check the docs — some operators, index types, and aggregation stages are unsupported.
- **Elastic clusters** have their own limits, distinct from standard clusters.

## Common pitfalls

- **Assuming feature parity with MongoDB.** Test the actual queries, aggregations, and change-stream usage your app does. The wire protocol matches; the semantics in edge cases sometimes don't.
- **Picking DocumentDB without trying DynamoDB.** For greenfield document workloads, DynamoDB is usually cheaper, scales further, and integrates better with the rest of AWS.
- **Single-AZ compute.** Storage is multi-AZ; compute needs at least one reader in another AZ to actually be HA.
- **Treating it as your search engine.** Even MongoDB Atlas leans on dedicated search; for full-text / fuzzy / faceted search, use OpenSearch.
- **No connection pooling.** Connection storms from serverless callers; pool client-side or front with a proxy.
- **Forgetting the I/O dimension on cost.** I/O charges can dominate a write-heavy workload. Tune indexes; consider whether you actually need the documents you're reading.
- **Major version upgrades treated as routine.** Verify your app's actual query surface still works on the new wire-protocol tier; minor versions of "MongoDB compatibility" can subtly change behavior.

## Pairs well with

- [DynamoDB](dynamodb.md) — the AWS-native alternative for new document workloads.
- **AWS DMS** — migrate from on-prem MongoDB into DocumentDB.
- **AWS Backup** — managed retention.
- **Secrets Manager** — credential rotation.
- **CloudWatch + Performance Insights** — observability.

## Pairs well with these repo pages

- [DynamoDB](dynamodb.md), [Aurora](aurora.md).
- `docs/04-reference-architectures/serverless-rest-api.md` (forthcoming) — when picking between DynamoDB and DocumentDB for the document tier.

## Further reading

- [Amazon DocumentDB documentation](https://docs.aws.amazon.com/documentdb/).
- [MongoDB API compatibility](https://docs.aws.amazon.com/documentdb/latest/developerguide/mongo-apis.html).
- [DocumentDB Elastic Clusters](https://docs.aws.amazon.com/documentdb/latest/developerguide/docdb-using-elastic-clusters.html).
- [Migrating from MongoDB to DocumentDB](https://aws.amazon.com/blogs/database/migrate-from-mongodb-to-amazon-documentdb-using-the-online-method/).
