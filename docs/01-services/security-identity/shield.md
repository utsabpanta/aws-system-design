# Shield

> **One-line summary.** AWS's DDoS protection service. **Shield Standard** is free and automatic for every AWS account; **Shield Advanced** is a paid subscription that adds L7 protection, the DDoS Response Team (DRT), and cost protection during attacks.

## TL;DR
- **Shield Standard** is on by default on every AWS account at no cost. Protects CloudFront, Route 53, ALB, NLB, and Global Accelerator from common L3/L4 DDoS attacks (SYN floods, UDP reflection).
- **Shield Advanced** is a paid monthly subscription (per AWS Organization) — adds **L7 DDoS protection**, **24/7 DDoS Response Team**, **cost protection** (AWS credits scaled costs back during a documented attack), and **unlimited WAF rule usage** on protected resources.
- Only consider Shield Advanced if you run high-profile public services that are credible DDoS targets — large e-commerce, gaming, news, financial.
- The "protected resources" concept matters: Shield Advanced is per-resource; activate it on the specific ALBs / CloudFront distributions / Global Accelerator endpoints that need it.
- Pair with **AWS WAF** (rule-based filtering), **CloudFront** (absorption capacity), and **Route 53 ARC** (failover) for a defense-in-depth picture.

## When to use it

**Shield Standard:** always on; nothing to enable.

**Shield Advanced:**
- High-profile public services where a sustained L7 DDoS would be a credible business event.
- Online gaming, news during election cycles, real-time finance, e-commerce during peak season.
- Workloads with contractual or regulatory uptime obligations that include DDoS scenarios.
- Workloads where you'd want the AWS DRT on a war-room call within minutes of an attack.

## When NOT to use it
- Low-profile workloads. Shield Standard's automatic protection is sufficient for most.
- Internal-only services that the internet can't reach.
- Workloads where you'd rather invest in CloudFront + WAF + over-provisioning than in a subscription that protects a small fraction of your stack.

## Key concepts

### Shield Standard (free, automatic)
- Always on for **CloudFront, Route 53, Global Accelerator, ALB, NLB, EC2 with EIPs**.
- Inline mitigation for common L3/L4 attacks — SYN floods, UDP reflection (DNS, NTP, SSDP), ICMP floods.
- No DRT support; no cost protection.

### Shield Advanced (paid)
- Per-AWS-Organization subscription at a significant monthly fee plus per-protected-resource fees on top of the underlying resource pricing.
- **Protected resources.** Enable Shield Advanced per resource (CloudFront distribution, ALB, NLB, Global Accelerator, Route 53 hosted zone, Elastic IP). Up to a configured maximum.
- **L7 DDoS protection** — automatic mitigation for application-layer attacks against protected CloudFront / ALB.
- **Proactive Engagement** — opt-in: the DRT proactively engages during a detected attack.
- **24/7 DDoS Response Team (DRT)** — engineers you can call (or who call you) during an event. Tunes WAF rules live, makes routing changes, helps with incident management.
- **Cost protection** — if a DDoS forces your AWS bill up (CloudFront data transfer, autoscaling), AWS credits the overage as service credits.
- **Unlimited WAF rule usage** — Shield Advanced bundles unlimited use of standard WAF rules on protected resources, removing per-rule pricing.
- **Health-based detection** — uses Route 53 / Application Recovery Controller signals to better detect attacks vs legitimate traffic.

### How attacks are mitigated
- **L3/L4** — AWS edge absorbs traffic, scrubbing centers strip attack patterns, only legitimate traffic forwarded to origin.
- **L7 (HTTP/HTTPS)** — Shield + WAF managed rule groups + custom rules + adaptive scoring. The DRT can deploy emergency rules in real time during an attack.

### Reporting
- **DDoS Reports** in CloudWatch and the Shield console — visibility into ongoing and historical events on protected resources.
- **CloudWatch metrics** — `DDoSDetected`, `DDoSAttackBitsPerSecond`, etc.

## Pricing model

- **Shield Standard**: free.
- **Shield Advanced**: significant monthly fee per Organization (in the thousands of dollars/month range) + per-protected-resource fees + data transfer charges that may exceed the included quotas. Cost protection refunds *DDoS-attack-driven* spikes only.

The Advanced subscription is large enough that it only makes economic sense when DDoS protection beyond Standard is a genuine business requirement.

## Quotas & limits

- **Protected resources per Shield Advanced subscription**: 1,000 default (raisable).
- **Health-based detection**: limited by associated Route 53 health checks.
- **DRT engagement**: 24/7 if you're a Shield Advanced subscriber.

## Common pitfalls

- **Forgetting Shield Standard is already on.** Many teams "evaluate DDoS protection" without realizing the basics are already in place — saving Advanced for genuine high-profile threat models.
- **Shield Advanced without protecting the actual resource.** Subscribing to Advanced but forgetting to flip on Shield Advanced for the specific CloudFront distribution / ALB you care about. The subscription doesn't auto-protect; you opt-in per resource.
- **No WAF on Shield-Advanced-protected resources.** L7 protection works much better with WAF rules in place. Use the unlimited WAF entitlement.
- **No CloudFront in front of ALB/NLB.** CloudFront's edge absorbs orders-of-magnitude more attack traffic than direct origin. Even with Shield Advanced on the ALB, fronting it with CloudFront is a meaningful improvement.
- **DRT not engaged in IR runbooks.** Subscribers can call the DRT during an incident; many teams forget to include this in their playbooks.
- **Cost protection misunderstood.** Credits cover *attack-driven* overage only — not "we forgot to add an SP and now CloudFront is expensive."

## Pairs well with
- [WAF](waf.md) — L7 filtering; Shield Advanced bundles unlimited WAF on protected resources.
- [CloudFront](../networking/cloudfront.md) — edge absorption; primary protection layer.
- [Route 53](../networking/route53.md) and **Application Recovery Controller** — failover during sustained attacks.
- **Global Accelerator** — anycast routing absorbs distributed attacks.

## Pairs well with these repo pages
- [WAF](waf.md), [CloudFront](../networking/cloudfront.md).

## Further reading
- [AWS Shield documentation](https://docs.aws.amazon.com/waf/latest/developerguide/shield-chapter.html).
- [Shield Advanced overview](https://aws.amazon.com/shield/features/).
- [DDoS Response Team (DRT)](https://aws.amazon.com/shield/drt/).
- [Shield pricing](https://aws.amazon.com/shield/pricing/).
- [AWS Best Practices for DDoS Resiliency whitepaper](https://docs.aws.amazon.com/whitepapers/latest/aws-best-practices-ddos-resiliency/welcome.html).
