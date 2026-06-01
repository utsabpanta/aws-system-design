# Lightsail

> **One-line summary.** A fixed-price, pre-bundled cloud VPS with managed databases, containers, CDN, and load balancers. AWS's "easy mode" front door.

## TL;DR

- Predictable monthly pricing for VMs (instances), databases, container services, load balancers, and CDN distributions. No EC2-style menu paralysis.
- Right for personal projects, prototypes, WordPress sites, small SaaS, and the "I just want a Linux box" use case. Not right for anything that needs the full AWS control plane.
- Lightsail resources live in their own simplified Region/AZ model; bridging them into a full VPC requires VPC peering (one click in the console) and isn't always seamless.
- Actively maintained in 2026 — compute-optimized and memory-optimized bundles, larger managed-database tiers, and a WordPress blueprint were all added in early 2026.
- Migrate to EC2 / RDS / ECS once your needs outgrow the bundle structure (the in-console "upgrade to EC2" tool snapshots and exports).

## When to use it

- Personal projects, hobby apps, small business sites, blogs, learning environments.
- A simple WordPress, Ghost, or Nextcloud install — the blueprints take 60 seconds.
- Small SaaS that needs a predictable monthly bill rather than per-second EC2 billing.
- A simple managed Postgres/MySQL for a side project (Lightsail managed databases are cheaper at the small end than RDS).
- Quick HTTP services as Lightsail container services (a lightweight alternative to App Runner now that App Runner is closing).

## When NOT to use it

- Production workloads needing full AWS integration (Security Hub, GuardDuty findings, fine-grained IAM, custom VPC topology, Direct Connect, etc.).
- Anything that needs Auto Scaling Groups, custom AMIs, GPUs, or instance types beyond the limited Lightsail catalog.
- Multi-Region or DR-grade designs — Lightsail's high-availability story is much narrower than EC2/RDS.
- Cost-sensitive scaling — at moderate scale, EC2 + Savings Plans is dramatically cheaper than the Lightsail bundle markup.

## Key concepts

**Instance** — a Linux or Windows VM. Pre-bundled at a fixed monthly price covering vCPU, RAM, SSD storage, and a transfer allowance. Tiers from a free-tier-eligible "nano" up to 72-vCPU compute-optimized and high-RAM memory-optimized bundles (added early 2026).

**Blueprint** — a launchable application image: LAMP, WordPress, Node.js, .NET, Plesk, Ghost, etc. Useful for one-click installs.

**Managed database** — single-node or HA Postgres/MySQL with backups, snapshots, and read-replica support, at fixed monthly tiers. Lightsail expanded this in 2026 with bundles up to 8 vCPU / 32 GB / 960 GB SSD.

**Container service** — fully managed container hosting. Push an image to AWS, Lightsail runs it behind an HTTPS endpoint with TLS and auto-scaling. The Lightsail analogue to App Runner / ECS Express Mode.

**Load balancer** — simple HTTPS load balancer with built-in cert via ACM. No L7 sophistication of ALB but cheap and serviceable.

**CDN distribution** — Lightsail's CloudFront wrapper. Same edge network underneath, simplified config.

**Object storage (Lightsail Buckets)** — S3-compatible storage with a flat per-GB fee.

**Static IP** — free while attached to an instance, billed when detached.

**Transfer allowance.** Each instance bundle includes a generous monthly internet egress allowance; overage is billed per GB at standard AWS rates. This is the main pricing surprise — high-bandwidth workloads can blow through the bundle.

## Pricing model

- **Fixed monthly bundles** for instances, databases, load balancers, CDN, container services. Per-hour billing prorates the monthly price.
- **Transfer allowance** included in each bundle; overage at standard internet egress rates.
- **Snapshots** and **detached static IPs** billed separately.
- **Container services** charged per node-month at fixed sizes (nano → x-large).

The bundling makes pricing predictable but breaks down at scale: a 32-vCPU Lightsail instance costs significantly more than the equivalent `m8g.8xlarge` on a Compute Savings Plan.

## Quotas & limits

- **Available in 15 AWS Regions** (subset of EC2 Regions, including US East/West, EU Frankfurt/London, Asia Pacific Tokyo/Jakarta).
- **Instances per account per Region**: 20 default, raisable.
- **Static IPs**: 5 per Region default.
- **Domains**: 6 DNS zones per account.
- **Load balancers**: 5 per Region.
- Many features (VPC peering, SSH key pairs) operate within Lightsail's own scope; bridging to the main AWS VPC requires explicit peering.

## Common pitfalls

- **Outgrowing Lightsail.** Workloads that need ALB rules, multi-AZ HA, full IAM, or Auto Scaling end up half-in-Lightsail-half-in-EC2 — painful. Migrate early if you see the seams coming. The in-console "upgrade to EC2" tool helps.
- **Blueprint drift.** Lightsail blueprints are point-in-time installs; they don't auto-update WordPress / Plesk / etc. Patching is your problem.
- **Internet transfer overage.** A viral blog post blows through the bundle allowance; the overage bill is real even though the base bundle felt cheap.
- **Limited observability.** CloudWatch coverage is thinner than for EC2/RDS; no Container Insights, limited Performance Insights on managed DBs.
- **Static IPs that detach.** Detaching a static IP starts billing immediately and can surprise you on cleanup.
- **Treating Lightsail Buckets as S3.** They share the API but have separate quotas, less feature parity (no Object Lock, narrower lifecycle), and a different pricing model.
- **DR through Lightsail.** Cross-Region replication and multi-Region failover are basically not first-class. If you need that, you're outgrowing Lightsail.

## Pairs well with

- **Route 53** (hosted zones live there, even if you point them at Lightsail resources).
- **CloudFront** — Lightsail CDN distributions are CloudFront under the hood; for advanced caching policies you can also point full CloudFront at a Lightsail instance origin.
- **Lightsail Container Service** — for small containerized HTTP workloads.
- **Backups + snapshots** — schedule them; Lightsail won't do it by default.

## Pairs well with these repo pages

- [EC2](ec2.md) — the upgrade path when Lightsail's ceiling becomes a problem.
- [App Runner](app-runner.md) — the AWS-managed container alternative (also a Lightsail-Container alternative, though App Runner is closing to new customers in 2026).
- [ECS](ecs.md) — the right container destination at production scale.

## Further reading

- [Amazon Lightsail documentation](https://docs.aws.amazon.com/lightsail/).
- [Lightsail FAQs](https://aws.amazon.com/lightsail/faq/).
- [Upgrade from Lightsail to EC2](https://docs.aws.amazon.com/lightsail/latest/userguide/amazon-lightsail-upgrading-to-amazon-ec2.html).
- [Lightsail Container Service overview](https://docs.aws.amazon.com/lightsail/latest/userguide/amazon-lightsail-containers.html).
