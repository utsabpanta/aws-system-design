# Transit Gateway

> **One-line summary.** Regional network hub that interconnects many VPCs, on-prem networks (via VPN / Direct Connect), and other Regions. Replaces N×N VPC peering with a hub-and-spoke.

## TL;DR

- The right answer for "we have more than ~5 VPCs that need to talk to each other and/or to on-prem." Above that, VPC peering becomes unmanageable.
- One Transit Gateway per Region, sharable across accounts via **AWS Resource Access Manager (RAM)**. Attach VPCs, VPN tunnels, Direct Connect gateways, and other TGWs (for cross-Region).
- **Route tables** on the TGW let you implement segmentation (a "shared services" route table, a "dev → only certain spokes" table, etc.).
- Expensive line item — per-attachment-hour + per-GB processed for every flow through the TGW. Architect carefully for "what *needs* to traverse the TGW" vs "what can use Endpoints / PrivateLink instead."
- **Network Manager** is the multi-Region observability layer; **Cloud WAN** is the higher-level abstraction for multi-Region, multi-segment networks (managed evolution of multi-TGW setups).

## When to use it

- More than a handful of VPCs across one or more accounts that need to talk to each other.
- Multi-account AWS Organizations with shared services (logging account, security account, network egress account).
- Hybrid network: connecting VPCs to on-prem via VPN tunnels or Direct Connect, with consistent routing.
- Multi-Region networks (TGW-to-TGW peering, or Cloud WAN).
- Centralizing internet egress through a "security VPC" with Network Firewall.

## When NOT to use it

- Two or three VPCs that need to talk — VPC Peering is simpler and cheaper.
- Workloads that can use **PrivateLink** instead — service-to-service over PrivateLink doesn't traverse TGW and doesn't incur TGW data processing fees.
- Workloads that only need access to AWS services — VPC Endpoints serve them; TGW is unnecessary.

## Key concepts

**Transit Gateway (TGW).** Regional resource. Each TGW has an AS number, default route tables, and a list of attachments.

**Attachments** (one TGW supports many):

- **VPC attachment** — connects a TGW to one VPC, via specific subnets (one per AZ for HA).
- **VPN attachment** — IPsec tunnels to on-prem (Site-to-Site VPN).
- **Direct Connect Gateway** — TGW connects through a Direct Connect Gateway to a DX VIF.
- **Peering attachment** — TGW-to-TGW (same- or cross-Region; cross-Region is the multi-Region story before Cloud WAN).
- **Connect attachment** — GRE tunnels for SD-WAN devices.

**Route tables.** TGW has one or more route tables. Each attachment is *associated* with one route table (decides where its traffic can go) and *propagates* its routes to one or more route tables (decides who can reach it). This split is the segmentation primitive.

Common patterns:

- **Flat** — every attachment in one route table; everyone can reach everyone. Simple, not segmented.
- **Hub-and-spoke** — spokes can reach a "shared services" attachment but not each other. Common for dev/test isolation.
- **Multi-segment** — separate route tables per environment (dev, staging, prod, shared) with controlled cross-segment routes.

**Sharing across accounts** — RAM shares the TGW with member accounts of an AWS Organization. Member accounts attach their VPCs to the shared TGW.

**Network Manager.** Multi-Region visualization, topology, and event monitoring across your TGWs. Free; turn it on.

**Cloud WAN.** A newer, higher-level construct for managed multi-Region networks. Uses TGWs underneath but exposes a "core network" and "segments" concept that's easier to manage at scale. Right when you'd otherwise build many TGWs with peering attachments.

**Appliance Mode.** For middlebox attachments (firewalls, NVAs) where the same flow's request and response must traverse the same appliance — set Appliance Mode on the VPC attachment.

## Pricing model

- **Attachment-hour** per attachment (VPC, VPN, DX, peering, Connect). Each AZ a VPC attachment touches counts as one attachment from a billing standpoint in most pricing models — verify the latest.
- **Per-GB processed** through the TGW. The dominant cost for chatty environments. Cross-AZ data transfer within the VPC isn't TGW-processed (it's not crossing the TGW), but anything that does cross the TGW is metered.
- **Cross-Region peering** — billed on each side as data transfer.
- **Cloud WAN** has its own pricing model — generally similar shape (attachment + per-GB) with management overhead built in.

The number that often shocks teams: a chatty service mesh across many VPCs can pay more in TGW data processing than in EC2. Use **PrivateLink** for high-volume service-to-service calls; reserve TGW for genuinely VPC-spanning traffic.

## Quotas & limits

- **TGWs per account per Region**: 5 default (raisable).
- **Attachments per TGW**: 5,000 default.
- **Route tables per TGW**: 20 default (raisable).
- **Routes per TGW route table**: 10,000.
- **Cross-Region peering attachments per TGW**: limited; check current docs.
- **Bandwidth** — high (multi-Gbps aggregate); per-VPC attachment has a soft limit around 50 Gbps that can be raised.

## Common pitfalls

- **Flat route table for everything.** "Everyone can talk to everyone" sounds simple but means a compromise in one VPC reaches all the others. Segment route tables by environment / security boundary.
- **All inter-service traffic via TGW.** TGW per-GB charges add up. For service-to-service across accounts, **PrivateLink** is usually cheaper and tighter-scoped.
- **Single AZ attachment.** A VPC attachment is to a set of subnets — one per AZ for HA. Otherwise an AZ failure on the chosen subnet's AZ takes the attachment down.
- **Forgetting Appliance Mode for NVAs.** Without it, asymmetric routing breaks stateful firewalls. Always enable Appliance Mode on VPC attachments that funnel through middleboxes.
- **Mixing TGW and peering for the same path.** Confusing routing, hard to reason about. Pick one inter-VPC mechanism per environment.
- **No Network Manager.** When something breaks at the inter-Region or multi-attachment level, you need topology and events. Network Manager is free; turn it on.
- **Cloud WAN vs many TGWs decision deferred too long.** Once you have 5+ TGWs peered together, Cloud WAN is usually the cleaner home. Evaluate early — migration is awkward.
- **Centralized internet egress without bandwidth planning.** A "security VPC" with one TGW attachment for all spokes' internet egress concentrates traffic — make sure the TGW attachment and the egress VPC's NAT / Network Firewall can handle it.

## Pairs well with

- [VPC](vpc.md), [VPC Endpoints](vpc-endpoints.md) — what TGW connects.
- [Direct Connect](direct-connect.md), [VPN](vpn.md) — hybrid connectivity attachments.
- **AWS Network Firewall** — centralized inspection in a security VPC.
- **AWS RAM** — share TGW across accounts.
- **AWS Network Manager / Cloud WAN** — multi-Region observability and orchestration.

## Pairs well with these repo pages

- `docs/04-reference-architectures/multi-account-organization.md` (forthcoming).
- `docs/04-reference-architectures/hybrid-on-prem-vpn.md` (forthcoming).

## Further reading

- [AWS Transit Gateway documentation](https://docs.aws.amazon.com/vpc/latest/tgw/).
- [TGW best practices](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-best-design-practices.html).
- [AWS Cloud WAN](https://docs.aws.amazon.com/network-manager/latest/cloudwan/what-is-cloudwan.html).
- ["Building a Scalable and Secure Multi-VPC AWS Network Infrastructure" whitepaper](https://docs.aws.amazon.com/whitepapers/latest/building-scalable-secure-multi-vpc-network-infrastructure/welcome.html).
