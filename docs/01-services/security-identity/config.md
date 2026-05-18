# Config

> **One-line summary.** Continuously evaluates the configuration of every AWS resource against rules, tracks state changes over time, and (optionally) auto-remediates drift.

## TL;DR
- Tracks the *configuration history* of every resource in your account — when an S3 bucket policy changed, when a security group rule was added, when a Lambda runtime version was updated.
- **Config rules** evaluate resources against desired state ("S3 buckets must not be public," "EBS volumes must be encrypted," "RDS must be in private subnets"). Pre-built **AWS-managed rules** cover most baselines; custom rules via Lambda.
- **Conformance packs** bundle rules + remediations against compliance frameworks (PCI, HIPAA, FedRAMP, CIS, NIST).
- **Auto-remediation** via SSM Automation documents — non-compliant resource detected → SSM doc fires → resource fixed (within seconds-to-minutes).
- The cost is **per-config-item recorded + per-rule evaluation**; a chatty account with many recorded resources can run up real bills. Tune what you record.

## When to use it
- Any production AWS account or AWS Organization needing compliance posture monitoring.
- "We must prove our config matched our policy at time T" — Config's history is the answer.
- Auto-remediation of common drift (re-encrypt EBS, block public S3, enforce SG egress).
- Audit Manager and Security Hub CSPM consume Config's evaluations.

## When NOT to use it
- Single tiny account with no compliance need — Trusted Advisor's free checks cover the obvious.
- Account where you really don't want auditable state history (rare; this is usually a sign of an architectural problem).

## Key concepts

**Recorder.** The Config component that captures resource state. One per Region per account. Choose what to record:
- **All resources** (broad, expensive at scale).
- **Specific resource types** (e.g., just S3, EC2, IAM).
- **Global resources** recorded only in the chosen Region (avoid duplication).

**Configuration item (CI).** A snapshot of a resource's state at a point in time. Every change creates a new CI. Stored in S3 (the **delivery channel**) and queryable via Config Aggregator or Advanced Query.

**Config rule.** Evaluates a resource against desired state.
- **AWS-managed rules** — hundreds of pre-built rules (e.g., `s3-bucket-public-write-prohibited`, `rds-storage-encrypted`).
- **Custom rules** — Lambda function that evaluates the resource config and returns COMPLIANT / NON_COMPLIANT.
- **Custom policy rules** — Guard DSL-based rules; no Lambda needed.

Evaluation triggers: **configuration change** (whenever a CI is recorded), **periodic** (every 1/3/6/12/24 hours), or **detective** (on demand).

**Conformance pack.** A YAML bundle of rules + remediations targeting a specific framework (CIS, PCI, HIPAA, NIST). Pre-built packs available from AWS and partners; deploy across the org via the Aggregator.

**Remediation.** Tie a rule to an SSM Automation document. When a resource becomes non-compliant, SSM remediates. Standard pattern: revoke a public bucket policy, enable encryption on an unencrypted EBS, attach a missing logging policy.

**Aggregator.** Multi-account / multi-Region aggregation of CIs and rules into one account. The right pattern in a security account.

**Advanced query.** SQL-like queries over Config history (e.g., "all EC2 instances with port 22 open to 0.0.0.0/0 across the org").

**Integration.** Feeds **Security Hub CSPM**, **Audit Manager**, **CloudWatch Events / EventBridge**.

## Pricing model

- **Per configuration item recorded** (per CI per Region).
- **Per rule evaluation** (per evaluation triggered, per rule, per Region).
- **Advanced queries** — per query.
- **Conformance pack evaluations** — per evaluation (rule-based pricing).
- **Delivery to S3** — standard S3 storage rates.

The big cost driver is **all-resources recording** in an account with many short-lived resources (Auto Scaling churn, ECS task lifecycle). Scope recording to the resource types you actually care about for compliance.

## Quotas & limits

- **Rules per Region**: 1,000.
- **Conformance packs per Region**: 50.
- **Aggregators per account per Region**: 50.
- **Configuration history retention** — driven by S3 lifecycle on the delivery channel bucket.

## Common pitfalls

- **All-resources recording on a busy account.** Bill explodes. Scope to resource types that matter for your compliance posture.
- **No conformance pack.** Hand-curated rule sets drift; conformance packs codify and evolve with the framework. Start with the AWS CIS / AFSBP pack and tune.
- **No remediation.** Detecting "S3 bucket is public" without auto-remediation means it stays public until a human notices. Wire SSM Automation remediations.
- **Aggregator without ownership.** Aggregating findings into a security account that no one looks at = no value.
- **No advanced query into investigations.** When something breaks, "what did this look like before the change?" is exactly what Config answers. Train responders on Advanced Query.
- **Lambda custom rules with high invocation rates.** Each config change can trigger Lambda evaluations; design rules to be cheap or use Custom Policy (Guard) rules where possible.
- **Forgetting Global resources.** Don't record global resources (like IAM) in every Region — duplicate and expensive. Pick one Region.

## Pairs well with
- **Security Hub CSPM** — Config findings flow in.
- **Audit Manager** — pulls Config evidence into audit reports.
- **Systems Manager Automation** — runs remediation actions.
- **AWS Organizations** — multi-account aggregation.
- **EventBridge** — react to compliance events.

## Pairs well with these repo pages
- [Security Hub CSPM](security-hub.md), [Audit Manager](audit-manager.md), [IAM](iam.md).
- [Operational Excellence pillar](../../05-well-architected/operational-excellence.md).

## Further reading
- [AWS Config documentation](https://docs.aws.amazon.com/config/).
- [AWS-managed Config rules](https://docs.aws.amazon.com/config/latest/developerguide/managed-rules-by-aws-config.html).
- [Conformance packs](https://docs.aws.amazon.com/config/latest/developerguide/conformance-packs.html).
- [Custom Policy rules (Guard)](https://docs.aws.amazon.com/config/latest/developerguide/evaluate-config-rules.html#new-rule).
- [Config Aggregators](https://docs.aws.amazon.com/config/latest/developerguide/aggregate-data.html).
