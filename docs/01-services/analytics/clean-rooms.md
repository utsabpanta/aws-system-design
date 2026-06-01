# Clean Rooms

> **One-line summary.** Collaborate on combined datasets across companies without sharing the underlying data. Each party keeps their data in their own S3 / Glue Catalog; pre-approved SQL or ML jobs run against the join, returning only aggregate / differentially-private outputs.

## TL;DR

- The right service for cross-company data collaboration where each side wants to learn from combined data without anyone seeing the raw records (advertising attribution, fraud-pattern sharing, healthcare research).
- **Analysis rules** constrain what queries can run: only specific aggregations, only over allowed columns, with **differential privacy** budgets, **k-anonymity** thresholds, or **cryptographic computing** (encrypted joins where neither side decrypts the other's data).
- **Clean Rooms ML** lets multiple parties train lookalike models on combined first-party data without sharing it.
- Right for marketing measurement, supply-chain risk sharing, healthcare cohort analysis, and similar regulated cross-org analytics.
- Less essential for single-organization analytics — Lake Formation handles internal data governance.

## When to use it

- Advertisers + publishers measuring campaign attribution on overlapping audiences without sharing audience PII.
- Healthcare research consortia analyzing combined patient cohorts without breaking HIPAA boundaries.
- Financial fraud-pattern sharing across institutions.
- Supply-chain risk analysis across partners.
- Lookalike modeling across first-party datasets (Clean Rooms ML).

## When NOT to use it

- Single-organization data sharing — **Lake Formation** is the right tool.
- Workloads where the parties can simply exchange aggregated data — Clean Rooms adds value when the join itself must remain private.
- Tiny one-off collaborations — the setup cost (collaboration agreements, analysis rules, configured tables) only amortizes for ongoing projects.

## Key concepts

**Collaboration.** Multi-party agreement. Each party joins, contributes tables, and is bound by analysis rules.

**Members.** Each AWS account participating. **Query runner** member runs queries; other members contribute data; the **result receiver** member receives the output.

**Configured tables.** Each party registers their tables (Glue Catalog tables backed by S3) with permitted columns and join keys. The configured table is the "what we are willing to expose, and how."

**Analysis rules.** Constrain what queries can run. Three rule types:

- **Aggregation analysis rule** — only `SUM`, `COUNT`, `AVG`, etc.; minimum-group-size threshold (no group with fewer than N rows can be returned).
- **List analysis rule** — return raw rows that match a join; useful for "show me users who overlap" — but each side controls which columns appear in the output.
- **Custom analysis rule** — bring your own Cedar-style policy template for queries.

**Differential privacy.** Add calibrated noise to query results so individual records can't be reverse-engineered. Set a privacy budget (epsilon); each query consumes from the budget.

**Cryptographic computing (Clean Rooms with C3R).** Encrypt data client-side; queries run on encrypted data; only authorized computations decrypt the result. The strongest privacy mode — neither party's raw data is ever in plaintext on the other's side.

**Clean Rooms ML.** Train a lookalike model on the joined dataset without sharing it. Train on Party A's seed audience + Party B's broader audience; result is a model A can score with.

**Outputs.** Query results land in the result-receiver's S3 bucket; AWS enforces that outputs satisfy the analysis rules.

## Pricing model

- **Per-query** pricing for Clean Rooms queries, by data scanned (similar shape to Athena).
- **Cryptographic Computing** adds a per-GB processed fee.
- **Clean Rooms ML** has its own per-training and per-scoring fees.
- **Underlying S3 / Glue** storage and catalog charged normally.
- **No platform monthly fee** for the collaboration itself.

## Quotas & limits

- **Collaborations per account**: configurable; high.
- **Members per collaboration**: up to 5 in many cases (check current docs).
- **Tables per member per collaboration**: bounded.
- **Differential privacy budget**: per-collaboration epsilon allocation.

## Common pitfalls

- **Analysis rules too loose.** A configured table that exposes too many columns or allows row-level joins leaks more than intended. Default-deny; expose only the columns and aggregations needed.
- **No differential-privacy budget tracking.** Each query consumes epsilon; budgets exhaust silently if not monitored.
- **Cryptographic computing as default.** It's the strongest mode but adds latency and cost; reserve for the use cases that genuinely require it.
- **Misaligned data.** Schemas / join keys / formats across parties have to match (or use a deterministic hash). Surprising results from mismatched join keys are the most common debugging time-sink.
- **Skipping the legal agreement.** Clean Rooms is a technical primitive; the data-use agreement between parties is a separate legal concern. Don't deploy without one.
- **Result-receiver assumes raw access.** The receiver gets only the query output — not the underlying data. Set expectations.
- **Treating it as ETL.** Clean Rooms is for **collaboration**, not bulk data movement.

## Pairs well with

- [Glue](glue.md) — Data Catalog for the configured tables.
- [S3](../storage/s3.md) — underlying storage on each side.
- [Lake Formation](lake-formation.md) — per-side governance of the source data.
- **AWS Marketplace** — some collaborations include data subscription models.
- [SageMaker](../ml-ai/) (forthcoming) — Clean Rooms ML modeling.

## Pairs well with these repo pages

- [Lake Formation](lake-formation.md), [Data Exchange](data-exchange.md).

## Further reading

- [AWS Clean Rooms documentation](https://docs.aws.amazon.com/clean-rooms/).
- [Analysis rules](https://docs.aws.amazon.com/clean-rooms/latest/userguide/analysis-rules.html).
- [Differential privacy in Clean Rooms](https://docs.aws.amazon.com/clean-rooms/latest/userguide/differential-privacy.html).
- [Cryptographic computing (C3R)](https://docs.aws.amazon.com/clean-rooms/latest/userguide/crypto-computing.html).
- [Clean Rooms ML](https://docs.aws.amazon.com/clean-rooms/latest/userguide/ml.html).
