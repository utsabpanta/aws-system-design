# Route 53

> **One-line summary.** AWS's managed DNS, domain registration, health-check, and traffic-routing service. The control plane for "where on the internet does this name point right now?"

## TL;DR
- Three jobs: **authoritative DNS** (hosted zones), **domain registrar** (.com / .org / .io / etc.), and **health-check-driven traffic policies** (weighted, latency, geolocation, failover routing).
- The DNS service has a **100% availability SLA** — the only AWS service offering that. The control plane lives mainly in `us-east-1`, but the data plane is globally distributed.
- **Routing policies** are the magic: weighted A/B tests, latency-based geographic routing, failover with health checks, geolocation for compliance / localization, multi-value answer for client-side load balancing.
- **Amazon Application Recovery Controller (ARC)** — formerly Route 53 ARC — gives you **zonal shift** for single-AZ failures and **routing controls** for multi-Region failover that's fast, observable, and protected by safety rules.
- **Route 53 Resolver** handles DNS inside VPCs, including conditional forwarding to on-prem AD DNS.

## When to use it
- Always. Authoritative DNS for any domain you operate on AWS, plus the routing policies for HA / latency / canary.
- Domain registration when you want one consolidated AWS bill / IaC for everything.
- Multi-Region active-active or active-passive failover (with health checks).
- Internal DNS in VPCs (Private Hosted Zones).

## When NOT to use it
- Bring-your-own external registrar — fine to keep the registrar elsewhere and point NS records at Route 53 hosted zones. You don't have to use Route 53 for registration just because you use it for DNS.
- Workloads where DNS-based traffic management isn't enough — for true L7 routing, an ALB / API Gateway / CloudFront with routes is the answer.

## Key concepts

**Hosted zone.** A container for DNS records.
- **Public hosted zone** — internet-resolvable; mapped to a domain you registered.
- **Private hosted zone** — VPC-resolvable only; for internal naming inside one or more VPCs.

**Record types.** A, AAAA, CNAME, MX, TXT, SRV, CAA, NS, SOA, PTR, plus **Alias records** (Route 53 only — A/AAAA-style record that targets AWS resources like ALB / CloudFront / S3 / API Gateway and is free of charge, unlike CNAMEs).

**Alias vs CNAME.** Alias records can be set on the zone apex (`example.com → ALB`), which CNAMEs can't. They're also free; CNAMEs incur per-query charges. Default to alias for AWS targets.

**Routing policies:**
- **Simple** — one or more values, returned round-robin.
- **Weighted** — split traffic by weight. The classic A/B and canary primitive.
- **Latency-based** — return the endpoint with lowest measured latency from the resolver's Region.
- **Geolocation** — by continent / country / state. Useful for compliance (data residency) and localization.
- **Geoproximity** — bias toward / away from specific Regions with a "bias" parameter (Route 53 Application Traffic Flow).
- **Failover** — primary / secondary, switched by health check.
- **Multi-value answer** — return up to 8 healthy values; client-side load balancing.

**Health checks.**
- **Endpoint health checks** — Route 53 polls an HTTP(S) / TCP endpoint from many global health checkers.
- **CloudWatch alarm health checks** — health = "alarm is in OK state."
- **Calculated health checks** — combine other health checks (AND / OR / inverse).

Health checks integrate with Failover and other routing policies for automatic DNS-driven failover.

**Amazon Application Recovery Controller (ARC).**
- **Zonal shift** — manually shift traffic away from one AZ (for supported resources like ALB, NLB, EKS) without changing DNS.
- **Zonal autoshift** — AWS detects AZ impairment via internal telemetry and shifts automatically on your behalf.
- **Routing controls** — on/off switches hosted on a highly available Route 53 ARC cluster, with **safety rules** (e.g., "only one Region replica enabled at a time") to prevent split-brain. The right primitive for orchestrated multi-Region failover.
- **Readiness checks** — continuous monitoring of quotas, capacity, and routing configuration to verify the standby Region is actually ready to take traffic.
- **Region switch** — the higher-level orchestration that combines all of the above for a managed planned regional failover experience.

