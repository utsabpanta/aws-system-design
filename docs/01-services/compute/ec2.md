# EC2 (Elastic Compute Cloud)

> **One-line summary.** Virtual machines as a service — the lowest-level AWS compute primitive and the substrate most other services run on top of.

## TL;DR
- The original AWS service. If a workload doesn't fit a higher-level primitive (Lambda, Fargate, RDS, …), it runs on EC2.
- Pick the right *instance family* (compute-optimized, memory-optimized, storage-optimized, GPU) before tuning anything else. The family choice swamps any in-instance optimization.
- **Graviton (ARM) instances are the default starting point in 2026.** M8g/C8g/R8g (Graviton4) deliver the best price/performance for most stateless workloads; M9g (Graviton5) is the newest.
- Auto Scaling Groups + an Application Load Balancer is the canonical "I want to run a web app on EC2" pattern. Spot Instances drop the bill 60–90% if the workload tolerates eviction.
- The biggest operational gotcha isn't the instance — it's the EBS volume type (`gp3` is the right default), the AMI lifecycle, and the security group rules.

## When to use it
- You need OS-level control (custom kernel, GPU drivers, kernel modules, niche package installs).
- The workload is long-running and steady-state — Lambda or Fargate would cost more at sustained load.
- You're running something AWS doesn't have a managed service for (self-hosted Kafka, exotic databases, ML training with custom CUDA setup).
- Compliance demands single-tenant hardware (Dedicated Hosts, Dedicated Instances).

## When NOT to use it
- The workload fits Lambda (<15 min, event-driven, stateless) — use Lambda.
- The workload is a stateless container with HTTP ingress — use ECS+Fargate or App Runner / ECS Express Mode.
- You'd be running an OS just to host a database AWS already manages (Postgres → RDS, Redis → ElastiCache).
- You don't want to patch, snapshot, or upgrade an OS.

## Key concepts

**Instance family + size** — `m8g.large`, `c7i.xlarge`, `r7gd.4xlarge`. The letter is the family (M general purpose, C compute, R memory, X high-mem, I/D storage, G/P GPU). The number is the generation (higher = newer / faster / cheaper). The suffix denotes processor or features: `g` = Graviton (ARM), `i` = Intel, `a` = AMD, `d` = NVMe instance store, `n` = network-optimized, `e` = extended memory, `b` = block storage optimized.

**Generation cheat sheet (2026):**
- General purpose: **M8g** (Graviton4) is the default. **M9g** (Graviton5) for newest workloads.
- Compute-intensive: **C8g** / **C7i**.
- Memory-intensive: **R8g** / **R7iz** (high-frequency).
- Storage-intensive: **I4g**, **Im4gn**, **D3en**.
- GPU/ML: **P5** (H100), **G6** (L4), **Trn1/Trn2** (Trainium), **Inf2** (Inferentia2).
- Burstable: **T4g** for cheap small workloads where bursts are rare.

