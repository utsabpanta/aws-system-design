# Artifact

> **One-line summary.** AWS's compliance document portal. Download AWS's own SOC, PCI, ISO, FedRAMP, and other audit reports; accept AWS agreements (BAA, GDPR DPA, etc.) on behalf of your account.

## TL;DR

- Where you go to download the **SOC 1 / SOC 2 / SOC 3 / PCI DSS AOC / ISO 27001 / 27017 / 27018 / FedRAMP / HIPAA** reports for *AWS itself* — the documents your auditors need to prove that the cloud you're running on is compliant.
- Also where you (or your legal team) accept AWS-published agreements like the **Business Associate Addendum (BAA)** for HIPAA, the **GDPR Data Processing Addendum**, and others.
- Free.
- Doesn't generate evidence about *your* workloads — that's **Audit Manager**. Artifact is about AWS's compliance posture, which your auditor needs as part of evaluating yours.

## When to use it

- Auditor asks for AWS's SOC 2 report — download it from Artifact and share.
- Adopting HIPAA / processing PHI on AWS — accept the BAA in Artifact.
- GDPR scope — accept the GDPR DPA.
- Internal compliance reviews where auditors need to confirm the shared-responsibility-model "AWS side" is met.

## When NOT to use it

- For evidence about *your* configuration / posture — use **Config**, **Audit Manager**, **Security Hub CSPM**.
- For your own SOC 2 report — that's something a third-party auditor produces for *your* company; AWS doesn't generate it for you.

## Key concepts

**Reports.** Compliance audit reports for AWS, organized by standard. Periodically refreshed (typically annually) as the corresponding audits are completed.

**Agreements.** Legal contracts you accept on behalf of your AWS account / Organization — BAA, GDPR DPA, France data protection addenda, etc.

**Access control.** Permissioned via IAM — `artifact:Get`, `artifact:DownloadAgreement`, etc.

**Org-wide acceptance.** Some agreements can be accepted at the management account level for the whole Organization.

## Pricing model

Free.

## Quotas & limits

- Bounded only by IAM permissions and the rate at which AWS publishes new reports.

## Common pitfalls

- **Confusing Artifact with Audit Manager.** Artifact is *AWS's* compliance documents. Audit Manager evaluates *your* configuration against frameworks.
- **Auditor asks for a "current SOC 2 report" but Artifact still shows last year's.** Audits run on a cycle; the most recent published report may be a few months old. AWS publishes when the next cycle completes.
- **Sharing Artifact PDFs externally without checking the redistribution terms.** Many of the documents have access restrictions (NDA-style); confirm allowed sharing before posting to a customer.
- **Forgetting to accept the BAA before processing PHI.** No HIPAA coverage on AWS services until the BAA is in place for your account.

## Pairs well with

- [Audit Manager](audit-manager.md) — Artifact for AWS-side evidence, Audit Manager for your-side.
- **AWS Compliance Center** (web) — broader compliance docs and links.
- **IAM** — control who can download what.

## Pairs well with these repo pages

- [Audit Manager](audit-manager.md), [Config](config.md).

## Further reading

- [AWS Artifact documentation](https://docs.aws.amazon.com/artifact/).
- [AWS Compliance Center](https://aws.amazon.com/compliance/).
- [AWS HIPAA whitepaper](https://docs.aws.amazon.com/whitepapers/latest/architecting-hipaa-security-and-compliance-on-aws/welcome.html).
