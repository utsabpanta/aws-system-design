# Cost Optimization

> **One-line summary.** Run the system at the lowest sustained price point that meets the other four pillars — and keep watching, because the bill grows on its own.

## TL;DR

- You can't optimize what you can't attribute. Tag every resource with `Owner`, `Service`, `Env` on day one.
- Three line items account for most surprise bills: idle compute, NAT Gateway egress, and inter-AZ data transfer. Audit them first.
- Commit-based discounts (Savings Plans / Reserved Instances) are 30–70% off on-demand for predictable baseline load. The math takes 10 minutes; the savings are real.
- Storage class transitions (S3 Intelligent-Tiering, Glacier) and lifecycle policies are nearly free to set up and save 50–90% on cold data.
- Cost is everyone's job. A FinOps practice with engineering ownership beats a finance team trying to police AWS spend from outside.

## What the pillar is about

Cost Optimization is the pillar that asks "are you paying as little as you can while still meeting your other commitments?" It covers visibility (where does the money go), allocation (whose money is it), expenditure management (commit vs. on-demand), and ongoing review.

The defining property of cloud spend: it grows on its own. Yesterday's launched feature, today's misconfigured instance, tomorrow's untagged dev cluster — all silently add to next month's bill. Cost optimization is a continuous practice, not a quarterly project.

## AWS's five design principles

1. **Implement cloud financial management (FinOps).** A named team or practice that owns cost visibility, forecasting, and optimization. Not finance alone, not engineering alone — both.
2. **Adopt a consumption model.** Pay for what you use, not what you might use. Lift-and-shift workloads on always-on EC2 should evolve toward serverless or auto-scaling.
3. **Measure overall efficiency.** Cost per business metric (cost per user, cost per request, cost per GB ingested). Raw spend is meaningless without that denominator.
4. **Stop spending on undifferentiated heavy lifting.** Managed services are usually cheaper end-to-end than self-managed equivalents once you account for engineering time, downtime, and ops overhead.
5. **Analyze and attribute expenditure.** Tags, accounts, cost categories. The only way to make optimization decisions is per-team and per-product cost data.

## Key practices

### Visibility

- **Tagging from day one.** Cost-allocation tags (`Owner`, `Service`, `Env`, `CostCenter`) on every resource. Enforce via Tag Policies in AWS Organizations.
- **Cost Explorer + Cost and Usage Reports (CUR).** CUR is the raw data (delivered to S3, queryable in Athena). Cost Explorer is the dashboard most teams live in.
- **AWS Budgets** for forecasted spend, **Cost Anomaly Detection** for unexpected spikes. Both should be wired before anything ships to production.
- **Per-account separation.** Production, staging, sandbox in separate accounts. Cost-by-account is the lowest-effort, highest-fidelity cost view.

### Compute

- **Right-sizing.** Compute Optimizer surfaces over-provisioned EC2, RDS, Lambda. Most workloads use 30–50% of provisioned capacity; that's pure overspend.
- **Savings Plans / Reserved Instances.**
  - **Compute Savings Plans** — most flexible, ~66% off, apply across EC2, Fargate, Lambda regardless of family/Region.
  - **EC2 Instance Savings Plans** — ~72% off, locked to instance family and Region.
  - **Reserved Instances** — older mechanism, similar discounts, less flexible.
  - Rule of thumb: cover 70–80% of your baseline with 1-year SPs; leave the rest on-demand to absorb growth.
- **Spot.** Up to 90% off for fault-tolerant workloads. Spot Fleet across multiple instance types and AZs maximizes availability.
- **Auto Scaling.** Don't pay for idle. Scheduled scaling for predictable patterns (lower at night), target-tracking for variable load.
- **Graviton.** ~20% better price/performance vs x86. Free money if your workload rebuilds for ARM.

### Storage

- **S3 storage classes.** Lifecycle objects from Standard → Standard-IA (30+ days) → Glacier Instant Retrieval (90+ days) → Glacier Deep Archive (180+ days). Or use **Intelligent-Tiering** to let S3 handle it automatically.
- **EBS gp3 over gp2.** Cheaper *and* faster. Migration is a one-command change.
- **Delete what you don't need.** Old snapshots, unattached volumes, abandoned dev resources. Trusted Advisor has free checks for the obvious cases.
- **S3 Storage Lens** for organization-wide S3 visibility. The big offenders are usually old logs, dev backups, and orphaned multipart uploads.

### Data transfer

