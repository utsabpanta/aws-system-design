# FinSpace

> **One-line summary.** Managed data management and analytics for financial-services workloads — specifically built around **kdb+/q** (KX systems) and time-series financial data.

## Status

> 🛑 **Amazon FinSpace is being shut down.**
>
> - **Closed to new customers since October 7, 2025.**
> - **End of support: October 7, 2026.** After that date, console access and resources go away.
>
> Existing customers can continue to use the service through October 7, 2026; AWS continues security / availability patches but not new features.
>
> **Migration:** AWS guidance is to extract kdb data and application code to S3, then run kdb+ on AWS-self-managed compute (EC2 / EKS / your own kdb cluster). For non-kdb dataset-browser use cases, evaluate alternative analytics tools (Lake Formation + Athena, Snowflake, Databricks).
>
> This page documents FinSpace for existing users and migration reference.

## TL;DR

- FinSpace launched as the AWS-managed home for **kdb+/q** workloads (the dominant tick-data / time-series engine in capital markets) and a dataset-browser product for cross-organization financial data sharing.
- AWS is **discontinuing FinSpace** on October 7, 2026.
- For existing customers, the migration is non-trivial — kdb+ runs on specific licensed software, and the workloads tend to be tightly-coupled financial-analytics pipelines. Plan early.
- For *new* time-series workloads, **Timestream for InfluxDB** (or self-managed kdb on EC2 / EKS for licensed kdb shops) is the path forward; for general data sharing, **Lake Formation + Data Exchange**.

## What it was

FinSpace targeted financial-services-specific needs:

- **Managed kdb Insights** — AWS-managed kdb+/q clusters with KX's commercial Insights distribution.
- **Dataset Browser** — a catalog and access-management tool for sharing curated financial datasets within an organization.
- Compliance-aligned features (audit trail, attribute-level access control).

It addressed the operational toil of running kdb+ at scale: cluster sizing, data tiering between memory and historical storage, snapshots, and cross-team data sharing.

## Migration paths

### For kdb workloads

AWS-published guidance:

1. Extract database contents (HDB, RDB) and application code to S3.
2. Set up kdb+ on AWS compute of your choice — EC2 (Graviton supported), EKS, or Outposts.
3. Use your own KX commercial license (FinSpace bundled this).
4. Re-establish ingest pipelines (Kinesis, MSK, custom) into the new self-managed cluster.
5. Cutover applications.

Self-managed kdb on AWS is well-trodden territory — many financial firms ran kdb on AWS before FinSpace existed.

### For non-kdb / dataset-browser workloads

- **Lake Formation + Glue Data Catalog** for centralized governance.
- **AWS Data Exchange** for cross-organization data sharing (if relevant).
- **QuickSight, Athena, Redshift** for the analytics layer.

## Pricing model (legacy)

- Per-environment / per-cluster hourly fees that bundled KX licensing.
- Storage tiered between memory, EBS, and S3.

No future pricing relevance; new subscriptions are not accepted.

## Common pitfalls (for existing users in migration)

- **Treating the October 2026 deadline as far away.** kdb migrations are large multi-team efforts — building a self-managed kdb cluster, validating it matches the FinSpace environment's behavior, and cutting over financial workloads typically takes many months.
- **No license plan.** FinSpace bundled KX commercial licensing; self-managed requires your own.
- **Re-platforming financial pipelines without parallel-run.** Run old and new in parallel before cutover; financial data lineage matters.
- **Skipping a "what should we even do with this data going forward" review.** Some workloads might fit a different stack (Timestream for InfluxDB for telemetry-style time-series; managed Spark / Snowflake for batch analytics) than a like-for-like kdb migration.

## Pairs well with these repo pages

- [Lake Formation](lake-formation.md), [Data Exchange](data-exchange.md) — alternative governance / sharing primitives.
- [Timestream](../database/timestream.md) — managed time-series for non-kdb use cases.
- [EC2](../compute/ec2.md), [EKS](../compute/eks.md) — hosts for self-managed kdb after migration.

## Further reading

- [Amazon FinSpace end-of-support notice](https://docs.aws.amazon.com/finspace/latest/userguide/amazon-finspace-end-of-support.html).
- [AWS Data Exchange documentation](https://docs.aws.amazon.com/data-exchange/) — for the dataset-sharing replacement path.
- [Migrate kdb Insights to self-managed kdb on AWS](https://docs.aws.amazon.com/finspace/latest/userguide/amazon-finspace-end-of-support.html) (AWS-published guidance).
- [KX kdb+ documentation](https://code.kx.com/q/) — for the engine itself.
