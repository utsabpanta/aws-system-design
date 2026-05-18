# Network Firewall

> **One-line summary.** Managed L3–L7 firewall at the VPC level. Stateful traffic inspection, IDS/IPS, domain-name filtering, and TLS inspection — without you operating a virtual appliance fleet.

## TL;DR
- VPC-attached firewall service. Sits in a dedicated firewall subnet; you route VPC traffic through it via route table changes.
- **Stateful** (Suricata-compatible rules) + **stateless** rule groups. Domain-based filtering by SNI or HTTP host header. Deep packet inspection.
- The **AWS-native alternative to running Palo Alto / Check Point / Fortinet virtual firewalls on EC2** (or behind Gateway Load Balancer). Less feature-rich than the major commercial NGFWs; far simpler operationally.
- Right for centralized egress filtering ("only let workloads reach this domain allow-list"), east-west VPC segmentation, and compliance-driven inspection requirements.
- Pricing is per-endpoint-hour + per-GB processed — expensive at high throughput. Architect for what *needs* inspection vs what doesn't.

## When to use it
- **Centralized egress** through a "security VPC" with a domain-name allow-list for outbound traffic.
- **East-west segmentation** between VPCs / accounts via Transit Gateway + Network Firewall on a central inspection VPC.
- **Compliance** that requires stateful inspection / IDS at the network layer.
- Replacing self-managed firewall appliances on EC2 with an AWS-managed alternative when the commercial NGFW features aren't required.

## When NOT to use it
- Workloads where security groups + NACLs + WAF cover the threat model — Network Firewall adds significant cost.
- Public web app L7 filtering — that's **WAF**.
- Workloads requiring features only commercial NGFWs offer (specific SD-WAN integration, advanced URL filtering categories) — Gateway Load Balancer + a commercial NGFW fleet is the alternative.

## Key concepts

**Firewall.** The VPC-level resource. Associated with one VPC; deploys **firewall endpoints** in subnets you specify (one per AZ for HA).

**Firewall policy.** Top-level config — references one or more stateless and stateful **rule groups**, plus defaults for unmatched traffic.

**Stateless rule groups.** Per-packet evaluation. Match on 5-tuple (src/dst IP, port, protocol), TCP flags. Actions: pass, drop, forward to stateful engine.

**Stateful rule groups.** Connection-aware. Three flavors:
- **5-tuple stateful** — like stateless but tracks connection state.
- **Domain-list** — match outbound traffic by HTTP host header or TLS SNI. The simplest way to allow-list / deny-list domains.
- **Suricata-compatible rules** — full Suricata syntax including community rule sets (Emerging Threats, etc.). Includes IDS/IPS-style detection.

**Route table integration.** To inspect traffic, route table for the source subnets sends `0.0.0.0/0` (or whatever scope) to the firewall endpoint; the firewall endpoint then routes to the IGW / NAT / Transit Gateway. Standard inspection-VPC pattern.

**TLS inspection.** Optionally decrypt and inspect TLS traffic using certs you provide. Adds CPU cost and operational considerations (cert distribution, exclusion lists for sensitive flows).

**Logging.** Alert logs, flow logs, TLS logs — to CloudWatch / S3 / Kinesis.

**Suricata rule sources.** Bring your own Suricata-compatible rule sets (Emerging Threats Open is a common starting point). Pay attention to rule update cadence and false-positive tuning.

**Firewall Manager.** Centrally manage Network Firewall policies across the Organization.

## Pricing model

- **Per-endpoint-hour** per AZ.
- **Per-GB processed** through the firewall.
- **Optional TLS inspection** — additional per-GB charges.
- **Logging** — pay the destination's ingestion (CloudWatch / S3 / Kinesis).

At high throughput, Network Firewall is meaningfully expensive. The architecture decision is **what needs inspection** — flow only the traffic that actually requires it through the firewall, not everything.

## Quotas & limits

- **Firewall policies per account per Region**: 100.
- **Rule groups per account per Region**: 100 stateless + 100 stateful.
- **Rules per stateful group**: 30,000 (capacity-bounded).
- **Throughput per firewall endpoint**: ~100 Gbps aggregate (varies); auto-scales within limits.
- **Suricata rule complexity** — bounded by per-rule-group capacity.

## Common pitfalls

- **Firewall in front of all traffic.** Inspecting traffic that doesn't need it doubles cost. Use route-table scoping to send only the relevant flows through the firewall.
- **No HA topology.** Single AZ firewall endpoint = AZ failure takes egress inspection down. Deploy endpoints in 2+ AZs and route per-AZ.
- **Reaching for it before SG/NACL/WAF.** A correct security group with deny-by-default and a WAF in front of public endpoints covers the majority of workloads. Add Network Firewall when you have a specific need it satisfies.
- **TLS inspection without thinking through cert distribution.** Endpoints don't trust your inspection cert by default — you need to distribute it to every workload that's being inspected (or break the flow).
- **Suricata rules pulled in unfiltered.** Open Emerging Threats has tens of thousands of rules; many fire constantly on benign traffic. Curate.
- **No alerting on firewall alert logs.** Logging without monitoring = no incident response. Send alert logs to a SIEM / CloudWatch Insights query that someone actually reads.
- **Single inspection VPC bottleneck.** A central security VPC with Network Firewall serving many spoke VPCs is a popular pattern; verify the firewall throughput against peak spoke traffic before committing.

## Pairs well with
- [VPC](../networking/vpc.md), [Transit Gateway](../networking/transit-gateway.md) — host topology.
- **AWS Firewall Manager** — org-wide policy.
- [WAF](waf.md) — L7 HTTP filtering at the application boundary.
- **Gateway Load Balancer** — for inserting commercial NGFW appliances; alternative pattern for the "I want NGFW features" case.

## Pairs well with these repo pages
- [WAF](waf.md), [Shield](shield.md), [Transit Gateway](../networking/transit-gateway.md).

## Further reading
- [AWS Network Firewall documentation](https://docs.aws.amazon.com/network-firewall/).
- [Centralized egress with Network Firewall](https://docs.aws.amazon.com/whitepapers/latest/building-scalable-secure-multi-vpc-network-infrastructure/centralized-egress-to-internet.html).
- [Suricata rules in Network Firewall](https://docs.aws.amazon.com/network-firewall/latest/developerguide/suricata-examples.html).
- [TLS inspection](https://docs.aws.amazon.com/network-firewall/latest/developerguide/tls-inspection.html).
