# Security

> **One-line summary.** Protect data, systems, and assets — and assume any single layer of defense will eventually fail.

## TL;DR
- Identity is the new perimeter. IAM, not the network, is what stops most modern breaches.
- Encrypt everything in transit (TLS everywhere) and at rest (KMS-managed keys). The cost is nearly free; the cost of not doing it is unbounded.
- Defense in depth: assume each control will fail. WAF, security groups, IAM, encryption, monitoring — together, not in place of each other.
- Logs and audits are security tools, not compliance checkboxes. CloudTrail, VPC Flow Logs, and GuardDuty findings are the only credible answer to "what happened?"
- Automate response. A 3 AM page is a security tool only if there's something an automated runbook can do faster than a human.

## What the pillar is about

Security is the pillar that asks "who can do what to which resources, under what conditions, and how do you know?" It covers identity, data protection, infrastructure protection, detection, and incident response — and the *interactions* between them, which is where things actually break.

The defining mental shift in cloud security is from network-perimeter ("we trust everything inside the firewall") to **zero trust** ("we trust nothing, every request is authenticated and authorized, every action is logged"). AWS gives you the primitives; the design discipline is yours.

## AWS's seven design principles

1. **Implement a strong identity foundation.** Centralized identity (IAM Identity Center / Cognito), no long-lived credentials, least privilege everywhere, MFA on every human account.
2. **Maintain traceability.** Real-time logs, metrics, and alerts on identity and resource changes. CloudTrail on, CloudTrail logs immutable.
3. **Apply security at all layers.** Edge (WAF, Shield), network (security groups, NACLs, Network Firewall), compute (Inspector, SSM patching), data (KMS, S3 bucket policies), application (Cognito, IAM, parameter store).
4. **Automate security best practices.** Config rules, GuardDuty, Security Hub, EventBridge → Lambda for auto-remediation.
5. **Protect data in transit and at rest.** TLS 1.2+ everywhere, KMS for at-rest encryption, separate keys per data classification.
6. **Keep people away from data.** Direct human access to production data is a smell. Build self-service tools that scrub PII or operate on read replicas.
7. **Prepare for security events.** Run incident response game days, codify investigation runbooks (where do CloudTrail logs live? how do I freeze a compromised role?), and pre-build the IAM permissions the responders will need.

## Key practices

### Identity and access
- **Use IAM Identity Center (formerly SSO)** for human access. Federation from your IdP (Okta, Azure AD, Google Workspace). Humans should never have long-lived IAM users.
- **Workloads use roles**, never access keys. EC2 instance profiles, ECS task roles, Lambda execution roles. For cross-account access from outside AWS (CI/CD), use **OIDC federation** with GitHub Actions or your CI provider — no static secrets.
- **Least privilege by default.** Start with no permissions, add what the workload needs. Use IAM Access Analyzer to find unused permissions and surface external access.
- **Permissions boundaries** prevent permission escalation by developers who can create roles.
- **SCPs** (in AWS Organizations) enforce account-wide guardrails ("no one can disable CloudTrail," "no resources outside approved Regions").

### Data protection
- **Encrypt at rest by default.** S3 default encryption (SSE-KMS), RDS encryption, EBS encryption, DynamoDB encryption. Use customer-managed KMS keys (CMKs) over AWS-managed where you want grant control and key rotation policies.
- **Encrypt in transit.** TLS on every public endpoint (ACM for certs, free for AWS-fronted endpoints). Enforce TLS in service-to-service traffic too — VPC Endpoints, ELB listeners, internal mTLS for sensitive flows.
- **Key separation.** Different KMS keys per data classification (PII, PCI, general). KMS key policies + IAM tightly scope who can decrypt.
- **Secrets in Secrets Manager**, not in env vars or Parameter Store (use Parameter Store for non-secret config; Secrets Manager for rotated secrets like DB passwords).
- **Don't put data in S3 paths you didn't intend to be public.** S3 Block Public Access on at the account level. Macie scans for PII in S3.

