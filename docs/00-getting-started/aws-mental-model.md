# AWS mental model

> **One-line summary.** Regions, AZs, edge, IAM, and the shared responsibility line — the load-bearing concepts every other page assumes you already understand.

## TL;DR

- A **Region** is a city-sized blast radius; an **Availability Zone** is a campus-sized blast radius inside it. Almost all of your design decisions live at the AZ boundary.
- The **shared responsibility model** decides who you can blame at 3 AM: AWS owns the cloud, you own *in* the cloud.
- **IAM** is the only thing standing between your account and someone else's bitcoin miner. Least privilege is not optional.
- The **VPC** is your private network. Every service either lives in a VPC or talks to one through an endpoint — never assume internet routing.
- AWS has four tiers of service abstraction (managed instances → managed services → serverless → fully managed). Pick the highest one your problem allows; you'll spend less on operations.

## Geography

### Regions

A Region is a geographically distinct cluster of data centers. Each Region has its own copy of most AWS services and is **isolated by default** — IAM roles, S3 buckets, KMS keys, VPCs, almost everything is Region-scoped. When you "make a service multi-Region," you're solving a cross-Region replication problem from scratch.

There are 30+ public Regions (and growing). The Region code (`us-east-1`, `eu-west-2`, `ap-southeast-1`) shows up in every ARN and in every endpoint URL.

A few Regions are special:

- **`us-east-1` (N. Virginia)** — the oldest, the largest, and the only place several global services live (IAM, CloudFront distributions, Route 53 hosted zones). Outages here ripple wider than outages elsewhere.
- **GovCloud and China Regions** — separate partitions with separate IAM and separate billing. Use a different ARN prefix (`aws-us-gov:`, `aws-cn:`).

### Availability Zones

A Region has 3–6 AZs. Each AZ is one or more physically separate data centers, on independent power and network, within tens-of-kilometers latency of each other (single-digit-ms RTT inside a Region).

The mental model: **AZ-level failures are the failure mode you design against**. AWS designs services so that any single AZ can fail without taking the service down — *if you've used the service correctly*. RDS Multi-AZ, S3 (always multi-AZ), DynamoDB (always multi-AZ), ELB across subnets in 2+ AZs. If you put everything in one AZ, you've opted out of the resilience you're paying for.

Two AWS-specific quirks worth knowing:

1. **AZ names are randomized per account.** `us-east-1a` in your account is not the same physical AZ as `us-east-1a` in someone else's. The stable identifier is the *Availability Zone ID* (`use1-az1`).
2. **An AZ is not a single building.** It can be several data centers, scattered across a metro, networked as one logical unit.

### Local Zones, Wavelength, Outposts

- **Local Zones** push compute and storage into specific metro areas (LA, Boston, Atlanta) for single-digit-ms latency to local users. Parent Region is still the source of truth.
- **Wavelength Zones** sit inside telco 5G networks (Verizon, KDDI) for ultra-low-latency mobile workloads.
- **Outposts** is an AWS rack you install in your own data center. Same APIs as the cloud, runs against your physical hardware.

These exist for very specific latency or data-residency constraints. Most workloads don't need them.

### Edge locations

**CloudFront** (CDN) and **Route 53** (DNS) run in 600+ edge locations worldwide — far more than there are Regions. The user's request hits the nearest edge, which terminates TLS, serves cache hits locally, and forwards cache misses to the origin in a Region. Anything user-facing belongs behind CloudFront, even if it's a single-Region origin.

## The shared responsibility model

AWS draws a line. **They are responsible for the security *of* the cloud** — physical security, hypervisor, networking fabric, the managed service's runtime. **You are responsible for security *in* the cloud** — IAM users and policies, OS patching on EC2 instances, application code, what you put in your S3 buckets, your secrets.

Where exactly the line falls depends on the abstraction level:

| Service shape | AWS handles | You handle |
|---|---|---|
| EC2 (IaaS) | Hypervisor, physical network | OS, patching, app, IAM, data |
| RDS (managed) | OS, DB engine binary, patching, backups | DB config, schema, queries, IAM, data |
| Lambda (serverless) | OS, runtime, scaling, capacity | App code, IAM, data |
| S3 (fully managed) | Everything except your bucket config | IAM, bucket policy, contents |

When something breaks, the first question is "whose side of the line is this?" That answers whether to open a support case or page your team.

## IAM — Identity and Access Management

The thing standing between your account and a stranger's crypto miner. Four concepts:

- **Principal** — the actor making the request. Could be a user, a role, or an AWS service.
- **Action** — the API call being made (`s3:GetObject`, `dynamodb:PutItem`).
- **Resource** — what the action operates on (an ARN — `arn:aws:s3:::my-bucket/*`).
- **Policy** — JSON that allows or denies combinations of (principal, action, resource), often qualified by conditions (source IP, MFA, time).

The evaluation logic, simplified: **explicit deny > explicit allow > implicit deny.** No allow anywhere means denied. Permissions boundaries, SCPs, and resource-based policies layer on top — see the IAM service page for the full evaluation chart.

Operational rules:

- **Always use IAM roles, never long-lived access keys** for workloads. EC2 has instance profiles; ECS/Lambda have task/execution roles; humans should federate through IAM Identity Center (formerly SSO).
- **Root account is for billing and the initial setup, then locked away.** Enable MFA, store the credentials offline, never use root for day-to-day work.
- **Least privilege is the default, not the goal.** Start with no permissions, add what the workload actually needs. Use Access Analyzer to find unused permissions.

