# Data Exchange

> **One-line summary.** AWS-hosted data marketplace and data subscription service. Find, subscribe to, and consume third-party datasets — financial market data, weather, healthcare, demographics — delivered into S3, Redshift, Lake Formation, or queried via APIs.

## TL;DR
- The right service when "we need third-party data X" and you'd otherwise negotiate a contract, set up SFTP, and write ingestion code per provider.
- Providers publish datasets; subscribers find them in the AWS Marketplace and subscribe with one click. AWS handles delivery, payment, and entitlements.
- Four delivery methods: **files (to S3)**, **APIs** (via API Gateway), **Amazon Redshift** datasets, and **Amazon S3-based datasets** (read-only via your own queries).
- Subscriptions are managed entitlements — auto-revoke when the subscription ends, replicated across Regions as configured.
- Right for: market data, alternative data, geospatial, healthcare research datasets, ML training data. Not for: ad-hoc one-off datasets where direct procurement is simpler.

## When to use it
- Subscribing to commercial datasets (Reuters / Refinitiv, Bloomberg-style data, S&P, Nielsen, Foursquare, weather APIs).
- ML training data — labeled datasets distributed via Data Exchange.
- Healthcare research datasets (HIPAA-aligned providers).
- Geospatial / location data (transit, weather, demographics).
- Replacing direct SFTP / API integrations with managed subscriptions.

## When NOT to use it
- Public open data — usually available directly via the provider (CDC, NASA, etc.) at no cost; Data Exchange isn't always the cheapest source.
- Internal data sharing between subsidiaries — Lake Formation cross-account sharing is the better tool.
- One-off ad-hoc datasets that the team will use once — direct procurement / download is simpler.

## Key concepts

**Provider.** Third-party (or AWS Partner) that publishes datasets and product listings in AWS Marketplace.

**Subscriber.** Your AWS account, subscribing to one or more products.

**Product.** A subscription offering — set of datasets, pricing tiers (subscription duration, free trials, BYO contracts).

**Dataset.** A collection of revisions. Files within each revision are delivered to your S3 bucket; metadata makes the latest revision queryable.

**Revisions.** Periodic updates from the provider (daily / weekly / on-event). Subscriber gets all new revisions automatically while subscribed.

### Delivery methods

**Files via S3.**
- The classic mode. Provider publishes file revisions; AWS copies them to your S3 bucket on a schedule or on event.
- Your downstream pipeline (Glue, Athena, Spark) processes from S3.

**Data Exchange APIs (via API Gateway).**
- Provider exposes an API; subscriber calls it with managed credentials.
- Useful for query-style access where the dataset is large or constantly changing.

**Amazon Redshift datasets.**
- Provider's data lives in Redshift; subscriber gets a **data share** (Redshift's cross-account sharing primitive) into their own Redshift cluster.
- Read-only; no data copy.

**Amazon S3-based datasets.**
- Provider's data lives in S3; subscriber gets read-only access via Lake Formation permissions or S3 bucket policy.

### Entitlements
Managed by AWS. When your subscription expires, access is revoked automatically.

### Multi-Region
Configure replication so new revisions are also delivered to multiple Regions.

### Cost integration
Subscriptions billed through AWS Marketplace — appear on your AWS bill alongside other AWS charges.

## Pricing model

- **Provider sets the price** per subscription, per delivery, or per-API-call (depending on product).
- **AWS adds platform fees** for the Marketplace transaction.
- **Underlying AWS services** (S3 storage, API Gateway calls, Redshift compute) charged separately to your account.
- **Free trials** common for many products.

## Quotas & limits

- **Subscriptions per account**: high (hundreds).
- **Datasets per product**: bounded; multi-dataset products supported.
- **Revisions retained**: configurable per dataset.
- **File / API size**: provider-dependent.

## Common pitfalls

- **No expiration handling.** Subscriptions expire; if your downstream pipelines assume the data is always fresh, you'll silently fall behind on the renewal date. Alarm on subscription state.
- **Storage costs on raw revisions.** Provider revisions accumulate in your S3 bucket. Lifecycle-policy older revisions or delete them after processing.
- **One-off dataset purchases with the wrong delivery method.** A subscription-friendly file-based product may not be the right choice for an API-style access pattern.
- **Skipping the comparison vs direct procurement.** Some Data Exchange products have markup vs going direct to the provider; for high-volume use, evaluate both paths.
- **Cross-Region replication forgotten.** Single-Region delivery is fine until the consumer pipeline moves; multi-Region replication is the prevention.
- **No entitlement audit trail.** CloudTrail logs subscription events; route to your central log store.

## Pairs well with
- [S3](../storage/s3.md) — file-based delivery destination.
- [Lake Formation](lake-formation.md) — managing permissions on subscribed S3-based datasets.
- [Redshift](../database/redshift.md) — data-share consumer.
- [API Gateway](../networking/api-gateway.md) — API-based product gateway.
- [Glue](glue.md) — Cataloging subscribed data for downstream analytics.
- **AWS Marketplace** — subscription, billing, entitlement plumbing.

## Pairs well with these repo pages
- [S3](../storage/s3.md), [Glue](glue.md), [Lake Formation](lake-formation.md), [Redshift](../database/redshift.md).

## Further reading
- [AWS Data Exchange documentation](https://docs.aws.amazon.com/data-exchange/).
- [Data Exchange for Amazon Redshift](https://docs.aws.amazon.com/data-exchange/latest/userguide/aws-data-exchange-redshift.html).
- [Data Exchange APIs](https://docs.aws.amazon.com/data-exchange/latest/userguide/apis.html).
- [AWS Marketplace Data Exchange catalog](https://aws.amazon.com/marketplace/search/results?searchTerms=&CATEGORY=Data%20Exchange).
