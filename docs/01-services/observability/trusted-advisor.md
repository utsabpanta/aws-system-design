# Trusted Advisor

> **One-line summary.** AWS-published best-practice checks across cost, performance, security, fault tolerance, service limits, and operational excellence. Free checks for everyone; the full check library for **Business** / **Enterprise** Support plans.

## TL;DR

- The "free advisor that catches the obvious" — public buckets, idle resources, missing MFA on root, unused security-group rules, EBS unattached volumes, low RI utilization.
- **Free tier** is small but valuable; **Business / Enterprise Support** unlocks the full library (hundreds of checks).
- **Trusted Advisor Priority** (Enterprise Support only) gives a curated, prioritized recommendation list with a customer team behind it.
- **Trusted Advisor Engine API** lets you pull check results programmatically and integrate into your own dashboards / Security Hub.
- Less commonly used in 2026 because **Security Hub CSPM**, **Cost Explorer Recommendations**, **Compute Optimizer**, and **AWS Config Conformance Packs** cover overlapping territory — but Trusted Advisor remains a free pulse check.

## When to use it

- Everyone — turn it on, look at the free checks at least quarterly.
- Business / Enterprise Support subscribers — make Trusted Advisor part of monthly ops reviews.
- Cost optimization sweeps — Trusted Advisor flags idle / underused resources for free.
- Pre-audit hygiene checks.

## When NOT to use it

- As the only source of security / cost / reliability hygiene — Trusted Advisor's check set is narrower than dedicated tools (Security Hub, Cost Explorer Recommendations, Compute Optimizer, Config Conformance Packs).
- Real-time alerting — Trusted Advisor refreshes on a schedule (hours to days); not for incident detection.

## Key concepts

### Categories

- **Cost optimization** — idle load balancers, underutilized EC2, low RI utilization, unattached EBS, idle RDS, S3 incomplete multipart uploads.
- **Performance** — high CPU instances, EBS optimization, content delivery (CloudFront).
- **Security** — security group with open ports, IAM password policy, MFA on root, S3 bucket permissions, CloudTrail logging.
- **Fault tolerance** — Multi-AZ status of RDS, ELB health checks, EBS snapshots age.
- **Service limits** — quota utilization across many services.
- **Operational excellence** — Newer category covering operational best practices.

### Free vs paid checks

- **Basic / Developer Support**: a small fixed set (security-focused mostly).
- **Business / Enterprise Support**: hundreds of checks across all categories.

### Trusted Advisor Priority (Enterprise Support)

- AWS-curated prioritized recommendation list.
- AWS technical account managers (TAMs) review and prioritize for your account.
- Status tracking (acknowledged, dismissed, resolved).

### Trusted Advisor Engine API

- Programmatic access to check results.
- Integrate into your own dashboards / Security Hub feeds / EventBridge automation.

### Notifications

- **EventBridge events** on check state changes — wire to Slack / SNS for "new finding" alerts.
- **Weekly summary email** to Billing / Operations / Security / Fault Tolerance contacts (configured in account settings).

### Organizational view

- **Organization-level Trusted Advisor** (Enterprise Support) aggregates findings across an AWS Organization.

## Pricing model

- **Trusted Advisor itself is free** — your bill is determined by the **AWS Support plan tier** (Basic / Developer / Business / Enterprise / Enterprise On-Ramp).
- **Trusted Advisor Priority** requires Enterprise Support.

## Quotas & limits

- **Check refresh cadence** — automatic refresh varies (some daily, some weekly); on-demand refresh limited per check.
- **Finding retention** — perpetual; resolved findings stay in history.
- **Org-level aggregation** — bounded by AWS Organizations account count; check current docs.

## Common pitfalls

- **Free tier checks ignored.** Even the small free set surfaces real issues. Look at them.
- **Trusted Advisor not in any review meeting.** Free findings stay unactioned. Add a 15-minute monthly review.
- **No EventBridge routing.** New findings go unnoticed. Send to Slack / SNS.
- **Trusted Advisor as the only security tool.** Use it alongside Security Hub CSPM, GuardDuty, Inspector — they're complementary.
- **Service-limit findings ignored until they bite.** "You're at 80% of your Lambda concurrency quota" is a chance to raise it before the throttle. Act on these.
- **Org-level aggregation off in multi-account orgs.** Per-account-only view is a lot more clicks for the same picture.

## Pairs well with

- [Security Hub CSPM](../security-identity/security-hub.md) — broader continuous compliance.
- [Compute Optimizer](../compute/ec2.md) — right-sizing recommendations.
- **AWS Cost Explorer Recommendations** — Savings Plans / RI suggestions.
- [AWS Config](../security-identity/config.md) — continuous compliance via custom rules.
- [EventBridge](../integration-messaging/eventbridge.md) — automation hooks on Trusted Advisor events.

## Pairs well with these repo pages

- [Security Hub CSPM](../security-identity/security-hub.md), [AWS Health](health.md), [Config](../security-identity/config.md).
- [Cost Optimization pillar](../../05-well-architected/cost-optimization.md).

## Further reading

- [AWS Trusted Advisor documentation](https://docs.aws.amazon.com/awssupport/latest/user/trusted-advisor.html).
- [Trusted Advisor Engine API](https://docs.aws.amazon.com/awssupport/latest/user/get-started-with-aws-trusted-advisor-api.html).
- [Trusted Advisor Priority](https://docs.aws.amazon.com/awssupport/latest/user/trusted-advisor-priority.html).
- [AWS Support plans](https://aws.amazon.com/premiumsupport/plans/).