**Route 53 Resolver.** Inside-VPC DNS resolution.
- **Resolver endpoints** for forwarding queries in/out of the VPC.
- **Resolver rules** for conditional forwarding (e.g., `corp.example.com` → on-prem AD DNS).
- **DNS Firewall** for blocking malicious / unwanted domains by category or custom list.

**Route 53 Profiles** — share resolver rules and DNS firewall rules across many VPCs and accounts; simplifies multi-account DNS governance.

**Traffic Flow** — visual policy editor for combining routing policies into a tree (e.g., geolocation → latency → weighted) and reusing the policy across many record sets.

## Pricing model

- **Hosted zones** — per zone per month (first 25 records free; per-record after).
- **Queries** — per million; standard queries are cheap; latency-based / geolocation-based queries cost slightly more.
- **Health checks** — per health check per month + extra for HTTPS / string match / fast interval.
- **ARC** — per cluster-hour for routing-control clusters, plus per check.
- **Domain registration** — annual fee, varies by TLD.
- **Resolver endpoints / DNS Firewall** — per endpoint-hour + per-query.

Route 53 is one of the rare AWS services where bills stay small for almost everyone; the only real cost driver is **lots of zones × lots of queries**, which is a high-traffic public-DNS situation.

## Quotas & limits

- **Hosted zones per account**: 500 default (raisable).
- **Record sets per hosted zone**: 10,000 default (raisable).
- **Health checks per account**: 200 (raisable).
- **Domains registered per account**: 20.
- **Resolver rules per account per Region**: 100.
- **Resolver endpoints per Region**: 10.

## Common pitfalls

- **CNAME at the zone apex.** Standard DNS doesn't allow CNAMEs at the apex; use Route 53 **Alias** for `example.com → ALB`.
- **Health checks that lie.** "TCP 443 reachable" doesn't mean the app is healthy. Health-check a path that actually exercises the dependency chain you care about (`/healthz?deep=true`).
- **No TTL planning before a cutover.** A DNS change with a 24-hour TTL means stale resolvers for 24 hours after cutover. Lower the TTL well in advance of a planned cut.
- **Geolocation-only routing without a default.** Users from unmapped countries get NXDOMAIN. Always set the catch-all default ("anywhere else").
- **Routing controls without safety rules.** A single misclick during an incident can promote both Regions to writer. Safety rules ("only one Region active") prevent this.
- **No `Resolver Query Logging`.** When you need to investigate "where did this request go," resolver query logging to CloudWatch / S3 is invaluable.
- **Private + public hosted zones with overlapping names.** Private zone wins inside VPCs that have it; public elsewhere. Easy to confuse; document explicitly.
- **Skipping ARC for a "manual runbook" multi-Region failover.** Manual runbooks fail at 3 AM. ARC's routing controls + safety rules + readiness checks are far more reliable.

## Pairs well with
- [CloudFront](cloudfront.md) — Route 53 alias to a CloudFront distribution for the public origin.
- [ELB](elb.md) — alias to ALB / NLB.
- **Amazon Application Recovery Controller (ARC)** — failover orchestration.
- **AWS Certificate Manager (ACM)** — TLS certs for the domains.
- **AWS Global Accelerator** — alternative to DNS-based geographic routing for non-HTTP traffic.

## Pairs well with these repo pages
- `docs/02-patterns/multi-region-active-passive.md` (forthcoming) — ARC is the failover primitive.
- `docs/04-reference-architectures/static-website-s3-cloudfront.md` (forthcoming) — Route 53 alias to CloudFront.

## Further reading
- [Amazon Route 53 documentation](https://docs.aws.amazon.com/Route53/).
- [Routing policy reference](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-policy.html).
- [Amazon Application Recovery Controller (ARC)](https://docs.aws.amazon.com/r53recovery/latest/dg/what-is-route53-recovery.html).
- [Route 53 Resolver](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resolver.html).
- [Route 53 SLA](https://aws.amazon.com/route53/sla/).
