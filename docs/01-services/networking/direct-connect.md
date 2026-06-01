# Direct Connect

> **One-line summary.** Dedicated, private fiber from your on-prem network to AWS. Predictable bandwidth, predictable latency, no public-internet path.

## TL;DR

- The right answer for "we move a lot of data between on-prem and AWS, the internet path isn't predictable enough, and/or we don't want this traffic on the public internet."
- Throughput options: **Dedicated Connection** (1, 10, 100, 400 Gbps physical port at a Direct Connect location) or **Hosted Connection** (50 Mbps – 25 Gbps from a Direct Connect Partner).
- Connect into AWS via **Virtual Interfaces (VIFs)**: **Private VIF** (to a VPC), **Public VIF** (to AWS public services like S3 / DynamoDB without internet routing), **Transit VIF** (to a Direct Connect Gateway, fronting Transit Gateway / many VPCs).
- **MACsec** for line-rate Layer-2 encryption on 10/100/400 Gbps connections — encrypted physical link, no IPsec overhead.
- A single Direct Connect is *not* HA. Use **two connections in two different DX locations** with BGP failover for production hybrid networks. AWS's **Direct Connect SLA** only applies to 99.99% configurations that meet the dual-location requirement.

## When to use it

- High-volume data transfer between on-prem and AWS (>10 Gbps sustained, or terabytes per day).
- Predictable latency requirements (financial trading, real-time control systems, latency-sensitive replication).
- Compliance / contractual requirements that traffic not traverse the public internet.
- Hybrid AD, SAN replication, video / media production pipelines.
- Multi-Region hybrid via Direct Connect Gateway + Transit Gateway.

## When NOT to use it

- Low-volume hybrid (Site-to-Site VPN over the internet is fine and dramatically cheaper).
- New / unvalidated workloads (start on VPN; move to Direct Connect when scale justifies it).
- Workloads that talk to AWS public services in a single Region with modest traffic — internet egress is often cheaper than DX after you factor port hours and provider costs.

## Key concepts

**Direct Connect location.** A physical AWS-operated colocation facility (Equinix, CoreSite, Digital Realty, etc.) where AWS terminates fiber. You either co-locate equipment there or contract with a Direct Connect Partner to extend connectivity to your own data center.

**Dedicated Connection.** Your own physical port (1, 10, 100, or 400 Gbps). Provisioning takes weeks (physical cross-connect at the colo, BGP setup, testing).

**Hosted Connection.** Partner provides a virtual circuit at 50 Mbps – 25 Gbps. Faster to provision, smaller throughput tiers, often cheaper at the low end.

**Virtual Interface (VIF).** Logical interface on top of the connection:

- **Private VIF** — BGP peering into one VPC's Virtual Private Gateway (VGW), or into a Direct Connect Gateway that fans out to many VGWs.
- **Public VIF** — BGP peering into AWS's public range; reach S3 / DynamoDB / public service endpoints across all Regions without internet routing. AWS advertises public prefixes to you; you advertise yours.
- **Transit VIF** — peers to a Direct Connect Gateway that's associated with one or more Transit Gateways. The standard pattern for hybrid with many VPCs.

**Direct Connect Gateway (DXGW).** A global resource (despite the name, it's not regional). Lets one Direct Connect connection reach VPCs / TGWs in any Region in the same AWS partition. Decouples the physical location of your DX from the Region your VPCs live in.

**MACsec.** IEEE 802.1AE Layer-2 encryption between your router and the AWS router at the DX location. Available on 10/100/400 Gbps connections (and select hosted variants). Cheaper and lower-overhead than running IPsec on top of DX.

**SiteLink.** Lets two DX locations talk to each other through the AWS backbone — useful when your data centers connect to AWS at different colos and you want them to reach each other over the AWS backbone rather than your own WAN.

**BGP.** All routing is BGP. You set up BGP sessions over the VIFs; AWS advertises VPC / TGW / public ranges; you advertise on-prem ranges. BFD (Bidirectional Forwarding Detection) for fast failure detection between redundant connections.

## Pricing model

- **Port-hour** — flat hourly fee per physical port (heavily tier-dependent: a 100 Gbps port costs many times a 1 Gbps port).
- **Data transfer out** — **dramatically cheaper than internet egress** (often a quarter or less). Data transfer *in* is free.
- **Hosted Connections** — partners bill you for the virtual circuit plus their own fees; AWS bills you for the data transfer.
- **MACsec** — typically included on supported ports; no separate AWS surcharge.
- **DX Gateway** — free.
- **SiteLink** — adds a fee per attachment + per-GB processed.

The data-transfer-out savings vs internet egress is the main long-term economic argument. The port-hour and provider costs are real, so DX only beats VPN for workloads with sustained throughput.

## Quotas & limits

- **Connections per Region per account**: 10 default (raisable).
- **VIFs per connection**: 50.
- **Direct Connect Gateways per account**: 200.
- **VPCs / TGWs associated with one DXGW**: in the high tens; multi-Region supported.
- **BGP ASN restrictions**: 64,512–65,534 (private 16-bit), 4,200,000,000–4,294,967,294 (private 32-bit), or your public ASN.

## Common pitfalls

- **Single Direct Connect for production.** No SLA, no HA. A fiber cut takes you down. Use two connections at two different DX locations (different metro is even better) with BGP failover.
- **VPN as DX backup, in the same colo.** A failure on the fiber to that colo takes both down. Backup VPN should terminate at a different geographic AWS gateway.
- **Public VIF instead of Interface Endpoints.** Public VIF gives you private routing to public services across all Regions, but for service-by-service access from a single VPC, Interface endpoints are often simpler and have IAM-style policies.
- **No BFD.** BGP default detection times are tens of seconds — too slow for production. Enable BFD on both ends for sub-second detection.
- **MTU mismatches.** AWS supports jumbo frames (9001 MTU) on private VIFs; misconfiguring intermediate equipment causes mysterious throughput drops.
- **Over-provisioned dedicated connections.** A 10 Gbps port is expensive 24/7. If usage is < ~3 Gbps average, a hosted connection is usually better.
- **Routing leaks via Public VIF.** Public VIF advertises your prefixes to AWS *and* AWS advertises its public prefixes to you. Filter carefully.
- **Forgetting LOA-CFA paperwork.** Provisioning a dedicated connection requires submitting a Letter of Authorization (LOA) to the colo. Plan for weeks.

## Pairs well with

- [Transit Gateway](transit-gateway.md) — hybrid network with many VPCs.
- [VPN](vpn.md) — backup path for DX.
- **AWS Direct Connect Resiliency Toolkit** — guided wizard for HA configurations (dual locations).
- **CloudWatch DX metrics** — `ConnectionBpsEgress/Ingress`, `ConnectionPpsEgress/Ingress`, `ConnectionLightLevelTx/Rx` (optical levels on the link).

## Pairs well with these repo pages

- [VPN](vpn.md) — the cheaper hybrid alternative for low-volume workloads.
- `docs/04-reference-architectures/hybrid-on-prem-vpn.md` (forthcoming) — hybrid network reference architectures.

## Further reading

- [AWS Direct Connect documentation](https://docs.aws.amazon.com/directconnect/).
- [Direct Connect Resiliency Toolkit](https://docs.aws.amazon.com/directconnect/latest/UserGuide/resiliency_toolkit.html).
- [Direct Connect locations](https://aws.amazon.com/directconnect/locations/).
- [MACsec on Direct Connect](https://docs.aws.amazon.com/directconnect/latest/UserGuide/MACsec.html).
- [Direct Connect SLA](https://aws.amazon.com/directconnect/sla/).
