# ELB (Elastic Load Balancing)

> **One-line summary.** AWS's load-balancing family — Application Load Balancer (L7 HTTP), Network Load Balancer (L4 TCP/UDP/TLS), Gateway Load Balancer (L3 for inline virtual appliances), and the legacy Classic Load Balancer.

## TL;DR
- **ALB** for HTTP / HTTPS / WebSocket / gRPC. Path-based routing, host-based routing, header / query rules, native ECS / EKS integration, native cognito / OIDC auth, native WAF, native Lambda target.
- **NLB** for TCP / UDP / TLS. Sub-millisecond overhead, millions of RPS, static IPs (one per AZ), preserves client source IP. Right for non-HTTP, ultra-low-latency, or "give me a static IP" use cases.
- **GWLB (Gateway Load Balancer)** routes traffic transparently through fleets of third-party virtual appliances (firewalls, IDS/IPS, packet inspection) at scale.
- **Classic Load Balancer (CLB) is essentially legacy.** EC2-Classic itself was retired in 2022; CLB is deprecated for new deployments. Migrate to ALB / NLB.
- An ALB is **rarely the right one-per-service answer** — share an ALB across many services with host- and path-based listener rules to amortize the hourly fee (which is exactly what ECS Express Mode does for you).

## When to use which

| Scenario | Use |
|---|---|
| HTTP / HTTPS / WebSocket / gRPC | **ALB** |
| Non-HTTP TCP / UDP, very low latency, static IP | **NLB** |
| TLS termination at L4 (passes through L7) | **NLB with TLS listener** |
| In-line virtual appliances (firewalls, IDS) | **GWLB** |
| New work | Never CLB |

## When NOT to use ELB at all
- For a single Region behind CloudFront serving cacheable HTTP — CloudFront → S3 may not need an LB at all.
- For serverless HTTP — Lambda + API Gateway or Function URL is often simpler.
- For service-to-service traffic inside one VPC — ECS Service Connect, App Mesh-replacement (VPC Lattice / ECS Service Connect), or direct NLB / ALB targets can be more direct.

## Key concepts

### Application Load Balancer (ALB)
- **Layer 7** — terminates HTTP, can inspect headers, paths, query strings.
- **Target groups** — per protocol/port; targets are EC2 instances, IP addresses, Lambda, ALB-as-target (chained).
- **Listener rules** — route based on host, path, header, query string, source IP, HTTP method, or weighted-mix between target groups.
- **Authentication** — built-in OIDC (Cognito, Google, Okta, Auth0, etc.) without writing auth code.
- **WAF integration** — attach a Web ACL directly.
- **Sticky sessions** — cookie-based (LB-generated or app-set).
- **HTTP/2, HTTP/3 (QUIC)**, gRPC support.
- **Slow start**, **least outstanding requests** routing algorithm options.
- **Mutual TLS (mTLS) on the listener** — client certificate validation at the LB.

