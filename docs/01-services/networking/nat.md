# NAT Gateway

> **One-line summary.** Managed network address translation. Lets private-subnet workloads initiate outbound internet traffic without exposing inbound. Also the line item that surprises everyone on the AWS bill.

## TL;DR

- One per AZ for high availability — a NAT Gateway is per-AZ; cross-AZ traffic from a subnet to a NAT in another AZ both pays cross-AZ transfer *and* exposes you to AZ failure on that NAT.
- Charges are **per hour** *and* **per GB processed**. The per-GB is what blows up: a busy workload can pay more for NAT than for the EC2 instances behind it.
- Cut NAT cost by using **VPC Endpoints** for AWS service traffic (S3 Gateway endpoint is free; Interface endpoints are usually cheaper than NAT for meaningful traffic).
- **NAT instances** (EC2-based NAT) still work and are dramatically cheaper for low-throughput workloads, but you operate the EC2. NAT Gateway is the default for production.
- Public NAT vs **private NAT** — most NAT Gateways are public (egress to the internet). Private NAT Gateways exist for cross-VPC NAT use cases without internet exposure.

## When to use it

- Workloads in private subnets that need to make outbound calls to the internet (package downloads, third-party API calls, OAuth flows to external IdPs).
- Default egress for ECS / EKS / Lambda-in-VPC workloads talking to anything outside AWS.

## When NOT to use it

- Workloads that only need to reach AWS services — use **VPC Endpoints** instead (cheaper and traffic stays on the AWS network).
- Public-subnet workloads — they can use the IGW directly with their own public IP; NAT is for the private side.
- Very-low-volume, dev/test workloads where the hourly cost dominates — a NAT instance (small EC2 with iptables-NAT) is much cheaper if you're OK operating it.

## Key concepts

**NAT Gateway** — fully managed, highly available within one AZ, auto-scales to ~45 Gbps. AWS handles patching and the underlying instance.

**Per-AZ HA.** A single NAT Gateway is HA within its AZ (managed under the hood), but it's *not* multi-AZ — it lives in one AZ. The standard pattern: **one NAT Gateway per AZ that has private subnets**, with each AZ's private subnets routing to their local NAT Gateway. If you skip this and route all AZs through one NAT, an AZ failure on the NAT's AZ takes egress down for everyone *and* you pay cross-AZ transfer in the meantime.

**Public NAT Gateway** — has a public IP (Elastic IP), translates private addresses to that EIP for outbound internet traffic. Inbound is not supported (it's NAT, not a load balancer).

**Private NAT Gateway** — translates private addresses to another private address. Used for cross-VPC NAT scenarios (overlapping CIDRs in two VPCs that need to talk via a third VPC, common in M&A scenarios) and on-prem connectivity patterns.

**NAT Instance** — a self-managed EC2 instance configured to forward and SNAT traffic. Cheaper at low scale, you operate it (patching, sizing, HA), the throughput is the instance's network bandwidth.

**Bandwidth.** NAT Gateway scales to ~45 Gbps automatically. For sustained high-bandwidth egress, consider whether NAT is even the right architecture (often the traffic could land directly via PrivateLink, VPC Endpoints, or an IGW).

**Source IP address selection.** Outbound traffic uses the NAT Gateway's EIP. Some third parties allow-list IPs; multiple NAT Gateways means multiple EIPs to share.

## Pricing model

- **Per-hour** charge per NAT Gateway (per-AZ deployment means multiplying by the AZ count).
- **Per-GB processed** for data through the gateway (in *and* out — both directions count).
- **Data transfer out to internet** at standard internet egress rates (separate from the NAT processing fee).
- **EIPs** — free while attached; billed when detached.

The per-GB processed fee is meaningful: at typical AWS rates and a busy workload, NAT data processing can easily exceed the rest of the VPC bill. **Two of the biggest cost optimizations on AWS bills involve NAT**:

1. Use **VPC Endpoints** (Gateway for S3/DynamoDB are free; Interface endpoints for most other services) so AWS-service traffic doesn't traverse NAT.
2. **Consolidate egress** through one well-placed NAT per AZ; don't run unnecessary parallel paths.

## Quotas & limits

- **NAT Gateways per AZ**: 5 default (raisable).
- **Bandwidth per NAT Gateway**: ~45 Gbps.
- **EIPs per Region**: 5 default (raisable).
- **Concurrent connections per NAT Gateway**: 55,000 per unique destination IP+port combination — practically high for normal workloads, but a poorly-distributed flow against a single backend hostname can hit this.

## Common pitfalls

- **One NAT Gateway for the whole VPC.** Single point of failure on that AZ, plus cross-AZ data transfer charges from the other AZs' private subnets. Use per-AZ NAT.
- **NAT for AWS-service traffic.** S3 PUT/GET, DynamoDB calls, CloudWatch Logs ingestion all hitting NAT is pure waste. Add a Gateway endpoint for S3 and DynamoDB (free); Interface endpoints for the high-traffic services.
- **Container image pulls through NAT.** ECR pull-through cache + Interface endpoint for ECR saves a fortune in NAT-processed GBs on a Fargate fleet that scales out frequently.
- **Forgetting EIPs on detached NATs.** EIPs charge while detached. Delete EIPs you're not using.
- **NAT Gateway as a connectivity tool.** It's egress NAT, not load balancing or inbound proxy. Inbound from the internet → use ALB/NLB or API Gateway.
- **Allow-listing one NAT's IP downstream.** If you later need a second NAT for scale or HA, the downstream allow-list breaks. Allow-list a small pool of EIPs or use a higher-level identity mechanism (signed requests, mTLS).
- **Routing the wrong CIDR to NAT.** Sometimes a workload's "outbound to the internet" is actually traffic that should go cross-Region via Transit Gateway or to an on-prem network via Direct Connect — accidentally NAT'd, it bypasses your private path.

## Pairs well with

- [VPC](vpc.md), [VPC Endpoints](vpc-endpoints.md) — the right way to reduce NAT traffic.
- [Transit Gateway](transit-gateway.md) — central NAT serving many VPCs.
- **AWS Network Firewall** — sits between subnets and NAT for outbound traffic filtering.

## Further reading

- [NAT Gateway documentation](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-nat-gateway.html).
- [NAT Gateway pricing](https://aws.amazon.com/vpc/pricing/).
- [NAT Gateway use cases](https://docs.aws.amazon.com/vpc/latest/userguide/nat-gateway-scenarios.html).
- [Cost optimization for NAT Gateway](https://aws.amazon.com/blogs/networking-and-content-delivery/cost-optimize-traffic-flow-with-aws-private-nat-gateway/).
