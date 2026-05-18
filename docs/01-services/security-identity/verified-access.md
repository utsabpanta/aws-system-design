# Verified Access

> **One-line summary.** Zero-trust application access. Users authenticate via your IdP and are evaluated per request against fine-grained policies before reaching corporate apps — no VPN needed.

## TL;DR
- The modern alternative to **Client VPN** for workforce application access. Per-application access, not per-network.
- Authenticates via **IAM Identity Center** or any OIDC-compatible IdP (Okta, Entra ID, Google Workspace, etc.). Authorizes per request via **Cedar policies** that evaluate identity claims and device posture.
- Supports both **HTTP(S) apps** (browser-based) and **TCP apps** (Git over CLI, SSH-style, DB clients — via the **Connectivity Client** desktop helper).
- **Browser extension** integrates device-security signals from third-party endpoint-management tools (Jamf, CrowdStrike, JumpCloud, etc.) — only needed if your policies reference device state.
- Lower per-user cost than Client VPN at scale; replaces "VPN for everything" with "scoped access to the specific apps each user needs."

## When to use it
- Workforce remote access to internal web apps (Confluence, Jira, internal dashboards, dev environments).
- TCP-based dev access (Git over SSH, kubectl, DB clients) without giving everyone full network reachability.
- Migrating away from VPN-based "network access" toward per-application zero-trust.
- Environments using IAM Identity Center or a modern IdP that wants to extend SSO to network-private apps.

## When NOT to use it
- Network-level access required (custom protocols, fat clients that need broad routing) — Client VPN may still fit.
- External / customer-facing apps — use Cognito + standard auth.
- Tiny user populations where the operational overhead beats the per-app scoping benefits.

## Key concepts

**Verified Access instance.** Top-level resource per Region. Has a policy and an attached identity provider.

**Trust provider.** Identity source: **IAM Identity Center** (recommended for AWS-org-aligned workforces) or any **OIDC IdP** (Okta, Entra ID, Google Workspace, JumpCloud, Auth0, etc.).

**Device trust provider** (optional). Integration with third-party endpoint security / MDM tools (Jamf, CrowdStrike, JumpCloud) — augments policy with device claims (posture, compliance status, OS version).

**Verified Access group.** A logical bucket of applications that share a policy.

**Verified Access endpoint.** One per protected app. Two types:
- **Load balancer endpoint** — ALB or NLB target.
- **Network interface endpoint** — direct to an ENI (an EC2 instance running the app).
- **CIDR endpoint** — TCP endpoint reachable via the Connectivity Client (no public DNS exposure).
- **RDS endpoint** — TCP endpoint to RDS without VPN.

**Policy.** Written in **Cedar** (AWS's open-source policy language; same as Verified Permissions). Evaluates per request:

```cedar
permit(
  principal,
  action == "verifyAccess::Access::"connect",
  resource
)
when {
  principal.email like "*@example.com" &&
  principal.groups.contains("engineering") &&
  context.device.is_managed == true
};
```

**Browser extension.** Required only if your policies evaluate device-security state from a third-party MDM. Otherwise users access apps without it (just identity + IdP auth).

**Connectivity Client.** Desktop helper for TCP apps. Routes traffic to the Verified Access endpoint based on hostname; user authenticates via the same IdP.

**Logging.** Per-request access logs include identity claims, decision, and rule that matched — useful for audit and policy tuning.

## Pricing model

- **Per-app-hour** per protected endpoint.
- **Per-GB processed** through Verified Access.
- **Per-request** charges layered on top.
- **IAM Identity Center / OIDC IdP** itself is free / your IdP's own cost.

Generally lower than Client VPN at moderate-to-large workforces because of the per-app rather than per-connected-user-hour pricing.

## Quotas & limits

- **Instances per account per Region**: 1 (with multiple groups beneath).
- **Groups per instance**: 50.
- **Endpoints per group**: 50.
- **Policies per group**: 1 (Cedar policy).
- **Endpoint targets**: ALB, NLB, ENI, RDS, custom TCP via Connectivity Client.

## Common pitfalls

- **Treating it as a VPN replacement for every workload.** Network-protocol fat clients sometimes still need VPN. Verified Access is for app-scoped access.
- **No device-trust integration when policies reference device state.** Device claims come from a configured device trust provider; without it, the policies fall through to "no device info."
- **Cedar policy errors only at runtime.** Test policies in staging; use policy syntax / validation tools.
- **Connectivity Client distribution.** TCP apps need users to install the client. Plan distribution / auto-deploy via your endpoint management.
- **Browser extension assumed mandatory.** It's optional unless policies reference device state.
- **No access logs.** Without them, "why was access denied?" is hard. Send logs to CloudWatch / S3 / Kinesis.
- **One huge group for everything.** Per-group policy scoping makes per-app policies cleaner. Use groups by sensitivity tier or per app family.

## Pairs well with
- [IAM Identity Center](iam-identity-center.md) — primary identity source.
- **Third-party IdPs (Okta, Entra ID, Google Workspace, etc.)** — OIDC-based federation.
- **Third-party endpoint security tools (Jamf, CrowdStrike, JumpCloud)** — device trust providers.
- [ELB](../networking/elb.md) — endpoint backends.
- **CloudWatch Logs / S3** — access log destination.

## Pairs well with these repo pages
- [Client VPN](../networking/vpn.md) — the older alternative for workforce access.
- [Verified Permissions](verified-permissions.md) — the sibling service that handles authorization decisions in your own apps.
- [Cognito](cognito.md) — customer-facing auth (different problem).

## Further reading
- [AWS Verified Access documentation](https://docs.aws.amazon.com/verified-access/).
- [Verified Access features](https://aws.amazon.com/verified-access/features/).
- [Cedar policy language](https://www.cedarpolicy.com/).
- [Connectivity Client for Verified Access](https://docs.aws.amazon.com/verified-access/latest/ug/connectivity-client.html).
- [Browser extension](https://chromewebstore.google.com/detail/aws-verified-access/aepkkaojepmbeifpjmonopnjcimcjcbd).