## VPC — the private network

Every Region you use needs a VPC (Virtual Private Cloud). It's a private network you own, defined by a CIDR block (typical: `10.0.0.0/16`). Inside it:

- **Subnets** — slices of the CIDR, each pinned to one AZ. Conventionally split into **public** (has a route to the internet gateway), **private** (no internet route — uses NAT for egress), and **isolated** (no internet at all, often for databases).
- **Route tables** — per-subnet, decide where traffic goes.
- **Security groups** — stateful instance-level firewalls; the default is deny.
- **NACLs** — stateless subnet-level firewalls; usually left at default.
- **Internet Gateway** — the door from public subnets to the internet.
- **NAT Gateway** — egress-only door for private subnets. Charged per hour and per GB; the surprise cost item on most bills.

A common mistake: putting a Lambda in a VPC "for security" when it doesn't need to talk to anything VPC-private. That introduces ENI overhead and complicates cold starts for no security benefit.

To reach AWS services *without* traversing the public internet, use **VPC Endpoints** — Gateway endpoints (S3, DynamoDB) are free; Interface endpoints (most other services) are per-hour + per-GB. Worth setting up when you have meaningful traffic to a service, both for cost (no NAT egress) and security (traffic never leaves AWS's network).

## Service abstraction levels

AWS services fall on a spectrum. As a rule, **pick the highest abstraction that still meets your requirements** — you'll write less code, run less infrastructure, and pay AWS to operate the lower layers.

| Tier | Examples | You manage |
|---|---|---|
| Managed instances | EC2, EBS | OS, runtime, scaling, patching |
| Managed services | RDS, ElastiCache, OpenSearch | Schema, queries, version upgrades |
| Serverless | Lambda, DynamoDB, S3, SQS, EventBridge | App code, configuration |
| Fully managed AI | Bedrock, Rekognition, Textract | API calls |

Going up the stack costs more per unit of compute/storage but less in engineering hours. The crossover varies — for small workloads, serverless is dramatically cheaper end-to-end; for very large steady-state workloads, EC2 with Savings Plans wins on raw price but loses on operational headcount.

## Pricing models

Three things AWS will sell you for compute:

- **On-demand** — pay per hour/second. Highest unit price, zero commitment.
- **Savings Plans / Reserved Instances** — commit to 1 or 3 years for 30–70% off.
- **Spot** — bid on spare capacity for up to 90% off, with the catch that AWS can reclaim it with 2 minutes' notice. Excellent for stateless batch and fault-tolerant workloads.

For storage and data transfer:

- **Storage** is per GB-month, with tiered pricing (S3 Standard > Infrequent Access > Glacier).
- **Data transfer *into* AWS is free.** Data transfer *between* AZs in the same Region is cheap-but-not-free. Data transfer *out* to the internet is the most expensive line on most bills. Cross-Region transfer is expensive. Plan your topology around this.

Three habits that prevent surprise bills:

1. **Tag everything** with cost-allocation tags from day one (`Owner`, `Service`, `Env`). Cost Explorer is only as useful as your tags.
2. **Set Budgets and Anomaly Detection alerts** before anything is in production.
3. **NAT Gateway and inter-AZ data transfer** are the two line items that surprise everyone. Audit them quarterly.

## Service quotas (limits)

Every service has account-level quotas — many of them defaults that are far below what production needs. A 50-page service that runs fine in staging will fail at launch because the Lambda concurrency quota was 1,000 and you needed 10,000.

Habits:

- Check quotas for every service in your design *before* you commit to it.
- Use **Service Quotas** (the AWS service) to view, request increases, and set CloudWatch alarms on quota usage.
- Some quotas are hard (cannot be raised). Know which ones — they affect architecture.

## How to read AWS docs

The AWS documentation set is large and uneven. Heuristics:

- **The service's developer guide** is usually the right starting point — it has narrative and concepts, not just API reference.
- **The pricing page** is canonical and updated whenever pricing changes; ignore third-party "AWS pricing explained" articles.
- **The Well-Architected Framework** lenses (per-workload-type guidance) are unusually high-quality.
- **AWS Architecture Center** has reference architectures that are useful, occasionally aspirational, and worth treating as a starting point rather than a final answer.
- **re:Invent talks** are the best source for the *why* behind a service. The 300-level and 400-level talks are dense and worth the watch.

If a doc page hasn't been updated in 3+ years, treat it with suspicion — the service may have shipped features that obsolete the advice.

## Console vs IaC

The AWS Console is great for exploration, not for production. Production infrastructure should be defined as code (CloudFormation, CDK, Terraform). The reason isn't dogma; it's that:

- Console changes are invisible to your team and your audit log readers.
- Console changes can't be code-reviewed.
- Console changes are nearly impossible to replicate to another Region or another account.

A reasonable workflow: explore in the Console, codify in IaC, then forget the Console exists for that resource. Use `aws cloudformation drift-detection` (or Terraform `plan`) to detect when someone snuck in via the Console.

## Further reading

- [System design primer](system-design-primer.md) — vocabulary that applies regardless of cloud.
- [Well-Architected Framework deep-dives](../05-well-architected/) — six pillars, one page each.
- AWS Well-Architected Framework whitepaper (the canonical source for the pillars).
- AWS Architecture Center.
