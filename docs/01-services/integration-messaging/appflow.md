# AppFlow

> **One-line summary.** Managed SaaS-to-AWS (and AWS-to-SaaS) data transfer service. 50+ pre-built connectors (Salesforce, ServiceNow, Slack, Zendesk, SAP, Marketo, Google Analytics, …) and a custom-connector SDK.

## TL;DR
- The right answer for "we need data from a SaaS into S3 / Redshift / S3 Tables and we don't want to write yet another integration."
- Connector library covers the major enterprise SaaS systems. Custom connector SDK (Java / Python) for what's not in the box.
- **Flows** run on schedule, on demand, or in response to events (e.g., a new opportunity in Salesforce).
- Built-in **data transformations** — merge, mask, filter, validate — without a separate ETL step.
- Integrates with **AWS Glue Data Catalog** for downstream analytics; **PrivateLink** for keeping data off the public internet; KMS for at-rest encryption.

## When to use it
- Pulling SaaS data into a data lake (S3) or warehouse (Redshift) for analytics.
- Syncing a SaaS to / from AWS storage on a schedule (CRM data to Redshift nightly; analytics back to Salesforce custom objects).
- Event-driven SaaS automation (Salesforce opportunity created → S3 + downstream pipeline).
- Replacing brittle custom ETL scripts written against SaaS APIs.

## When NOT to use it
- High-frequency, low-latency event streams from SaaS — AppFlow is batch / scheduled, not real-time pub/sub.
- Workloads needing complex multi-step ETL transformations (joins, aggregations) — use **Glue** or **Step Functions** downstream of AppFlow.
- SaaS without an AppFlow connector and where a custom connector isn't worth the effort — direct API integration may be simpler.

## Key concepts

**Flow.** Configured data movement: source, destination, schedule (or event trigger), field mapping, transformations, filters.

**Connectors.** 50+ pre-built (Salesforce, ServiceNow, Slack, Zendesk, SAP OData, SAP S/4HANA, Marketo, Google Analytics 4, Snowflake, Datadog, etc.). AWS publishes new connectors regularly; partners publish through AWS Marketplace.

**Custom Connector SDK.** Build your own connector for a system not in the catalog. Java and Python; deploys as a Lambda function. Same SDK AWS uses internally for its own connectors.

**Sources and destinations.** AWS-side: S3, Redshift, EventBridge, Lookout for Metrics, S3 Tables. SaaS-side: any supported connector.

**Triggers.**
- **On-demand** — manual or API-invoked.
- **Schedule** — cron-style.
- **Event** — listen to SaaS events (e.g., Salesforce CDC, ServiceNow notifications). Connector-dependent.

**Field mapping.** Source-to-destination column / field mapping; supports renames, type coercion, concatenation.

**Transformations.** Merge fields, mask PII, filter records (drop rows that don't match a predicate), validate values.

**PrivateLink.** Optionally route SaaS-side traffic over PrivateLink endpoints (where supported by the connector) for compliance / data-residency.

**Glue Data Catalog integration.** Automatically register data landing in S3 as Glue tables — instantly queryable with Athena.

**Error handling.** Failed flows retry; persistent failures route to error logs in CloudWatch.

## Pricing model

- **Per-flow-run fee** + **per-GB processed**.
- **Source-side API fees** (some SaaS connectors meter their own calls — your SaaS vendor's bill).
- **Storage at the destination** (S3 / Redshift) at standard rates.
- **PrivateLink** — endpoint hours.

## Quotas & limits

- **Flows per account per Region**: 1,000 default (raisable).
- **Records per flow run**: bounded by source-API limits more than by AppFlow.
- **Concurrent flow runs**: connector-dependent.
- **Filter conditions, mappings per flow**: high; check current docs.

## Common pitfalls

- **AppFlow for real-time streaming.** It's batch / scheduled / event-triggered, not millisecond streaming. For real-time, use webhook + Lambda or EventBridge partner buses.
- **Pulling everything every run.** Most connectors support incremental pulls (CDC, since-last-run timestamps); configure them or you'll repeatedly transfer everything.
- **Ignoring SaaS API rate limits.** Salesforce / ServiceNow / many SaaS have strict API quotas. AppFlow respects rate limits but heavy schedules can still exhaust them — coordinate with other consumers.
- **No Glue Data Catalog integration.** Data lands in S3 unregistered; analytics teams can't find it.
- **Storing SaaS credentials in plain config.** Use Secrets Manager and reference from the connector.
- **No error monitoring.** Flow failures show up only on inspection. Wire CloudWatch alarms / EventBridge rules on flow failure events.
- **Custom connector built before checking the catalog.** AWS ships new connectors regularly; check before investing in a custom one.

## Pairs well with
- [S3](../storage/s3.md) and [Redshift](../database/redshift.md) — common destinations.
- **AWS Glue Data Catalog** — register output for analytics.
- **EventBridge** — chain SaaS data ingest into broader workflows.
- **Secrets Manager** — store connector credentials.
- **PrivateLink** — keep SaaS traffic off the public internet.

## Pairs well with these repo pages
- [S3](../storage/s3.md), [Redshift](../database/redshift.md), [EventBridge](eventbridge.md).
- `docs/04-reference-architectures/data-lake-on-s3.md` (forthcoming).

## Further reading
- [Amazon AppFlow documentation](https://docs.aws.amazon.com/appflow/).
- [Supported connectors](https://aws.amazon.com/appflow/integrations/).
- [AppFlow Custom Connector SDK](https://github.com/awslabs/aws-appflow-custom-connector-java).
- [AppFlow features](https://aws.amazon.com/appflow/features/).
