# Outposts

> **One-line summary.** AWS hardware (a rack or a server) installed in your data center, edge facility, or co-lo. Same APIs as AWS Regions, but the compute and storage are physically yours.

## TL;DR

- Two form factors: **Outposts racks** (industry-standard 42U racks fully populated with AWS-designed hardware) and **Outposts servers** (1U / 2U servers for smaller footprints — branch offices, factories, retail stores).
- Run **EC2, EBS, S3 on Outposts, ECS, EKS, RDS, EMR, ElastiCache, ELB, App Mesh, MSK** locally on the Outposts. Same SDK / IaC as a Region.
- Connects to a "parent Region" via Direct Connect or VPN; the parent Region hosts the management plane.
- Right for **data residency** ("our data must stay in this building"), **low-latency on-prem integration** ("our manufacturing line needs single-digit ms to the controller"), or **on-prem workloads that benefit from AWS APIs**.
- Not for the general "cloud is too expensive, let's run on-prem" case — Outposts hardware is fully managed, but you're paying for AWS-grade infrastructure on-site.

## When to use it

- Data residency / sovereignty requirements that block public Region use.
- Low-latency integration with on-prem systems (factory floor, financial trading, gaming server colos).
- Existing on-prem workloads that need AWS API compatibility for a gradual migration.
- Branch / retail / remote locations that need local compute with cloud management (servers form factor).
- Compliance regimes where physical control of hardware matters.

## When NOT to use it

- Pure cloud workloads — use AWS Regions; Outposts is for cases where on-site placement is the requirement.
- Tiny / single-server needs — Outposts servers exist for these, but at fairly substantial commitments.
- Workloads with full data-center elasticity needs — Outposts capacity is fixed once installed.

## Key concepts

### Outposts racks

- Standard 42U racks, fully populated with AWS-designed compute, storage, and network gear.
- Installed in your data center / co-lo.
- Capacity scales by ordering more rack units.
- Connection to the parent Region via two redundant Direct Connect links or VPN.

### Outposts servers

- **1U or 2U industry-standard servers** for smaller deployments (a few EC2 instances, S3 on Outposts).
- Power-only requirements (compared to rack); easier physical install.
- Right for branch offices, retail stores, factory floors, remote sites.

### Services on Outposts

A subset of AWS services run *on* Outposts hardware locally:

- **EC2** (specific instance types).
- **EBS** local volumes.
- **S3 on Outposts** — local S3 API endpoint backed by Outposts disks.
- **ECS, EKS** — container orchestration locally.
- **RDS, ElastiCache, EMR** — managed services on-rack.
- **ELB** (ALB / NLB).
- **App Mesh, MSK**, etc. (varies; check current docs).

Some services run remotely in the parent Region but are accessible from Outposts (CloudWatch, IAM, KMS).

### Local gateway

On-prem path for traffic from Outposts to your local network. The "edge gateway" of the Outposts.

### Service link

Encrypted connection from Outposts to the parent Region for management-plane traffic.

### Networking

- **VPC extends from the parent Region** to Outposts subnets — the same VPC spans cloud and Outposts.
- Cross-Region peering / Transit Gateway integration for connecting Outposts in different Regions.

### Local resilience

- Single-rack Outposts is a single point of failure for the hardware. **Multi-rack Outposts** with multiple racks for HA.
- Workloads should still be designed for failure (Multi-AZ patterns don't apply on a single rack — AWS Outposts isn't multi-AZ within itself; you can design across multiple Outposts).

### Outposts ordering / lifecycle

- Order through AWS console.
- AWS ships, schedules installation, manages hardware lifecycle (patches, replacements).
- Outposts has a 3-year subscription model (with payment options).

## Pricing model

- **Subscription** — 3-year terms (all-upfront / partial upfront / no upfront pricing options).
- **EC2 / EBS / S3 / managed services** on Outposts have separate per-hour pricing (similar shape to Region prices but Outposts-specific).
- **Service link** data transfer billed.

Outposts is a meaningful commitment — multi-year subscription, dedicated hardware on-site. Plan capacity carefully.

## Quotas & limits

- **Outposts per account per Region**: 100 default (raisable).
- **Rack capacity**: depends on configuration ordered.
- **Service availability on Outposts**: subset of AWS services; check the current supported list.
- **Number of racks per Outpost site**: configurable.

## Common pitfalls

- **Outposts to dodge cloud cost.** The math rarely supports this — Outposts is AWS-grade infrastructure with on-site placement, not a cheap alternative.
- **Single rack used as production HA.** A single rack is a single failure domain. Multi-rack or multi-Outposts for HA.
- **No bandwidth planning for service link.** Outposts → parent Region is required for management; under-provisioned link causes operational pain.
- **Forgetting workloads that *don't* run on Outposts.** Not every AWS service is available on Outposts; verify the supported service list before architecting.
- **Treating Outposts as offline-capable.** Most Outposts services require some connectivity to the parent Region; long disconnects degrade functionality.
- **Outposts servers in places with no power / cooling planning.** They draw real power; verify the host environment.
- **Subscription mismatch.** 3-year subscriptions are long; ensure capacity is right-sized for actual usage growth.

## Pairs well with

- [Direct Connect](../networking/direct-connect.md) — service link transport.
- [VPC](../networking/vpc.md) — VPC extends to Outposts subnets.
- [Local Zones](local-zones.md), [Wavelength](wavelength.md) — adjacent edge options if you don't need on-prem hardware.
- [EC2](../compute/ec2.md), [EKS](../compute/eks.md), [ECS](../compute/ecs.md) — compute on Outposts.
- [S3](../storage/s3.md) — "S3 on Outposts" local API.

## Pairs well with these repo pages

- [Local Zones](local-zones.md), [Wavelength](wavelength.md), [Direct Connect](../networking/direct-connect.md).
- `docs/04-reference-architectures/hybrid-on-prem-vpn.md` (forthcoming).

## Further reading

- [AWS Outposts documentation](https://docs.aws.amazon.com/outposts/).
- [Services on Outposts](https://docs.aws.amazon.com/outposts/latest/userguide/what-is-outposts.html#services-on-outposts).
- [Outposts rack vs servers](https://aws.amazon.com/outposts/rack/).
- [Outposts pricing](https://aws.amazon.com/outposts/pricing/).
- [Multi-Outposts resiliency](https://docs.aws.amazon.com/outposts/latest/userguide/disaster-recovery-resiliency.html).
