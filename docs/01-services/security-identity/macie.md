# Macie

> **One-line summary.** Managed data security service for S3. Discovers, classifies, and continuously monitors sensitive data (PII, financial identifiers, credentials) at object scale.

## TL;DR
- The right answer for "what sensitive data sits in our S3 buckets, and is anything publicly accessible / shared cross-account?"
- Continuously evaluates **bucket-level security posture** (public, encryption status, replication, sharing) plus on-demand and scheduled **content classification jobs** (sample or full-scan).
- Built-in **managed data identifiers** for common PII (names, addresses, SSNs, credit cards, AWS access keys, etc.) plus **custom data identifiers** for organization-specific patterns.
- Findings flow to **Security Hub CSPM** and **EventBridge** for routing.
- Cost grows with the *bytes you classify* — strategy matters. Sampled discovery jobs and bucket-level posture checks alone are cheap; full-scan classification at PB scale is expensive.

## When to use it
- Any org that stores customer / employee data in S3 and needs to know where the sensitive stuff is.
- Compliance (GDPR, CCPA, PCI, HIPAA) requirements around data discovery and reporting.
- Onboarding to a new account / acquired company — figure out S3 sprawl quickly.
- Continuous monitoring for accidentally-exposed sensitive buckets.

## When NOT to use it
- Data outside S3 — Macie only works on S3 (and S3-via-Storage-Gateway). DynamoDB / RDS need different tools.
- Workloads where you already maintain authoritative data inventory and don't need discovery — Macie is most useful when "where is X?" is hard to answer.
- Very low-budget environments where full classification is unaffordable — bucket-level posture monitoring alone gives most of the value at minimal cost.

## Key concepts

### Bucket-level monitoring (always on once enabled)
Continuously evaluates every S3 bucket in the account for:
- **Public access** (any allow-anonymous policy or ACL).
- **Encryption status** (SSE-S3, SSE-KMS, none).
- **Cross-account sharing** (allow-other-account policies).
- **Replication destination** (replicating outside the org).
- **Object Lock and versioning state**.

Findings emitted for each material issue.

### Sensitive-data discovery
Two modes:
- **Automated sensitive data discovery** — Macie samples a small subset of objects from each bucket regularly, gives you a heatmap. Cheap, continuous, low-precision.
- **Classification jobs** — you define which buckets / prefixes to scan, the data identifiers to look for, and the schedule. Can be one-time or recurring. Higher cost, higher fidelity.

### Data identifiers
- **Managed** — AWS-maintained for common PII types: name, address, email, phone, SSN, EIN, passport, driver's license, credit card, IBAN, AWS secrets, ML-based detection of credentials.
- **Custom** — regex-based + keyword proximity rules; for company-specific patterns (customer IDs, internal employee numbers, project codes).
- **Allow lists** — string lists or regex that suppress matches (e.g., "this string looks like a credit card but it's a test value").

### Findings
- **Policy findings** — bucket-level posture violations.
- **Sensitive data findings** — objects containing matching data identifiers.

Findings include sample matches (redacted by default), object location, and severity.

### Multi-account
Enable as a delegated admin from a security account. Member accounts' findings aggregate centrally.

### Integrations
- **Security Hub CSPM** — automatic aggregation.
- **EventBridge** — finding-driven automation.
- **S3 Object Lock** — alert on object writes that bypass intended retention.

## Pricing model

- **Bucket-level evaluation** — per S3 bucket per month (small).
- **Automated discovery** — per GB sampled (small per bucket).
- **Classification jobs** — per GB scanned; scales with how much data and how often you scan.
- **Custom data identifiers** — no extra fee for defining; included in classification jobs.

The cost lever is **scope and frequency of classification jobs** — scan only what matters, on the right cadence.

## Quotas & limits

- **Classification jobs per account per Region**: 1,000 default.
- **Custom data identifiers per account per Region**: 10,000 default.
- **Object size for content inspection**: 20 MB inspected per object (truncated beyond).
- **Supported object types**: text, common archive formats, common document formats (PDF, DOCX, etc.).

## Common pitfalls

- **Not enabled.** "We don't have PII in S3" is rarely true. Macie almost always finds something on first scan.
- **Full-scan classification of everything.** Big buckets × broad data-identifier list = big bill. Start with automated discovery + bucket-level monitoring; promote to classification jobs for buckets that warrant it.
- **No EventBridge routing.** Findings sit in the console; no one acts. Route to SIEM / Slack / Lambda.
- **Allow-list as a finding suppression mechanism.** Allow lists should reflect "actually not sensitive"; use suppression rules in Security Hub for noise.
- **Custom data identifiers without false-positive testing.** A custom pattern that fires on every customer-id-shaped string finds a lot of noise. Use keyword proximity rules to reduce false positives.
- **Macie as your only data inventory.** Macie is a discovery tool; combine it with bucket tagging and an explicit data inventory practice for governance.
- **No remediation runbook for public-bucket findings.** "Macie says this bucket is public" should immediately page someone; otherwise it's just a record.

## Pairs well with
- **Security Hub CSPM** — aggregates findings.
- **EventBridge + Lambda** — auto-remediation (e.g., revoke `s3:GetObject` to `*`).
- **S3 Block Public Access** — the prevention to Macie's detection.
- **AWS Config** — for non-data security posture on S3 (Macie covers the contents).

## Pairs well with these repo pages
- [S3](../storage/s3.md), [Security Hub CSPM](security-hub.md), [GuardDuty](guardduty.md).
- [Security pillar](../../05-well-architected/security.md).

## Further reading
- [Amazon Macie documentation](https://docs.aws.amazon.com/macie/).
- [Managed data identifiers](https://docs.aws.amazon.com/macie/latest/user/managed-data-identifiers.html).
- [Custom data identifiers](https://docs.aws.amazon.com/macie/latest/user/custom-data-identifiers.html).
- [Automated sensitive data discovery](https://docs.aws.amazon.com/macie/latest/user/automated-sensitive-data-discovery.html).
- [Macie multi-account](https://docs.aws.amazon.com/macie/latest/user/macie-orgs.html).
