# VPC (Virtual Private Cloud)

> **One-line summary.** Your private network in AWS. CIDR-defined IP space partitioned into subnets across AZs, with route tables, security groups, NACLs, and gateways that decide who can talk to what.

## TL;DR
- Every AWS workload runs in a VPC (the "default VPC" is one too, just an opinionated starter). Region-scoped — VPCs don't cross Regions.
- Three subnet flavors that matter operationally: **public** (route to IGW), **private** (route to NAT for egress), **isolated** (no internet at all — databases, internal-only services).
- **Security groups** are stateful instance-level firewalls. **NACLs** are stateless subnet-level firewalls. Default to SGs only; touch NACLs rarely.
- Plan CIDR ranges generously (`/16` is normal; `/24` per subnet is often too small). Resizing or replumbing later is painful.
- **IPv6** is mature; **IPAM** (IP Address Manager) is the right way to govern address allocation across many VPCs and accounts.

## When to use it
- Always. Every workload lives in a VPC.

## When NOT to use it
- A few fully managed services (Lambda without VPC config, DynamoDB, S3, public-facing API Gateway) don't *require* a VPC. Adding one "for security" without a real reason adds overhead.

## Key concepts

**CIDR block.** The IPv4 range your VPC owns. Typical: `10.0.0.0/16` (65,536 addresses). Up to **5 IPv4 CIDR blocks per VPC** (you can add ranges later). **IPv6** CIDR optional and free; allocated `/56` by AWS from its pool, or BYOIP.

**Subnet.** A CIDR slice within the VPC, pinned to **one AZ**. Conventions:
- **Public** subnet — has a route table entry `0.0.0.0/0 → IGW`. Resources here can be assigned public IPs and reach the internet directly.
- **Private** subnet — `0.0.0.0/0 → NAT` (NAT Gateway or NAT instance). Resources have no public IPs; can initiate outbound, can't be reached directly from the internet.
- **Isolated** subnet — no `0.0.0.0/0` route. Used for databases and internal-only services that should never have internet access in either direction.

A typical 3-AZ production VPC has 3 public, 3 private, 3 isolated subnets — nine total.

**Route table.** Per-subnet. Decides where traffic goes. Most-specific route wins. Local route (the VPC CIDR) is always present and can't be removed.

**Internet Gateway (IGW).** The door from public subnets to the internet. One per VPC. Free.

**Egress-only IGW** — IPv6 equivalent of NAT — allows IPv6 outbound only.

**NAT Gateway.** Managed NAT for private subnets' outbound traffic. Per-AZ (deploy one per AZ for HA). Per-hour cost + per-GB processed — see [`nat.md`](nat.md) for the cost discussion.

**Security Group (SG).** Stateful, instance-level firewall. Allow rules only; default deny. SG can reference other SGs (not just CIDRs) for portable policies. Default SG in every VPC allows all internal traffic — usually a mistake to leave as-is.

**Network ACL (NACL).** Stateless, subnet-level firewall. Allow *and* deny rules, evaluated in numbered order. Default NACL allows all in/out. Use NACLs sparingly — a deny rule is sometimes useful, but most workloads should rely on SGs.

**ENI (Elastic Network Interface).** The virtual NIC. Each EC2 instance / Fargate task / Lambda-in-VPC gets one or more. SG attached to the ENI, not the host. Instance types cap ENIs and IPs per ENI.

**VPC Peering.** Layer-3 connection between two VPCs (same or cross-account, same or cross-Region). No transitive — A peered to B and B peered to C doesn't give A access to C. For more than a handful of VPCs, use **Transit Gateway** (see [`transit-gateway.md`](transit-gateway.md)).

**VPC Endpoints.** Private connectivity to AWS services without traversing the public internet. See [`vpc-endpoints.md`](vpc-endpoints.md).

**IPAM (IP Address Manager).** Govern CIDR allocation across many VPCs and accounts in an Organization. Prevents overlapping CIDRs, automates planning, integrates with the AWS Organizations account vending pattern.

**Flow Logs.** Log every accepted/rejected flow on an ENI, subnet, or whole VPC. To CloudWatch Logs or S3. Essential for security incident response.