**AMI (Amazon Machine Image)** — the disk image an instance boots from. Maintain your own AMIs with [EC2 Image Builder](https://docs.aws.amazon.com/imagebuilder/) or build them in CI; never SSH in and `apt install` your way to a "golden" image you can't rebuild.

**EBS (Elastic Block Store)** — durable network-attached block storage. `gp3` is the right default — cheaper *and* faster than the legacy `gp2`. Use `io2 Block Express` for databases needing >16k IOPS sustained. Instance store (NVMe local to the host) is fast, cheap-per-GB, and ephemeral.

**ENI (Elastic Network Interface)** — the virtual NIC inside the VPC. Each instance type caps the number of ENIs and IPs per ENI; Pod density on EKS is bounded by this unless you use `VPC CNI custom networking` or `prefix delegation`.

**Auto Scaling Group (ASG)** — the unit of horizontal scaling. Defines launch template, min/max/desired capacity, AZ spread, scaling policies (target tracking on CPU/ALB request count, or step scaling). ASG replaces failed instances automatically.

**Spot Instances** — up to 90% off on-demand. AWS can reclaim with a 2-minute notice. Pair with a [Mixed Instances Policy](https://docs.aws.amazon.com/autoscaling/ec2/userguide/asg-purchase-options.html) across multiple types and AZs to keep capacity stable. Lifecycle hooks let you drain gracefully.

**Reserved Instances / Savings Plans** — commit to 1- or 3-year usage for 30–70% off. Compute Savings Plans are the most flexible (apply across families, Regions, even Fargate/Lambda); EC2 Instance Savings Plans go deeper but lock to a family in one Region.

## Pricing model

Charged per-second (1-minute minimum) for Linux/Windows on-demand. Three discount mechanisms:

1. **Savings Plans** (1- or 3-year commit, ~30–66% off depending on flexibility).
2. **Reserved Instances** (older — similar discount, less flexibility; SPs are usually the right choice for new commits).
3. **Spot** (variable price, 60–90% off, 2-minute reclaim notice).

EBS volumes billed per GB-month + per IOPS/throughput above the included baseline (`gp3` includes 3,000 IOPS / 125 MB/s free). Data transfer billed separately — *between AZs in the same Region is not free*, and per-GB egress to the internet is the big surprise on most bills.

## Quotas & limits

The defaults bite hard for new accounts:
- **vCPU quotas per family group** (e.g., "standard On-Demand" covers M/C/R/A/T/Z; 32 vCPUs for new accounts is common). [Service Quotas console](https://docs.aws.amazon.com/general/latest/gr/aws_service_limits.html) is the place to raise these.
- **Spot vCPUs** — separate quota per family group, often lower than on-demand.
- **Elastic IPs per Region** — defaults to 5.
- **EBS volume size**: up to 64 TiB per volume; **snapshot storage**: unlimited but billed.
- **Instances per VPC / per AZ**: implicitly bounded by subnet IP space — size subnets generously (/24 is usually too small for production).

Raise quotas *before* you need them; some increases take days of human review.

## Common pitfalls

- **`gp2` volumes for new workloads.** `gp3` is cheaper and faster. Migrate; it's a one-API-call change with no downtime.
- **`t`-family for production workloads with steady CPU.** Burst credits run out, then the instance throttles. T-family is for *bursty* workloads, not "small cheap."
- **Single AZ in production.** A whole AZ goes down ~once every couple years. ASG across 2+ AZs is the minimum.
- **Long-lived SSH keys baked into AMIs.** Use Systems Manager Session Manager instead — no inbound SSH, IAM-controlled, fully audited.
- **Public IPs in private subnets.** Subnet's "auto-assign public IP" setting on by accident is a classic source of unintended internet exposure.
- **No instance metadata IMDSv2 enforcement.** SSRF attacks against IMDSv1 have stolen credentials repeatedly; enforce IMDSv2 via launch template and via SCPs.
- **Ignoring [Compute Optimizer](https://aws.amazon.com/compute-optimizer/) recommendations.** Most workloads are over-provisioned; Compute Optimizer surfaces it for free.

## Pairs well with
- **Auto Scaling Groups + ALB/NLB** — the standard web-tier topology.
- **EBS + RDS / ElastiCache** — durable state externalized off the instance.
- **Systems Manager Session Manager** — shell access without inbound SSH.
- **CloudWatch + AppConfig** — observability and runtime config.
- **EFS / FSx** — when multiple instances need shared filesystem state.

## Further reading
- [Amazon EC2 documentation](https://docs.aws.amazon.com/ec2/).
- [Instance types](https://aws.amazon.com/ec2/instance-types/) — the canonical (and lengthy) list.
- [EC2 Spot best practices](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-best-practices.html).
- [Graviton getting-started](https://aws.amazon.com/ec2/graviton/) — what to know before rebuilding for ARM.
- Amazon Builders' Library — "Reliability, constant work, and a good cup of coffee" (Amazon's pattern for EC2-scale services).
