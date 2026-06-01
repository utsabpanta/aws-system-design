# AWS Health

> **One-line summary.** Personalized view of AWS service events affecting *your* account — outages, scheduled maintenance, account-specific notifications (security, EOL announcements, certificate expirations).

## TL;DR

- The personalized version of [status.aws.amazon.com](https://status.aws.amazon.com/). Where AWS tells *you* about things that affect *your* resources.
- Three categories of events:
  - **Public events** — broad AWS service issues / Region-wide degradations.
  - **Account-specific events** — your scheduled instance maintenance, security notifications, billing events, EOL warnings.
  - **Org-level events** — aggregated across an AWS Organization (Business / Enterprise Support).
- **AWS Health Dashboard** is the console UI; **Health API** is the programmatic surface; **EventBridge integration** fires events for downstream automation.
- For multi-account orgs, **Organizational view** aggregates events to the management account / delegated admin — the right place to wire automation.

## When to use it

- Any AWS account — everyone has access to the Health Dashboard.
- Multi-account orgs — enable Organizational view to centralize.
- Wire **EventBridge** rules to notify on-call when AWS events affect your services.
- Automate responses to scheduled maintenance (drain a node before a scheduled instance reboot).
- Track AWS-published end-of-life announcements for services you use.

## When NOT to use it

- Not really — Health is free. Everyone should at least have notifications on.

## Key concepts

### Event types

- **Issue** — ongoing degradation / outage (e.g., "EC2 API errors in us-east-1").
- **Scheduled change** — planned maintenance with a window (e.g., "your instance i-123 will be retired on date X").
- **Account notification** — billing alerts, security notices, certificate expirations, EOL announcements for services you use, deprecation warnings.

### Affected resources

For account-specific events, Health lists the specific resources (instance IDs, RDS clusters, etc.) affected. For public events, the resource list may be empty.

### Severity

- **Critical** — service interrupting / data-affecting.
- **Important** — meaningful but not interrupting.
- **Informational** — heads-up, no immediate action.

### AWS Health Dashboard (console)

- **Open issues** — current events.
- **Scheduled changes** — upcoming maintenance.
- **Other notifications** — informational.
- **Event log** — historical events.

### AWS Health API

- `DescribeEvents`, `DescribeEventDetails`, `DescribeAffectedEntities`.
- Available to Business / Enterprise Support plans.
- Org-level API for the delegated admin / management account.

### EventBridge integration

- Every Health event emitted to EventBridge as `aws.health` source.
- Filter by service / Region / event-type-code / event-type-category.
- Route to Lambda, SNS, Slack, ticketing — the canonical "AWS told us something; alert someone" automation.

### Organizational view

- Enable in the management account; events from all member accounts aggregate.
- Required for Enterprise Support's "AWS event impact across our entire portfolio" view.

### Personal Health Dashboard

The older name for AWS Health; same service.

## Pricing model

- **AWS Health is free.**
- **API access requires Business / Enterprise Support** plan.
- **Event delivery via EventBridge is free**; downstream consumers (Lambda, etc.) billed normally.

## Quotas & limits

- **Event retention**: 90 days for active events; older events archive.
- **API rate**: Health API is rate-limited; bulk pulls should paginate.
- **EventBridge integration**: native; no setup beyond enabling a rule.

## Common pitfalls

- **No EventBridge rules.** Critical events get noticed only when someone checks the dashboard. Wire to Slack / on-call paging at minimum.
- **No Organizational view in multi-account.** Each account team has to monitor independently.
- **Ignoring "informational" notifications.** EOL announcements, deprecation notices, certificate expiry warnings — informational severity, real impact. Triage them.
- **Treating Health as the only source of truth for AWS status.** Cross-check with [the public status page](https://status.aws.amazon.com/) and your own metrics during incidents — Health can lag.
- **No automation for scheduled instance retirements.** AWS announces upcoming instance retirements via Health; without automation to gracefully migrate, you'll find out when the instance reboots.
- **Treating "no event in Health" as proof everything's fine.** Account-specific events are good signal but don't catch everything. Always run your own SLO monitoring.

## Pairs well with

- [EventBridge](../integration-messaging/eventbridge.md) — primary automation hook.
- [CloudWatch](cloudwatch.md) — alarm side of incident response.
- [Trusted Advisor](trusted-advisor.md) — best-practice findings, separate from Health events.
- **AWS Support API** — open a support case from a Health event.
- [Organizations](organizations.md) — org-level Health view.

## Pairs well with these repo pages

- [EventBridge](../integration-messaging/eventbridge.md), [CloudWatch](cloudwatch.md), [Trusted Advisor](trusted-advisor.md), [Organizations](organizations.md).
- [Operational Excellence pillar](../../05-well-architected/operational-excellence.md).

## Further reading

- [AWS Health documentation](https://docs.aws.amazon.com/health/).
- [AWS Health Dashboard](https://docs.aws.amazon.com/health/latest/ug/aws-health-dashboard-status.html).
- [AWS Health API](https://docs.aws.amazon.com/health/latest/APIReference/Welcome.html).
- [EventBridge events for AWS Health](https://docs.aws.amazon.com/health/latest/ug/cloudwatch-events-health.html).
- [Organizational view](https://docs.aws.amazon.com/health/latest/ug/aggregate-events.html).
