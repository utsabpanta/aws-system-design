# Resource Explorer

> **One-line summary.** Search across all your AWS resources — Region- and service-spanning queries from one place. "Find every untagged S3 bucket in our 50 accounts" in seconds.

## TL;DR

- Builds an index of resources across an account (or Organization) and lets you query by name, tag, ARN substring, type, or arbitrary keyword.
- **Cross-Region search** without switching console Regions.
- **Multi-account search** via AWS Organizations integration (delegated admin pattern).
- **Free** to use.
- Replaces "log into 12 Regions, click Resource Groups, find nothing" with a fast SQL-style query.

## When to use it

- Anytime you need to find resources across Regions / accounts ("where did we leave that test EC2?").
- Tag governance — "show me every resource without an `Owner` tag."
- Cost / security investigations — "all resources in `us-east-1` of type `ec2:instance` with public IPs."
- Operational reviews — "all RDS clusters across the org."

## When NOT to use it

- Querying resource *configuration* deeply — use **AWS Config Advanced Query** (Config has the configuration history; Resource Explorer just indexes the resources).
- Compliance reporting — Config or Audit Manager is the right tool.
- Real-time inventory — Resource Explorer indexes asynchronously; recent changes lag by minutes.

## Key concepts

### Index types

- **Local index** — per-Region; tracks resources in that Region only.
- **Aggregator index** — per-account; aggregates Local indexes from all Regions in the account into one searchable surface. One per account.

You need a Local index in every Region you want searched, plus a single Aggregator index in your "default search Region."

### Views

A **view** is a saved subset of the index (filter by tags, types, scope) plus IAM-controlled access to that subset.

Multiple views let you give different teams different slices:

- Developer view — only Dev account resources.
- Security view — every resource org-wide with specific tags.
- FinOps view — everything tagged `Service` to enable cost mapping.

### Multi-account search

- Aggregator account designated via **AWS Organizations**.
- All member accounts' indexes aggregate.
- The right place to put Resource Explorer is in a central observability account.

### Query syntax

- Free-text — keyword matches against name, ARN, tag values.
- **Qualified search** — `resourcetype:ec2:instance region:us-east-1 tag:Owner=team-x`.
- Pre-built filters in the console for common attributes.

### IAM scoping

View-level + index-level permissions. Users see only the resources in views they have access to.

### Integration

- **AWS Console search bar** — backed by Resource Explorer when enabled.
- **Resource Explorer API** for programmatic queries.

## Pricing model

- **Free.**

## Quotas & limits

- **Indexes per account per Region**: 1 (Local) + 1 (Aggregator if applicable).
- **Views per index**: 100.
- **Query rate**: bounded but generous.
- **Index update latency**: minutes from resource change to searchable.

## Common pitfalls

- **Resource Explorer not turned on.** It's free; turn it on in every Region of every account where you want fast inventory search.
- **No Aggregator index.** Without it, you can only query the Region you're in. Pick a "default search Region" and create an Aggregator index there.
- **No multi-account aggregation.** In a multi-account org, per-account indexes are still siloed without the Organizations integration.
- **Tag governance not in place.** Resource Explorer is most useful when tags are consistent. If tags are scattered, queries return mush.
- **Treating Resource Explorer as a compliance tool.** It's an inventory search, not a compliance evaluator. Use Config / Security Hub for compliance.
- **Skipping views for team scoping.** Giving every developer the full org index makes for noisy results. Per-team views with IAM scoping.

## Pairs well with

- [Organizations](organizations.md) — multi-account aggregation.
- [Config](../security-identity/config.md) — deeper resource configuration history and compliance.
- **Resource Groups** — group resources by tag for SSM Run Command / Automation targeting.
- [Trusted Advisor](trusted-advisor.md) — best-practice findings.
- [Security Hub CSPM](../security-identity/security-hub.md) — security findings.

## Pairs well with these repo pages

- [Organizations](organizations.md), [Config](../security-identity/config.md), [Trusted Advisor](trusted-advisor.md).
- [Operational Excellence pillar](../../05-well-architected/operational-excellence.md).
- [Cost Optimization pillar](../../05-well-architected/cost-optimization.md) — tag-driven cost attribution depends on consistent tagging.

## Further reading

- [AWS Resource Explorer documentation](https://docs.aws.amazon.com/resource-explorer/).
- [Set up Resource Explorer](https://docs.aws.amazon.com/resource-explorer/latest/userguide/getting-started.html).
- [Multi-account search](https://docs.aws.amazon.com/resource-explorer/latest/userguide/manage-service-multi-account.html).
- [Resource Explorer query syntax](https://docs.aws.amazon.com/resource-explorer/latest/userguide/using-search-query-syntax.html).