### Network Load Balancer (NLB)
- **Layer 4** — TCP / UDP / TLS. Preserves client source IP.
- **Static IPs** — one EIP per AZ; bring your own IP / public IP.
- **TLS termination** at the LB (cert via ACM) or pass-through (TCP listener).
- **Extremely high throughput / low latency** — sub-millisecond LB overhead, millions of RPS.
- **Cross-zone load balancing** is off by default for NLB (each AZ's NLB only balances within its AZ); enable for true cross-AZ balancing at the cost of cross-AZ data transfer.
- **PrivateLink endpoint service** — NLB is the canonical fronting LB when exposing your service to other accounts via PrivateLink.

### Gateway Load Balancer (GWLB)
- **Layer 3 / 4** — transparent network insertion of third-party virtual appliances.
- Uses **GENEVE** encapsulation to send traffic to a fleet of appliances and bring the inspected traffic back.
- Sold to enterprises running Palo Alto, Check Point, Fortinet, etc. virtual firewalls in AWS at scale.

### Classic Load Balancer (CLB)
- Legacy from EC2-Classic days. CLB was retired alongside EC2-Classic in 2022.
- Existing CLBs continue to work; the console hides the option for new environments in Elastic Beanstalk and elsewhere.
- **Migrate to ALB or NLB** — the migration is straightforward and unlocks newer features.

## Common to ALB / NLB
- **Multi-AZ.** Spread targets and the LB across at least 2 AZs.
- **Health checks.** HTTP path (ALB) or TCP probe (NLB). Set sensible thresholds; aggressive failure thresholds during deploys can mass-deregister healthy targets briefly.
- **Connection draining (deregistration delay)** — the LB stops sending new connections to a target but waits up to N seconds for existing connections to drain.
- **Access logs** to S3.

## Pricing model

- **Per LB-hour** — flat per ALB / NLB / GWLB (small).
- **Per LCU-hour** — **L**oad **B**alancer **C**apacity **U**nit. Captures the actual work the LB does — new connections per second, active connections, processed bytes, rule evaluations. The dominant cost component for non-trivial traffic.
- **Data transfer** — same AWS rules; cross-AZ matters for NLB cross-zone.

NLBs are typically cheaper than ALBs for raw TCP forwarding; ALBs justify the cost when their L7 features (auth, path routing, WAF) save engineering work elsewhere.

## Quotas & limits

- **ALBs / NLBs per Region**: 50 default (raisable).
- **Target groups per LB**: 100.
- **Rules per ALB listener**: 100 default (raisable).
- **Targets per target group**: 1,000 (raisable).
- **Listeners per LB**: 50.
- **Maximum certificates per ALB / NLB**: 25 (raisable) for SNI.
- **GWLB**: targets up to thousands per appliance fleet.

## Common pitfalls

- **One ALB per micro-service.** Hourly fee × many services adds up. Share an ALB; use listener rules with host or path. ECS Express Mode automates this.
- **NLB cross-zone off when needed.** A 4-AZ NLB with cross-zone off only balances within an AZ — a hot AZ stays hot. Enable cross-zone where balancing matters more than the cross-AZ data charges.
- **Aggressive health checks during deploys.** Brief 503s during a deploy can mass-deregister healthy targets. Tune thresholds with rolling updates in mind.
- **No TLS termination plan.** ACM certs are free for AWS-fronted LBs; use them instead of bringing your own.
- **CLB for new deployments.** Don't.
- **Forgetting `X-Forwarded-For` / Proxy Protocol.** ALB sets `X-Forwarded-For`; NLB optionally enables Proxy Protocol v2. Application logs without these show the LB's IP for every request — useless for security investigation.
- **ALB target group health on the *infrastructure* not the *app*.** A `/` check that the load balancer can reach proves nothing about the app. Health-check a `/healthz` that exercises real dependencies (with sensible failure modes).
- **Public-facing NLB with no source-IP allow-list.** NLB preserves client IP; you can scope at the SG on the target. Use that.

## Pairs well with
- [VPC](vpc.md) — the LB lives in subnets across AZs.
- [Route 53](route53.md) — alias from a friendly name.
- [CloudFront](cloudfront.md) — in front of ALB for caching + WAF + Shield.
- [ECS](../compute/ecs.md) / [EKS](../compute/eks.md) — primary ALB / NLB consumers.
- **AWS Certificate Manager (ACM)** — free TLS certs.
- **AWS WAF** — managed and custom rule groups for ALB.
- **PrivateLink** — expose your service via NLB endpoint service.

## Further reading
- [Elastic Load Balancing documentation](https://docs.aws.amazon.com/elasticloadbalancing/).
- [Application Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/).
- [Network Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/).
- [Gateway Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/gateway/).
- ["Choosing between ALB, NLB, GWLB" AWS docs](https://docs.aws.amazon.com/elasticloadbalancing/latest/userguide/what-is-load-balancing.html#elb-features).
