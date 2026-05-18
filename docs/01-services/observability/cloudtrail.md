# CloudTrail

> **One-line summary.** Records every AWS API call. The audit log for "who did what, when, from where" — the foundation for security incident response, compliance reporting, and access analysis.

## TL;DR
- Captures every authenticated AWS API call (management events) and, optionally, **data events** (S3 object access, Lambda invocations, DynamoDB item-level access).
- **Always on by default** for management events (90-day Event History in the console). For longer retention, durable storage, multi-account aggregation, or data events → create a **trail** (delivers to S3) or an **event data store** (delivers to **CloudTrail Lake**, queryable with SQL).
- **CloudTrail Lake** is the modern query layer — SQL over historical events without separate ETL.
- **Insights events** auto-flag anomalous API call rates.
- Mandatory baseline: org-wide trail → central log archive account, with S3 Object Lock for immutability. This is the canonical answer to "show me what happened during this incident."

## When to use it
- Always on, always logged. The question is "to where, for how long, and with which events."
- Security incident response — "who made this API call?"
- Compliance / audit — proving access patterns over time.
- Detecting anomalous API behavior (Insights).
- Forensics over data-event-level access (S3 GetObject, DynamoDB item access).

## When NOT to use it
- Application-level logs — CloudTrail is *AWS API* logs, not your app logs.
- Real-time blocking of API calls — CloudTrail is a record, not a gate (use **SCPs**, **IAM**, **Config rules** for prevention; CloudTrail for detection).

## Key concepts

### Event types
- **Management events** — control-plane API calls (CreateBucket, RunInstances, AssumeRole, PutObject metadata APIs).
- **Data events** — data-plane API calls (S3 GetObject / PutObject, Lambda Invoke, DynamoDB GetItem / PutItem, EBS Direct API access). Disabled by default (high volume); opt in per resource.
- **Insights events** — auto-generated anomaly alerts on unusual API call rates.
- **Network activity events** — newer event class for VPC-level activity.

### Event History (free)
The last 90 days of management events in the AWS console. Free, on by default. Limited filtering; not durable beyond 90 days.

### Trails
Persistent capture of events to S3.
- **Single-account, single-Region** — original mode.
- **Multi-Region** — captures events from all Regions.
- **Organization trail** — capture across an AWS Organization; the canonical setup.
- **Delivery** to S3 + optional CloudWatch Logs.
- **SNS notification** when log files arrive.

### CloudTrail Lake (event data stores)
- SQL queryable store of CloudTrail events.
- **Retention up to 10 years**.
- Queries over billions of events; pay per data scanned.
- Optional **Federation** — query other AWS log sources alongside CloudTrail.

### Multi-account aggregation
Org trail in the management account delivers all member-account events to a central S3 bucket (typically in the **log archive account** of the AWS Organizations baseline). Lock the bucket with **S3 Object Lock** for immutability.

### CloudTrail Insights
Statistical anomaly detection on API call rates — flags unusual spikes / drops. Useful for noticing "suddenly 1000× RunInstances in 5 minutes" = potential crypto-mining incident.

### Integrations
- **EventBridge** — every CloudTrail event becomes an EventBridge event in the default bus. Use it to alert / auto-remediate on specific API calls.
- **CloudWatch Logs subscription** for real-time forwarding to Lambda / Firehose / OpenSearch.
- **Athena** — query CloudTrail logs in S3 via SQL (or use CloudTrail Lake natively).

### Log file integrity validation
Optional SHA-256 digest signing of log files; you can verify post-hoc that logs haven't been tampered with.

## Pricing model

- **Event History** (90 days, management events): **free**.
- **Trails** — first copy of management events to S3 is **free** (per trail). Additional copies of management events: per 100K events. **Data events**: per 100K events (significant at high volume).
- **CloudTrail Lake** — per GB ingested + per GB scanned in queries.
- **Insights** — per 100K analyzed events.
- **S3 / CloudWatch Logs / KMS** at standard rates for delivery destinations.

The cost drivers are **data events** (S3 object access can be billions of events) and **CloudTrail Lake** scans. Filter aggressively; only enable data events for resources you genuinely need to audit.

## Quotas & limits

- **Trails per Region per account**: 5.
- **Event data stores per account per Region**: 10 default.
- **Log file delivery latency**: ~15 minutes typical.
- **Insights detection lag**: hours typical.
- **CloudTrail Lake retention**: up to 10 years.

## Common pitfalls

- **CloudTrail off in some Region.** Attackers create resources in unused Regions to fly under the radar. Use multi-Region or organization trails.
- **Log archive account not separated.** Logs in the same account as the workload can be deleted by a compromised admin. Use the log archive account pattern with cross-account trail delivery + Object Lock.
- **Data events on every S3 bucket.** Massive bill. Enable only for sensitive buckets.
- **No EventBridge rules on key events.** "Anyone disabled CloudTrail" / "anyone created an IAM user" should page someone. Wire EventBridge.
- **Insights ignored.** They're cheap; review periodically.
- **Trail bucket without Object Lock.** A compromised account can delete its own logs. Object Lock (Compliance mode) prevents this.
- **Querying CloudTrail via Athena from S3 instead of CloudTrail Lake.** Lake handles the parsing / partitioning; rolling your own Athena setup is more work.
- **Log-file-integrity validation off.** Without it, you can't prove logs weren't tampered with after the fact.

## Pairs well with
- [GuardDuty](../security-identity/guardduty.md), [Detective](../security-identity/detective.md), [Security Hub CSPM](../security-identity/security-hub.md) — all consume CloudTrail.
- [S3](../storage/s3.md) — trail destination.
- [Athena](../analytics/athena.md), **CloudTrail Lake** — query historical events.
- [EventBridge](../integration-messaging/eventbridge.md) — real-time event routing.
- [Organizations](organizations.md) — org-wide trail setup.
- [KMS](../security-identity/kms.md) — encryption for log files.

## Pairs well with these repo pages
- [GuardDuty](../security-identity/guardduty.md), [Detective](../security-identity/detective.md), [Organizations](organizations.md).
- [Security pillar](../../05-well-architected/security.md).
- `docs/04-reference-architectures/multi-account-organization.md` (forthcoming).

## Further reading
- [AWS CloudTrail documentation](https://docs.aws.amazon.com/cloudtrail/).
- [CloudTrail Lake](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-lake.html).
- [Organization trails](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/creating-trail-organization.html).
- [CloudTrail Insights](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/logging-insights-events-with-cloudtrail.html).
- [Log file integrity validation](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-validation-intro.html).