### Network protection
- **Security groups** are stateful, instance-level firewalls. Default-deny inbound, restrict outbound when it matters. SG-to-SG references (not CIDRs) keep policies portable as instances change.
- **VPC Endpoints** for AWS services in private subnets. Saves NAT egress costs *and* keeps traffic off the public internet.
- **WAF** in front of CloudFront and ALB for L7 protection — managed rule groups handle most common attacks (OWASP Top 10, bots, IP reputation).
- **Shield Standard** is free DDoS protection at L3/L4 (automatic for CloudFront, Route 53, ALB). **Shield Advanced** is paid, adds L7 protection and a dedicated response team — worth it for high-profile public services.
- **Network Firewall** for stateful inspection / IDS-IPS at the VPC level when you need it.

### Detection
- **CloudTrail** on across the organization, with logs delivered to a separate logging account and immutable (Object Lock + cross-Region replication).
- **VPC Flow Logs** for network forensics.
- **GuardDuty** is the lowest-effort, highest-value security tool AWS sells — threat detection on top of CloudTrail, VPC Flow Logs, DNS, S3, EKS, RDS, Lambda. Turn it on in every account.
- **Security Hub** aggregates GuardDuty + Inspector + Macie + Config + third-party findings, scores against AWS Foundational Security Best Practices and CIS benchmarks.
- **Config** continuously evaluates resources against rules ("S3 buckets must not be public," "RDS must be encrypted"). Auto-remediation via SSM Automation.
- **Inspector** scans EC2 and ECR images for known CVEs.

### Incident response
- Have a **named incident commander role** in IAM, with permissions to investigate (read CloudTrail, snapshot EBS, isolate a compromised role) but not modify production.
- **Pre-built isolation playbooks** — Lambda functions that detach an instance from an SG, revoke a role's permissions via a permissions boundary, quarantine an S3 bucket.
- **Logs in a separate account** (the AWS log archive account pattern). A compromised production account must not be able to delete its own logs.
- **Game days.** Practice "AWS access key leaked," "RDS password in a GitHub repo," "EC2 instance making outbound connections to a mining pool" before they happen for real.

## AWS services that support this pillar

- **IAM, IAM Identity Center, IAM Access Analyzer** — identity, federation, permission visibility.
- **Cognito** — user identity for apps (user pools + identity pools).
- **KMS, CloudHSM** — key management, encryption at rest.
- **Secrets Manager, Parameter Store** — secrets and config.
- **ACM** — TLS certs (free for AWS-fronted endpoints).
- **WAF, Shield, Network Firewall, Verified Access, Verified Permissions** — perimeter and authorization.
- **GuardDuty, Inspector, Macie, Detective, Security Hub, Config, Audit Manager, Artifact** — detection, response, compliance.
- **CloudTrail, VPC Flow Logs, CloudWatch Logs** — audit trail.
- **Organizations + SCPs** — guardrails across accounts.

## Common anti-patterns

- **Long-lived IAM access keys** committed to Git, baked into AMIs, or stored in env vars. Use roles + STS.
- **`*` in IAM policies.** `s3:*` against `*` is a backdoor; even narrowly-scoped resources should use the smallest action set that works.
- **One-account, one-VPC for everything.** Compromised dev → compromised prod. Use AWS Organizations with separation by environment and blast radius.
- **CloudTrail off, or off in one Region.** CloudTrail must be on in every Region of every account — and the logs must go to an account no one in the workload account can write to.
- **Public S3 buckets by accident.** Block Public Access at the account level prevents this almost entirely.
- **MFA on humans only.** MFA-protect dangerous IAM actions too (delete CloudTrail, disable GuardDuty) via `aws:MultiFactorAuthPresent` conditions or SCPs.
- **Treating compliance as the goal.** SOC 2 / ISO 27001 / PCI compliance is the floor, not the ceiling. Many breached companies were compliant on paper.

## Pairs well with
- [Reliability](reliability.md) — a compromised system is, by definition, an unreliable system.
- [Operational Excellence](operational-excellence.md) — security automation lives inside your CI/CD and incident-response tooling.
- `docs/01-services/security-identity/` — per-service deep-dives (IAM, KMS, Cognito, WAF…).
- `docs/04-reference-architectures/multi-account-organization.md` — the AWS Organizations baseline.

## Further reading
- AWS Well-Architected Framework — Security pillar whitepaper.
- AWS Security Reference Architecture (AWS SRA).
- AWS Foundational Security Best Practices (Security Hub standard).
- *The Phoenix Project* and *The Unicorn Project* (Gene Kim) — culture context.
- *Site Reliability Engineering*, chapter on managing operational load — applies directly to on-call security.
