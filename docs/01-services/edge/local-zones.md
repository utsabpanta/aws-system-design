# Local Zones

> **One-line summary.** AWS-managed infrastructure in specific metro areas that aren't dedicated AWS Regions — gives you single-digit-millisecond latency to local users for compute, storage, and database workloads.

## TL;DR

- 33+ Local Zones globally as of 2026 (Los Angeles, Boston, Houston, Atlanta, Miami, NYC, Lagos, Lima, Querétaro, and more).
- Each Local Zone is parented to an AWS Region (`us-west-2-lax-1a` is parented to `us-west-2`). Management plane lives in the parent Region; compute / storage / databases run locally.
- Subset of AWS services available locally: **EC2, EBS, FSx, RDS, ElastiCache, ECS, EKS, ALB, NLB, ECR pull-through caching, S3 with caveats**.
- Right for **latency-sensitive workloads in specific metros** — game studios, real-time finance, AR/VR, live media production, on-the-edge ML inference.
- Not for "low-latency for everyone globally" — that's CloudFront / Global Accelerator.

## When to use it

- Real-time apps where 10ms-class latency to specific metro users matters (game studios, video editing, finance).
- Workloads serving users in metros far from the nearest Region.
- Hybrid setups where the Local Zone is "close enough to" on-prem infrastructure for low-latency integration.
- AR/VR / interactive streaming with strict latency requirements.

## When NOT to use it

- Workloads where users are globally distributed — CloudFront at edge POPs is dramatically more present (600+ POPs).
- Workloads that don't need low-latency to a specific metro — regular Regions are cheaper.
- Heavy data-locality requirements that need on-prem hardware — use **Outposts**.
- Workloads needing AWS services not available in Local Zones (most services are NOT in Local Zones; verify the list).

## Key concepts

### Local Zone naming

`<parent-region>-<location-code>-<az-id>`, e.g., `us-west-2-lax-1a` (Los Angeles, parented to `us-west-2`).

### Parent Region

Each Local Zone has a parent Region (`us-west-2` for `us-west-2-lax-1a`). Management plane, IAM, KMS, and many AWS services run in the parent Region. The Local Zone provides local compute / storage capacity.

### Subnets in Local Zones

VPCs from the parent Region extend into Local Zones via Local-Zone-specific subnets. Standard VPC routing — Internet Gateway, NAT, route tables — works.

### Supported services

A subset of AWS services run *in* Local Zones (varies by Zone):

- **EC2** (specific instance types).
- **EBS** (specific volume types).
- **FSx for ONTAP / OpenZFS / Windows / Lustre** (varies).
- **RDS** (specific engines).
- **ElastiCache**.
- **ECS, EKS**.
- **ALB, NLB**.

Not in Local Zones: most managed analytics / ML services, fully managed Bedrock, etc. — those route to the parent Region.

### S3

- **S3 in Local Zones** — newer offering; S3 buckets resident in specific Local Zones for very-low-latency object access.
- For most workloads, S3 still lives in the parent Region.

### Enabling a Local Zone

Opt in via the AWS console / API per account per Zone — Local Zones aren't enabled by default in your account.

### Data transfer

- **Within the Local Zone** — free.
- **Local Zone ↔ parent Region** — billed per GB (separate from inter-AZ).
- **Local Zone to internet** — egress at standard internet rates.

### Direct Connect / VPN

- Local Zones support Direct Connect via specific DX locations near each Local Zone.
- Useful for very-low-latency on-prem connectivity in that metro.

## Pricing model

- **Compute / storage** at Local Zone rates (typically slightly higher than parent Region).
- **Data transfer Local Zone ↔ parent Region** — per GB.
- **Internet egress** at standard rates.

Expect a modest premium vs equivalent parent-Region resources.

## Quotas & limits

- **vCPU quotas** per Local Zone (separate from parent Region).
- **Instance types** — subset of what's in the parent Region.
- **Service availability** — varies per Zone; check the service-by-zone matrix.
- **Number of Local Zones globally**: 33+ as of 2026 (expanding).

## Common pitfalls

- **Putting a service in a Local Zone when it's not available there.** Verify the supported-services matrix per Zone before architecting.
- **Forgetting the parent Region dependency.** Management calls and many service endpoints route to the parent Region. If the parent Region has issues, your Local Zone is partially affected.
- **No HA across Local Zones.** A single Local Zone is one AZ-equivalent. For HA, pair multiple Zones or use Local Zone + parent Region multi-AZ.
- **Local Zones used for "global latency."** They serve specific metros, not the globe. CloudFront / Global Accelerator are for global routing.
- **No Direct Connect plan for ultra-low-latency on-prem hybrid.** Standard internet to a Local Zone is fast; Direct Connect can be faster + more reliable for high-volume integration.
- **Underestimating cross-Local-Zone-to-parent-Region data transfer cost.** A chatty service that fetches from RDS in the parent Region on every request pays cross-Zone transfer per request.

## Pairs well with

- [VPC](../networking/vpc.md) — extends from parent Region to Local Zone subnets.
- [Direct Connect](../networking/direct-connect.md) — ultra-low-latency on-prem connectivity to a Local Zone.
- [EC2](../compute/ec2.md), [EBS](../storage/ebs.md), [RDS](../database/rds.md), [ElastiCache](../database/elasticache.md), [ECS](../compute/ecs.md), [EKS](../compute/eks.md) — supported services.
- [Wavelength](wavelength.md) — adjacent option for 5G-edge use cases.
- [Outposts](outposts.md) — when you need on-prem hardware control instead of metro-edge.

## Pairs well with these repo pages

- [Wavelength](wavelength.md), [Outposts](outposts.md), [CloudFront](../networking/cloudfront.md).

## Further reading

- [AWS Local Zones overview](https://aws.amazon.com/about-aws/global-infrastructure/localzones/).
- [Local Zones FAQs](https://aws.amazon.com/about-aws/global-infrastructure/localzones/faqs/).
- [Local Zones service availability](https://aws.amazon.com/about-aws/global-infrastructure/localzones/features/).
- [Extending VPCs to Local Zones](https://docs.aws.amazon.com/vpc/latest/userguide/Extend_VPCs.html).
- [S3 in Local Zones](https://docs.aws.amazon.com/AmazonS3/latest/userguide/local-zones-overview.html).
