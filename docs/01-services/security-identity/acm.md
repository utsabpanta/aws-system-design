# ACM (AWS Certificate Manager)

> **One-line summary.** Free, managed public TLS certificates for AWS-fronted endpoints (ALB, NLB, CloudFront, API Gateway, App Runner, etc.) plus private CA for internal mTLS / IoT scenarios.

## TL;DR
- **Public certs are free** when used with AWS-fronted endpoints — no excuse to run plain HTTP on anything internet-facing.
- Auto-renewal handled by AWS — certs renew silently as long as the validation (DNS or email) is in place.
- Public certs **only validate domains you control**; private CAs (ACM Private CA) issue certs from your own root for internal use.
- **CloudFront certs must live in `us-east-1`** even if your origin is elsewhere. Easy to forget.
- For workloads needing certs on EC2 / your own LB / on-prem (i.e., **not** AWS-fronted), use ACM **Private CA** + the **ACM-issued public cert export** (paid feature) or roll your own ACME / cert-manager pipeline.

## When to use it
- Public TLS for any AWS-fronted endpoint (ALB, NLB, CloudFront, API Gateway, App Runner, ECS, Beanstalk).
- mTLS at ALB / API Gateway listeners — ACM hosts the trust store.
- Private CA for internal TLS (microservices), IoT device certs, dev/test environments with stable internal CAs.
- Code-signing scenarios where you need a publicly trusted cert (ACM-issued exported certs can be used).

## When NOT to use it
- TLS for non-AWS endpoints where the workload can use Let's Encrypt directly — free, well-tooled, runs anywhere.
- Highly specialized certs (EV / OV public TLS, code-signing certs from specific CAs) that ACM doesn't issue.

## Key concepts

### Public certificates (free)
- **Domain validation** — DNS (`CNAME` record in Route 53; Route 53 integration adds it for you) or email. DNS validation is the default and the only sane choice for automation.
- **SAN list** — multiple domains on one cert; up to many SANs per cert.
- **Wildcard certs** — `*.example.com`. Single-level wildcards only — `*.*.example.com` is not supported.
- **Auto-renewal** — happens 60 days before expiry as long as DNS validation records are still in place. Email-validated certs require manual re-validation (one of many reasons DNS validation is the right default).

### Private CAs (ACM Private CA)
- AWS-managed private CA you fully control. Root and subordinate CA hierarchy.
- Issue certs to internal services, EC2 instances, containers, IoT devices.
- **Short-lived certs** support — issue with hour-scale lifetimes for ephemeral workloads.
- Per-CA monthly fee + per-cert-issued fee. Not free.

### Importing your own certs
- ACM can import an externally-issued cert (with private key). Useful for migrating from another CA.
- Imported certs **don't auto-renew** — ACM only auto-renews certs it issued.
- 825-day max validity (browser ecosystem-wide limit).

### Region notes
- Public ACM certs are **regional**. A cert in `us-east-1` cannot be used on an ALB in `eu-west-1`.
- **CloudFront requires the cert in `us-east-1`** — always provision CloudFront-bound certs there.

### Exporting certs
- Public ACM certs **cannot be exported with the private key** — that's a deliberate security property.
- Private CA certs **can** be exported (with the private key) — needed for workloads not on AWS-managed endpoints.

### Lifecycle and audit
- CloudTrail logs cert events (issuance, renewal).
- ACM integrates with **AWS Config** for tracking cert state across the org (e.g., "alert on certs expiring in 30 days that haven't auto-renewed").

## Pricing model

- **Public certs for AWS-fronted endpoints**: **free**.
- **Exporting public ACM certs**: paid per export.
- **Private CA**: per-CA monthly fee (significant; in the hundreds of dollars / month / CA) + per-issued-cert fee.
- **Imported certs**: free to store; you pay nothing to ACM for the cert itself but get no auto-renewal.

## Quotas & limits

- **Public certs per account per Region**: 2,500 default (raisable).
- **SAN names per cert**: 10 default (raisable).
- **Domain names per validation request**: 10.
- **Private CAs per Region**: 100.
- **Cert validity**: up to 13 months for public certs (industry standard); private certs configurable per CA policy.

## Common pitfalls

- **HTTP-only public endpoints in 2026.** No excuse — ACM public certs are free for any AWS-fronted endpoint.
- **CloudFront cert in the wrong Region.** Must be `us-east-1`. The CloudFront console will refuse, but Terraform / CDK can be made to make the mistake.
- **Email validation in production.** Manual re-validation needed at every renewal. Always DNS.
- **DNS validation `CNAME` deleted "to clean up DNS."** Cert auto-renewal silently breaks. Use Route 53 integration in ACM (creates and tracks the validation record for you) and treat validation records as load-bearing.
- **Imported certs assumed to auto-renew.** They don't. Set CloudWatch alarms on cert expiry for any imported cert.
- **Wildcard cert for everything.** Convenient until it's compromised — a leaked wildcard exposes every subdomain. For sensitive subdomains, issue per-subdomain certs.
- **Private CA where AWS-fronted public certs would do.** Private CAs have a real monthly fee; don't reach for them when ACM public would work.
- **No alerting on cert state.** Auto-renewal usually works, but when it doesn't, the first signal shouldn't be a customer reporting an expired cert. Wire Config rules or EventBridge alerts on ACM events.

## Pairs well with
- [CloudFront](../networking/cloudfront.md), [ELB](../networking/elb.md), [API Gateway](../networking/api-gateway.md), [App Runner](../compute/app-runner.md) — all consume ACM public certs.
- [Route 53](../networking/route53.md) — DNS validation; integrated workflow for adding validation records.
- **AWS Config** — track cert state across accounts.
- **EventBridge** — react to cert expiry events.
- **AWS IoT** — Private CA for device certs.

## Pairs well with these repo pages
- [Security pillar](../../05-well-architected/security.md) — "TLS everywhere."

## Further reading
- [AWS Certificate Manager documentation](https://docs.aws.amazon.com/acm/).
- [Public vs private certificates](https://docs.aws.amazon.com/acm/latest/userguide/acm-public-certificates.html).
- [DNS validation](https://docs.aws.amazon.com/acm/latest/userguide/dns-validation.html).
- [ACM Private CA](https://docs.aws.amazon.com/privateca/latest/userguide/PcaWelcome.html).
- [Certificate auto-renewal](https://docs.aws.amazon.com/acm/latest/userguide/managed-renewal.html).