**DHCP options set.** Custom DNS servers, NTP servers, domain name. Most VPCs use the default; large environments customize for AD integration or split-horizon DNS.

**Mirror Sessions / Traffic Mirroring.** Copy traffic from an ENI to a target for inspection. Used for IDS, packet capture, NDR products.

## Pricing model

- **VPC itself is free.**
- **IGW is free** (the routing is free; you pay for actual data transfer at standard rates).
- **NAT Gateway** — per-hour + per-GB processed (the real cost; see [`nat.md`](nat.md)).
- **VPC Endpoints** — Gateway endpoints (S3, DynamoDB) are free; Interface endpoints are per-hour + per-GB.
- **VPC Peering** — free to create; pay cross-AZ / cross-Region data transfer at standard rates.
- **Transit Gateway** — attachment-hour + per-GB processed.
- **IPv6** — free.
- **Flow Logs** — pay the destination's storage / ingestion costs (CloudWatch Logs / S3 ingestion).

The dominant networking cost on most bills isn't the gateway, it's **inter-AZ data transfer** between resources in your own VPC, plus **NAT Gateway egress**, plus **public internet egress**.

## Quotas & limits

- **VPCs per Region**: 5 default (raisable).
- **CIDR blocks per VPC**: 5 IPv4 + 1 IPv6 (raisable).
- **Subnets per VPC**: 200.
- **Route tables per VPC**: 200; routes per route table: 50.
- **Security groups per VPC**: 2,500 default (raisable).
- **Rules per SG**: 60 inbound + 60 outbound (combined cap 120; raisable).
- **SGs per ENI**: 5 (raisable to 16).
- **NACL rules**: 20 in + 20 out per NACL (raisable to 40 + 40).
- **Active VPC peering connections per VPC**: 50 (raisable).

## Common pitfalls

- **Too-small CIDR.** `/24` subnets fill up fast — every ENI, every Fargate task, every Lambda warm pool burns IPs. Use `/22` or larger per subnet in production VPCs.
- **Overlapping CIDRs.** Two VPCs with `10.0.0.0/16` can't peer or share a Transit Gateway route table. IPAM prevents this.
- **Default SG left wide open.** Lock it down on day one.
- **NACLs as your primary firewall.** They're stateless (you have to allow both directions and the ephemeral port range); easy to misconfigure. Use SGs for almost everything.
- **One AZ in production.** AZ failures happen. Spread subnets across 2 or 3 AZs, deploy resources accordingly.
- **No VPC Endpoints.** Every S3 / DynamoDB / SSM / Logs request from private subnets traverses NAT — paying both NAT hours *and* per-GB processed. Endpoints save money and shorten the path.
- **Manual route tables / SGs in production.** Define everything in IaC (CloudFormation/CDK/Terraform). Console drift is hard to reverse and audit.
- **No Flow Logs.** When an incident happens, no logs means no investigation. Turn them on at the VPC level.
- **Cross-AZ chatter.** Two services in different AZs chat freely → cross-AZ data transfer charges add up. Use topology-aware routing (ECS, EKS, Service Connect) where it matters.

## Pairs well with
- [NAT Gateway](nat.md), [VPC Endpoints](vpc-endpoints.md), [Transit Gateway](transit-gateway.md), [Direct Connect](direct-connect.md), [VPN](vpn.md) — the connectivity surface.
- **AWS PrivateLink** — service-to-service across accounts without public internet.
- **AWS Network Firewall** — stateful, deep-inspection firewall at the VPC level.
- **Reachability Analyzer + Network Access Analyzer** — diagnose connectivity and audit reachability against policy.

## Further reading
- [Amazon VPC documentation](https://docs.aws.amazon.com/vpc/).
- [VPC subnet design](https://docs.aws.amazon.com/vpc/latest/userguide/configure-subnets.html).
- [Amazon VPC IP Address Manager](https://docs.aws.amazon.com/vpc/latest/ipam/).
- [VPC Flow Logs](https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs.html).
- [AWS networking reference architectures](https://docs.aws.amazon.com/whitepapers/latest/building-scalable-secure-multi-vpc-network-infrastructure/welcome.html).
