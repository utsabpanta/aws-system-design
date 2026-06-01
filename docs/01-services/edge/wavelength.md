# Wavelength

> **One-line summary.** AWS compute and storage embedded inside telco 5G networks. Workloads run at the edge of the mobile carrier's network for ultra-low-latency to 5G devices.

## TL;DR

- 30+ Wavelength Zones globally as of 2026, embedded in major 5G operator networks (Verizon, KDDI, SK Telecom, Vodafone, Bell, etc.).
- Right for **5G mobile workloads** that need sub-10ms latency to devices on the carrier's network — interactive AR/VR, real-time gaming on mobile, autonomous-vehicle telemetry, live broadcast production, industrial IoT over 5G.
- Each Wavelength Zone is parented to an AWS Region. Subset of services available locally (EC2, EBS, ECS, EKS, ECR, VPC primitives).
- Traffic from 5G devices stays on the carrier's network, hitting the Wavelength Zone without traversing the public internet — that's the latency win.
- A niche product — most workloads don't have a 5G-mobile-end-user latency requirement; for the workloads that do, nothing else fits.

## When to use it

- **Real-time mobile gaming** where 5G phones / tablets are the clients.
- **AR / VR** experiences over 5G with strict latency budgets (sub-20ms total round-trip including device + network + compute).
- **Autonomous vehicles** or fleet telemetry over 5G needing local processing.
- **Live media production** where 5G cameras / mics feed compute at the edge for real-time processing.
- **Industrial IoT** over private 5G with carrier integration.

## When NOT to use it

- Non-5G workloads — Local Zones serve metro latency without the 5G dependency.
- Global workloads — Wavelength is operator-and-zone-specific; users on a different carrier don't benefit.
- Workloads that don't need the carrier-network proximity — regular Regions or Local Zones are cheaper and have broader service availability.

## Key concepts

### Wavelength Zone

Compute and storage capacity embedded in a telecom carrier's data center. Each Zone:

- Belongs to a specific **carrier** (Verizon in the US, KDDI in Japan, SK Telecom in Korea, Vodafone in Europe, Bell in Canada, etc.).
- Parents to a specific AWS Region.
- Identified as `<parent-region>-wl1-<carrier>-<location>` (e.g., `us-east-1-wl1-bos-wlz-1`).

### Carrier IP

Wavelength instances can have a **carrier IP** — addressable from devices on the carrier's 5G network without traversing the internet. The latency win comes from this routing path.

### VPC integration

- Wavelength Zones are accessed via Wavelength-specific subnets in a VPC.
- **Carrier Gateway** routes carrier-IP traffic.
- **Service link** to the parent Region for management plane and AWS-service access.

### Supported services

Subset focused on compute and storage:

- **EC2** (specific instance types).
- **EBS**.
- **ECS, EKS**.
- **ECR pull-through caching**.
- **VPC primitives** (subnets, route tables, Carrier Gateway, NAT, IGW).

Other AWS services route to the parent Region.

### Mobile device → Wavelength data path

5G device → carrier 5G network → Wavelength Zone (compute) → optional path back to parent Region for further processing. The first leg stays on the carrier's network.

### Enabling

Opt-in per account per Zone, similar to Local Zones.

## Pricing model

- **Compute / EBS** at Wavelength-specific rates (premium vs parent Region).
- **Wavelength Zone ↔ parent Region** data transfer per GB.
- **Carrier-IP traffic** — costs depend on carrier (some carriers do not charge data transfer over their own 5G network into Wavelength).

Wavelength has its own pricing nuances per carrier; check the per-Zone pricing page.

## Quotas & limits

- **vCPU quotas** per Wavelength Zone per account.
- **Service availability** — narrower than Regions; verify supported services per Zone.
- **Wavelength Zone count**: 30+ globally as of 2026.
- **Carrier IP allocation**: bounded; managed by the Carrier Gateway.

## Common pitfalls

- **Wavelength for non-5G workloads.** The whole point is the 5G carrier integration. Non-5G traffic doesn't benefit from Wavelength's path.
- **Forgetting to opt in.** Wavelength Zones aren't enabled in your account by default.
- **No carrier-IP plan.** Workloads need to know which devices reach them via carrier IP (the 5G-direct path) vs the internet (slower path through parent Region).
- **Single Wavelength Zone for HA.** A single Zone is one failure domain. For HA in a metro, design for multi-Zone or pair with Local Zones / parent Region failover.
- **Picking a Wavelength Zone in the wrong carrier.** A Verizon Zone helps Verizon 5G subscribers, not AT&T's. Workload reach matches the carrier footprint.
- **Underestimating service link bandwidth.** Wavelength → parent Region traffic for management or service calls; oversaturate the link and operations suffer.
- **Service availability assumptions.** Many AWS services don't run in Wavelength Zones; they route to the parent Region — adds latency for what was supposed to be a low-latency workload.

## Pairs well with

- [Local Zones](local-zones.md) — alternative for metro latency without 5G dependency.
- [Outposts](outposts.md) — when on-prem hardware control is the requirement.
- [VPC](../networking/vpc.md) — extends to Wavelength subnets.
- [EC2](../compute/ec2.md), [ECS](../compute/ecs.md), [EKS](../compute/eks.md) — workload hosts.
- **AWS IoT Core** — adjacent for IoT-device-to-cloud paths, though not the same shape.

## Pairs well with these repo pages

- [Local Zones](local-zones.md), [Outposts](outposts.md), [IoT Core](iot-core.md).

## Further reading

- [AWS Wavelength documentation](https://docs.aws.amazon.com/wavelength/).
- [Wavelength Zones list](https://aws.amazon.com/wavelength/locations/).
- [Carrier Gateway and carrier IPs](https://docs.aws.amazon.com/wavelength/latest/developerguide/wavelength-carrier-gateways.html).
- [AWS Wavelength pricing](https://aws.amazon.com/wavelength/pricing/).
- [Comparing AWS edge options](https://aws.amazon.com/about-aws/global-infrastructure/edge-locations/).
