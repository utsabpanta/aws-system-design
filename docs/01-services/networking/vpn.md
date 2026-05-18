# VPN (Site-to-Site & Client)

> **One-line summary.** IPsec tunnels into AWS. **Site-to-Site VPN** connects your data center / branch to a VPC; **Client VPN** is OpenVPN-based remote access for end users.

## TL;DR
- **Site-to-Site VPN** is the default hybrid-cloud connectivity for small/medium workloads — internet-based IPsec, fast to provision, dramatically cheaper than Direct Connect at modest scale.
- A Site-to-Site VPN connection always comes with **two IPsec tunnels** on different AWS hardware for HA. Configure your on-prem device for both, with BGP for failover.
- **Client VPN** is fully managed OpenVPN. Users get a `.ovpn` config; auth via mutual TLS, AD, or SAML/Okta/etc. The right choice when you'd otherwise stand up your own VPN appliance for workforce remote access.
- For high-throughput hybrid, **Direct Connect** beats VPN on bandwidth, latency, and per-GB cost. Many production hybrid setups use Direct Connect with a Site-to-Site VPN backup.
- Both VPN flavors can attach to a **Transit Gateway** for many-VPC connectivity instead of terminating on a single VPC's Virtual Private Gateway (VGW).

## When to use it

**Site-to-Site VPN:**
- Connect on-prem network to a VPC quickly without DX provisioning.
- Backup path for Direct Connect (terminating at a different AWS gateway, not the same DX location).
- Multi-site SD-WAN-style connectivity into AWS via a Transit Gateway with many VPN attachments.
- Test / dev / lab environments where DX cost is unjustified.

**Client VPN:**
- Workforce remote access to VPC-private resources (internal apps, dev environments, RDS instances).
- Contractor / vendor access scoped to specific resources.
- Bring-your-own-OpenVPN compatibility for environments that have existing OpenVPN clients.

## When NOT to use it

**Site-to-Site VPN:**
- Sustained high throughput requirements (> a few Gbps continuous) — DX beats VPN on cost and predictability above this.
- Strictly low-latency or predictable-jitter requirements — the internet path makes VPN latency variable.
- Compliance that demands traffic stay off the public internet — use DX.

**Client VPN:**
- Modern zero-trust application access — **AWS Verified Access** or third-party identity-aware proxies (Cloudflare Access, Tailscale, Zscaler) usually beat VPN for per-app access.
- Tiny user populations — Verified Access or simple bastion + SSM Session Manager may be simpler.

## Key concepts

### Site-to-Site VPN
**Customer Gateway (CGW).** AWS-side representation of your on-prem device (IP address, BGP ASN, optional pre-shared keys for IPsec).

**Virtual Private Gateway (VGW).** AWS-side termination point inside a single VPC. The "old way" of attaching VPN — replaced for multi-VPC by terminating on a Transit Gateway instead.

**Transit Gateway attachment (preferred).** Site-to-Site VPN connection terminates on a TGW, giving many VPCs access through one tunnel pair.

**Two tunnels, always.** Each Site-to-Site connection creates two IPsec tunnels on different physical AWS endpoints. Your CGW must configure both. Run BGP over both for active/active or active/passive failover.

**Routing modes:**
- **Static** — define on-prem and AWS prefixes manually. Simple, doesn't auto-recover from topology changes.
- **BGP (dynamic)** — your CGW advertises on-prem routes; AWS advertises VPC / TGW routes. The right choice for production.

**Accelerated Site-to-Site VPN.** Routes traffic via AWS edge POPs and the AWS backbone for lower-latency and more-predictable VPN performance. Worth enabling on geographic spread.

### Client VPN
**Endpoint** — the managed AWS resource. Associate it with subnets in a VPC; clients connect to those subnets' route domain.

**Auth modes:**
- **Mutual TLS** (client certs) — issue certs to users; revoke via CRL.
- **AD (Active Directory)** — AWS Directory Service or on-prem AD via Connector.
- **SAML federation** — Okta, Azure AD, Google Workspace, etc.

