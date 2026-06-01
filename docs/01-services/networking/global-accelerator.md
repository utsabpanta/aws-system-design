# Global Accelerator

> **One-line summary.** Two static **anycast IPs** that map to your application across one or more Regions, routing traffic over the AWS backbone for predictable latency and fast Regional failover.

## TL;DR

- For non-HTTP / non-cacheable traffic where you'd want CloudFront's "AWS backbone, edge entry" benefit. Game servers, IoT, TCP/UDP services, multi-Region active-active web stacks.
- Two **fixed anycast IPs** that don't change — easier than juggling Route 53 for client allow-lists, firewall rules, and DNS-cache-busting.
- Traffic enters AWS at the **nearest edge POP** (180+ POPs), then traverses the AWS backbone to the closest healthy endpoint. Lower jitter, lower tail latency than the public internet.
- **Health checks + traffic dials** move traffic away from impaired endpoints in seconds — no waiting for DNS TTL.
- Costs more than DNS-only routing; the cost is justified when latency / reliability of non-HTTP traffic matters or when static IPs are a hard requirement.

## When to use it

- Real-time games, video conferencing, voice — UDP / RTP / WebRTC that needs predictable latency.
- IoT fleets that need a static IP for firmware / firewall reasons.
- Multi-Region failover where DNS TTLs are too slow (seconds vs minutes).
- TCP services (databases over private TCP, custom protocols, FTP / SFTP).
- "We need a static IP" — Global Accelerator gives you two anycast IPs that map to evolving backends.

## When NOT to use it

- Plain HTTP that's cacheable — **CloudFront** is cheaper and adds caching.
- Single-Region, low-volume workloads — Route 53 + ALB is fine and dramatically cheaper.
- Workloads that only need same-Region routing — Global Accelerator's value is the AWS backbone + edge entry; it doesn't help a single-AZ deployment.

## Key concepts

**Standard Accelerator.** Network-layer (TCP/UDP) acceleration. The default.

**Custom Routing Accelerator.** Maps client IP + port to specific backends deterministically — used heavily for gaming (match-make a player to a specific game-server instance).

**Listener.** Port or port range + protocol (TCP / UDP). The accelerator's "endpoint" the client connects to.

**Endpoint group.** A Region's worth of endpoints. Each accelerator can have endpoint groups in multiple Regions; **traffic dial** (0–100%) controls how much of the eligible traffic goes to each group, enabling instant blue/green and canary across Regions without DNS changes.

**Endpoint.** ALB / NLB / EC2 instance / Elastic IP within an endpoint group. Each endpoint has a weight (within its group).

**Health checks.** Continuous health checks on each endpoint. Unhealthy endpoints are removed from the pool in seconds, no DNS to update.

**Client affinity.** None (default — distribute round-robin) or Source IP (sticky to one endpoint by client IP — useful for game sessions).

**Two static anycast IPs.** AWS assigns them; they're announced from every Global Accelerator edge POP. The client's network sends to whichever is closest by BGP, and Global Accelerator forwards.

**BYOIP.** Bring your own IPv4 / IPv6 prefix to Global Accelerator if you already have IPs allow-listed everywhere.

## Pricing model

- **Per accelerator-hour** (small flat fee).
- **Per-GB transferred** ("Data Transfer Premium" — charges based on dominant traffic direction and the source/destination Regions).
- **Listeners and endpoint groups** are part of the accelerator; no separate fee.

Global Accelerator isn't cheap — the per-GB premium is on top of standard AWS egress. Use it when the latency and reliability gains justify the cost; for cacheable HTTP, CloudFront's per-GB rates plus cache hit ratio usually win.

## Quotas & limits

- **Accelerators per account**: 20 default (raisable).
- **Endpoint groups per listener**: 100.
- **Endpoints per endpoint group**: 100.
- **Listeners per accelerator**: 10.
- **BYOIP prefix size**: /24 minimum.

## Common pitfalls

- **Global Accelerator in front of cacheable HTTP.** CloudFront cache + AWS backbone is cheaper and faster. Use Global Accelerator only for non-cacheable / non-HTTP traffic.
- **Reliance on DNS for "instant failover."** DNS TTL makes "instant" actually mean tens of seconds to many minutes. Global Accelerator's traffic dial and health-check-based removal are seconds.
- **Endpoint groups in one Region only.** Single-Region usage misses the cross-Region failover value. If you can't justify multi-Region endpoints, you might not need Global Accelerator.
- **Forgetting client affinity for games / WebRTC.** Round-robin breaks session-based protocols. Enable Source IP affinity where the protocol needs stickiness.
- **Skipping Custom Routing for game backends.** Mapping players to specific game-server processes deterministically is a Custom Routing strength — using Standard requires layer-7 logic on the backend.
- **Two-IP-list maintenance ignored.** Distributing the static anycast IPs to many client teams / firewalls and forgetting one of them creates "works for half the users" failures. Document and propagate both IPs everywhere they're allow-listed.

## Pairs well with

- [CloudFront](cloudfront.md) — sibling service for HTTP; Global Accelerator is for non-HTTP and non-cacheable.
- [Route 53](route53.md) — friendly name in front of the static anycast IPs.
- [ELB](elb.md) — common endpoints (ALB / NLB) per Region.
- **AWS Shield Standard / Advanced** — DDoS protection inherits at the accelerator level.
- **CloudWatch metrics** — `ProcessedBytes`, health-check pass/fail counts per endpoint group.

## Pairs well with these repo pages

- `docs/02-patterns/multi-region-active-active.md` (forthcoming) — Global Accelerator is one of the AWS-native multi-Region routing primitives.

## Further reading

- [AWS Global Accelerator documentation](https://docs.aws.amazon.com/global-accelerator/).
- [Standard vs Custom Routing](https://docs.aws.amazon.com/global-accelerator/latest/dg/about-accelerator-types.html).
- [Traffic dials and endpoint weights](https://docs.aws.amazon.com/global-accelerator/latest/dg/about-endpoint-groups-traffic-dial.html).
- [Comparing CloudFront and Global Accelerator](https://aws.amazon.com/global-accelerator/faqs/).
