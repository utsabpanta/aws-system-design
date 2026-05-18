# Lake Formation

> **One-line summary.** Centralized **fine-grained permissions** on the Glue Data Catalog. Grant per-database / table / column / row / cell access without managing S3 bucket policies for every dataset.

## TL;DR
- The right layer for "we have many people / teams / accounts querying a shared data lake; we need to govern access at the table / column / row level, not at the S3 path level."
- Replaces per-bucket / per-prefix IAM gymnastics with a **catalog-centric** permission model.
- Permissions flow into **Athena, Redshift Spectrum, EMR, Glue jobs, QuickSight, S3 Tables** — all the engines that query through the Glue Data Catalog honor Lake Formation.
- **LF-Tags** (tag-based access control) scale better than per-resource grants in large catalogs.
- Cross-account sharing via **Resource Links** + **AWS RAM** — the canonical pattern for a "central data lake account, consumer analytics accounts" topology.

## When to use it
- Shared data lakes with multiple consumers (analyst teams, data scientists, downstream apps).
- Multi-account analytics platforms with a central data-lake account.
- Compliance that requires per-column / per-row access control (PCI, HIPAA, GDPR).
- Cross-account data sharing without copying data.

## When NOT to use it
- Single-team data lake with one engine — direct IAM + Glue / Athena permissions can be enough.
- Workloads not going through Glue Data Catalog (e.g., direct-S3 access from non-catalog engines) — Lake Formation requires the catalog as the access boundary.
- Tiny accounts where the operational complexity of LF outweighs the granular access benefit.

## Key concepts

**Data Lake admin.** IAM identity authorized to register S3 locations with Lake Formation and grant permissions. Bootstrapping role.

**Registered S3 locations.** Tell Lake Formation "this S3 prefix is managed data" — LF can then issue short-lived per-query credentials to engines accessing data there, instead of relying on broad IAM/bucket policies.

**Catalog permissions.** Grant per-database / per-table / per-column / per-row / per-cell permissions to IAM principals (users, roles, SAML identities). Standard verbs: `SELECT`, `INSERT`, `DELETE`, `ALTER`, `DROP`, plus catalog-level (`CREATE_DATABASE`, etc.).

**Row-level security and cell-level security.** Define **data filters** (`region = 'US'` predicates) and attach them to permission grants. The engine enforces the filter transparently.

**Column-level security.** Grant access to specific columns; exclude sensitive ones (`ssn`, `email`).

**LF-Tags (tag-based access control).** Attach tags to catalog resources (database / table / column); grant permissions by tag rather than per-resource. Critical for large catalogs.

**Cross-account sharing.**
- **Direct grant** — grant a table to an external account; consumer creates a **Resource Link** in their catalog.
- **AWS RAM** — share the catalog resource via Resource Access Manager.

Consumer engines see the shared table as if it were local; LF enforces permissions on every query.

**Governed tables.** Lake Formation table type with ACID transactions and time-travel. Largely superseded by **Apache Iceberg** / **S3 Tables**; new workloads should default to Iceberg.

**Storage Optimizer.** Background compaction for governed tables.

**Audit.** Permission grants and data access logged in CloudTrail; queryable for compliance review.

## Pricing model

- **Lake Formation itself is free** — no per-grant or per-query fee.
- Underlying **Glue Data Catalog** charges apply (per 100K objects + per 1M requests).
- **Underlying compute** (Athena, Redshift Spectrum, EMR, Glue jobs) charged as normal.
- **Governed tables** add Storage Optimizer compute and storage costs (use Iceberg / S3 Tables instead for new workloads).

The economic argument is operational, not direct cost: LF replaces hand-rolled IAM / bucket policies that take engineering time to maintain.

## Quotas & limits

- **LF-Tags per account per Region**: 1,000.
- **Tag values per tag**: 1,000.
- **Tags per resource**: 50.
- **Permissions grants per principal**: very high.
- **Cross-account sharing**: bounded by AWS RAM quotas.

## Common pitfalls

- **Half-adopted Lake Formation.** Some tables LF-managed, some not — engines see inconsistent permissions. Adopt all-in for a catalog.
- **Per-resource grants instead of LF-Tags.** Doesn't scale. LF-Tags are the right primitive at >100 tables.
- **Cross-account sharing without Resource Links.** Consumer can't query directly without the Resource Link in their own catalog.
- **Governed tables for new workloads.** Use **Apache Iceberg** / **S3 Tables** instead — they have better engine support and AWS's investment.
- **Skipping audit log review.** LF permission grants and queries are CloudTrail-logged; without periodic review, drift accumulates.
- **Engine version mismatch.** Older engine versions may not respect newer LF features (row-level security, cell-level masking). Track minimum-version requirements per engine.
- **Hybrid: some access via direct S3 IAM, some via LF.** Bypass paths exist. Lock down S3 access so the only way to read managed data is through LF-aware engines.

## Pairs well with
- [Glue](glue.md) — Data Catalog backbone.
- [Athena](athena.md), [EMR](emr.md), [Redshift](../database/redshift.md) Spectrum — engines honoring LF permissions.
- [QuickSight](quicksight.md) — downstream BI consumer.
- **AWS Resource Access Manager (RAM)** — cross-account sharing.
- [S3 Tables](../storage/s3.md) — newer table format that integrates with LF for permissions.

## Pairs well with these repo pages
- [Glue](glue.md), [Athena](athena.md), [Redshift](../database/redshift.md), [S3](../storage/s3.md).
- `docs/04-reference-architectures/data-lake-on-s3.md` (forthcoming).

## Further reading
- [AWS Lake Formation documentation](https://docs.aws.amazon.com/lake-formation/).
- [LF-Tags](https://docs.aws.amazon.com/lake-formation/latest/dg/tag-based-access-control.html).
- [Row-level and cell-level security](https://docs.aws.amazon.com/lake-formation/latest/dg/data-filters-about.html).
- [Cross-account data sharing](https://docs.aws.amazon.com/lake-formation/latest/dg/cross-account-permissions.html).
- [Lake Formation best practices](https://docs.aws.amazon.com/lake-formation/latest/dg/best-practices.html).