**Authorization rules.** Per-endpoint rules grant access to specific CIDRs based on user group. The "least privilege" mechanism for Client VPN — by default, an authenticated user has no access until a rule allows it.

**Split tunnel.** Send only AWS-bound traffic through the VPN; user's regular internet traffic stays on their local connection. Almost always the right default.

**Client connect handlers** — Lambda hook that runs on each new connection for additional authorization / posture checks.

## Pricing model

### Site-to-Site VPN
- **Per-connection-hour** for each Site-to-Site VPN connection.
- **Data transfer out to internet** at standard rates (the data still leaves AWS at internet egress prices).
- **Accelerated Site-to-Site** adds a per-hour fee and per-GB Global Accelerator pricing on top.
- When attached to a Transit Gateway, the **TGW attachment hour + per-GB processed** also applies for traffic across the TGW.

### Client VPN
- **Per-endpoint-hour per associated subnet** (a multi-AZ endpoint hits each AZ's subnet hourly).
- **Per-connected-user-hour** for each active client session.
- **Data transfer** at standard rates.

The "users × hours connected" billing means Client VPN gets expensive with a large, always-connected workforce — at scale, identity-aware app proxies (Verified Access etc.) often win.

## Quotas & limits

### Site-to-Site VPN
- **Connections per Region**: 50 per VGW, more via TGW attachments.
- **Tunnels per connection**: 2 (mandatory).
- **Per-tunnel bandwidth**: ~1.25 Gbps practical maximum (use Equal-Cost Multi-Path / ECMP across multiple VPN connections for more).
- **BGP routes advertised**: up to 100 per session.

### Client VPN
- **Endpoints per Region**: 5 (raisable).
- **Concurrent connections per endpoint**: 20,000 (raisable).
- **Authorization rules per endpoint**: 50.
- **Routes per endpoint**: 10 (raisable).

## Common pitfalls

- **Configuring only one of the two Site-to-Site tunnels.** No HA; tunnel maintenance windows take you down.
- **Static routing in production.** Topology changes don't propagate; failures don't recover. Use BGP.
- **VPN as DX backup at the same colo.** Pointless — a fiber-cut event takes both down. Backup VPN should terminate at a different AWS gateway, ideally a different geographic AWS endpoint.
- **No BGP timers tuning.** Defaults are conservative; tune holdtime and keepalive (within AWS-supported ranges) for faster failover.
- **Client VPN authorization too broad.** Authenticated user can reach the whole VPC. Scope authorization rules per CIDR / per user group.
- **Full-tunnel Client VPN by default.** Sends all user traffic through AWS, blowing through data-transfer egress costs and adding latency to non-AWS apps. Use split-tunnel unless there's a specific need.
- **Client VPN as long-term workforce access plan.** Per-user-hour pricing adds up; consider AWS Verified Access or identity-aware proxies for app-level access.
- **MTU / fragmentation.** IPsec adds overhead; default 1500 MTU paths can fragment. Set the path MTU and TCP MSS clamp correctly on the on-prem side.

## Pairs well with
- [Transit Gateway](transit-gateway.md) — the modern termination point for Site-to-Site VPN.
- [Direct Connect](direct-connect.md) — primary path; VPN as backup.
- [VPC](vpc.md) — the destination network.
- **AWS Verified Access** — modern zero-trust app access; alternative to Client VPN for many use cases.
- **AWS Directory Service / Identity Center** — auth for Client VPN.

## Pairs well with these repo pages
- [Direct Connect](direct-connect.md) — the high-end alternative.
- `docs/04-reference-architectures/hybrid-on-prem-vpn.md` (forthcoming).

## Further reading
- [Site-to-Site VPN documentation](https://docs.aws.amazon.com/vpn/latest/s2svpn/).
- [Client VPN documentation](https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/).
- [Accelerated Site-to-Site VPN](https://docs.aws.amazon.com/vpn/latest/s2svpn/accelerated-vpn.html).
- [AWS Verified Access](https://docs.aws.amazon.com/verified-access/) — the modern alternative to Client VPN.