- The most common bill surprises:
  - **NAT Gateway** charges per hour ($30+/month/AZ) and per GB processed. Audit egress patterns; use VPC Endpoints for AWS services to bypass NAT.
  - **Inter-AZ traffic** — every cross-AZ packet has a per-GB charge in both directions. Microservices chatter across AZs can add up surprisingly fast. Co-locate chatty services or use Local Zone topology if it matters.
  - **Inter-Region traffic** is more expensive again. Multi-Region designs need to budget for replication bandwidth.
  - **Egress to the internet** is the most expensive. CloudFront reduces it (cheaper egress through CloudFront than direct from origin) and serves a cache at the edge.
- **VPC Endpoints** (Gateway for S3/DynamoDB are free; Interface endpoints have a per-hour + per-GB cost that's still usually cheaper than NAT egress).

### Databases

- **Right-size and right-engine.** A `db.r6g.xlarge` running at 10% CPU is overspend. Aurora Serverless v2 scales capacity per ACU (Aurora Capacity Unit) and is ideal for spiky workloads.
- **Reserved Capacity** for predictable databases (RDS, DynamoDB, OpenSearch). DynamoDB provisioned-with-auto-scaling-and-RIs is much cheaper than on-demand for steady traffic.
- **Read replicas vs caching.** A read replica costs as much as a primary; a Redis cache that handles 90% of reads is typically much cheaper.
- **DynamoDB on-demand for spiky / unknown traffic, provisioned for steady.** On-demand is roughly 7× more expensive per request than provisioned at the same utilization.
- **Aurora I/O-optimized** if you have very I/O-heavy workloads (large analytical scans, high-write OLTP) — flat per-instance pricing instead of per-I/O.

### Serverless

- **Lambda is cheap, until it's not.** Sub-millisecond compute is amazing; 10-second functions hammered at high RPS are surprisingly expensive. Compare to Fargate or EC2 above ~1M invocations/day on long-running functions.
- **Lambda right-sizing.** Memory and CPU are coupled — sometimes 2× memory makes the function 3× faster and net-cheaper. Use the AWS Lambda Power Tuning tool.
- **API Gateway HTTP APIs** vs REST APIs. HTTP APIs are ~70% cheaper and faster; use REST only when you need the features it has that HTTP API doesn't (per-method WAF, request transformations, API keys/usage plans).

## AWS services that support this pillar

- **AWS Cost Explorer, Cost and Usage Reports (CUR)** — visibility.
- **AWS Budgets, Cost Anomaly Detection** — alerts.
- **Compute Optimizer** — right-sizing recommendations.
- **Trusted Advisor** — free checks for the obvious wins.
- **Savings Plans, Reserved Instances** — commit-based discounts.
- **S3 Intelligent-Tiering, Storage Lens** — storage optimization.
- **Resource Groups + Tag Editor, AWS Organizations Tag Policies** — tag enforcement.
- **AWS Pricing Calculator** — forecasting before you build.
- **AWS Application Cost Profiler** — per-tenant cost attribution for SaaS.

## Common anti-patterns

- **Untagged resources.** You can't blame what you can't identify. Block resource creation without required tags via Service Control Policies.
- **All on-demand forever.** Six months of steady production load with no Savings Plans coverage is leaving 30–70% on the table.
- **Set-and-forget instance types.** AWS launches a new, cheaper, faster instance family every year. Re-evaluate at least annually.
- **NAT Gateway as default routing for every private subnet.** Use VPC Endpoints for AWS services; sometimes the NAT can be removed entirely.
- **Cross-AZ chatter for stateless services.** A service mesh routing every request randomly across AZs incurs data transfer costs for no benefit. Use availability zone affinity where the chatter is hot.
- **Test/dev resources running 24/7.** Schedule them off nights and weekends — saves ~75% with one Lambda + EventBridge schedule.
- **Treating cost as finance's problem.** The team that can fix the cost is the team that can see the cost. FinOps requires engineering ownership.
- **Orphaned resources.** Unattached EBS volumes, old snapshots, idle load balancers, abandoned NAT Gateways. Trusted Advisor surfaces these for free.

## Pairs well with

- [Performance Efficiency](performance-efficiency.md) — same tools, often the same optimizations.
- [Operational Excellence](operational-excellence.md) — cost dashboards live alongside performance dashboards in the operations function.
- [Sustainability](sustainability.md) — efficient compute is also greener compute.
- `docs/04-reference-architectures/cost-optimization-patterns.md`.

## Further reading

- AWS Well-Architected Framework — Cost Optimization pillar whitepaper.
- [FinOps Framework](https://www.finops.org/) (FinOps Foundation).
- *Cloud FinOps* (J.R. Storment, Mike Fuller).
- AWS re:Invent talks: "Optimize your AWS costs", annual session — usually the densest hour of practical cost wins each year.
- AWS Pricing Calculator and Compute Optimizer documentation.
