# Detective

> **One-line summary.** Managed security investigation service. Builds an entity graph from CloudTrail, VPC Flow Logs, EKS audit logs, GuardDuty findings, and Security Hub data — and lets you click through to see who did what when.

## TL;DR

- The "investigation" side of AWS security tooling. **GuardDuty / Inspector / Macie** detect; Detective explains.
- Auto-ingests **GuardDuty findings** (one-click pivot from a finding to the entity graph) and **CloudTrail / VPC Flow Logs / EKS audit logs / Security Hub findings**.
- Pre-built **finding profiles** and **entity profiles** show timelines, related findings, related entities, and unusual behavior compared to baseline.
- Right for security teams who actually investigate findings; less essential if your model is "ship findings to a SIEM and investigate there."
- Pricing scales with the volume of data ingested; budget for it deliberately on high-volume accounts.

## When to use it

- Security teams investigating GuardDuty or Security Hub findings.
- Forensics during or after an incident — Detective's graph dramatically reduces investigation time vs raw CloudTrail queries.
- Multi-account environments where the investigation has to span accounts (Detective aggregates from member accounts).
- EKS clusters where audit-log forensics matter.

## When NOT to use it

- Workloads with no security-investigation function (no one to do the work the graph enables).
- Environments where a SIEM (Splunk / Datadog / Elastic) already does the investigation workflow well — Detective duplicates some of that value.
- Very small AWS footprints — manual CloudTrail queries are fine at low scale.

## Key concepts

### Behavior graph

Detective continuously builds an **entity graph** from ingested data sources. Nodes are entities (IAM users, roles, IP addresses, EC2 instances, S3 buckets, EKS pods, federated users, etc.); edges are relationships (this principal called this API on this resource at this time).

### Data sources

- **AWS CloudTrail management events** — every API call.
- **VPC Flow Logs** — network flows.
- **GuardDuty findings** — auto-ingested; pivot from finding to graph.
- **Security Hub findings** — broader security findings.
- **EKS audit logs** — Kubernetes API activity.

Detective does the ingestion automatically when the source service is enabled in the account.

### Pivots

The killer feature: starting from a GuardDuty finding, you can pivot to:

- The principal that triggered it (recent activity timeline, related findings).
- The target resource (who else accessed it recently?).
- The IP address (other principals from this IP, geolocation, ASN).
- The user agent / SDK version.

### Finding groups

Detective clusters related findings into a **finding group** — multiple GuardDuty alerts that share an entity (e.g., the same compromised IAM user) become one investigative thread.

### Multi-account

Enable as a delegated admin from a security account; member accounts' data ingests into the central behavior graph. Investigators see the whole org.

### Retention

Detective retains data for up to 1 year by default; configurable shorter retention to manage cost.

## Pricing model

- **Per GB of source data ingested per month**, with separate dimensions for CloudTrail, VPC Flow Logs, GuardDuty, EKS audit logs, Security Hub findings.
- Volume-tiered (cheaper per GB at higher volumes).
- No per-investigation fee; the cost is the ingestion / graph maintenance.

On a busy production account with lots of CloudTrail and VPC Flow Log volume, Detective is a real line item — budget intentionally.

## Quotas & limits

- **Behavior graph members per delegated admin**: 1,200.
- **Data sources**: enable / disable per source per account.
- **Retention**: up to 1 year.

## Common pitfalls

- **Detective without GuardDuty.** GuardDuty is the primary source of high-value findings to investigate. Use them together.
- **No team trained on Detective.** The tool is only useful if someone uses it. Train responders on the investigation workflow; mock-drill during game days.
- **All data sources on in every account, all year.** Cost-tunable. For low-risk accounts, shorter retention or selective data sources is reasonable.
- **Detective as an alternative to a SIEM.** It complements; it doesn't replace. Many orgs run both — Detective for AWS-centric investigations, SIEM for cross-cloud / app / endpoint correlation.
- **Ignoring finding groups.** Multiple findings on the same entity are usually one incident. Investigate the group, not each finding in isolation.
- **No runbook from finding type to Detective pivot.** Document the investigation pattern for each common GuardDuty finding type — when an IAM credential exfiltration alert fires, the investigator should know exactly which Detective views to open.

## Pairs well with

- [GuardDuty](guardduty.md) — primary finding source.
- [Security Hub CSPM](security-hub.md) — broader finding feed.
- [CloudTrail](../observability/cloudtrail.md) (forthcoming) — the underlying audit log.
- **AWS Organizations** — multi-account behavior graph.
- **SIEM / SOAR** — Detective enriches; SIEM aggregates and automates.

## Pairs well with these repo pages

- [GuardDuty](guardduty.md), [Security Hub CSPM](security-hub.md).
- [Security pillar](../../05-well-architected/security.md).

## Further reading

- [Amazon Detective documentation](https://docs.aws.amazon.com/detective/).
- [Detective + GuardDuty integration](https://docs.aws.amazon.com/guardduty/latest/ug/detective-integration.html).
- [Detective behavior graph](https://docs.aws.amazon.com/detective/latest/userguide/graph-data-about.html).
- [Detective best practices](https://aws.github.io/aws-security-services-best-practices/guides/detective/).
