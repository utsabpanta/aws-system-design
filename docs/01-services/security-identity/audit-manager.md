# Audit Manager

> **One-line summary.** Continuous, evidence-based compliance assessment. Maps AWS resource state and CloudTrail activity to controls in standards (SOC 2, PCI, HIPAA, NIST, CIS, GDPR) and assembles audit-ready reports.

## TL;DR
- Targets the "we have an audit coming, gather evidence" problem. Continuously collects evidence (Config evaluations, CloudTrail events, Security Hub findings, manual uploads) and maps it to controls in frameworks.
- Pre-built **frameworks** for SOC 2 (TSC 2017), PCI DSS, HIPAA, NIST 800-53 / 800-171, CIS AWS Foundations, GDPR. Custom frameworks too.
- **Assessment reports** package evidence per control into auditor-ready PDFs.
- Right for teams with formal compliance obligations who otherwise screenshot the AWS console and paste into Word documents.
- Less essential if your compliance footprint is light or your auditors have a direct integration with your tooling already.

## When to use it
- Annual SOC 2 / PCI / HIPAA audits where you'd otherwise spend weeks collecting evidence.
- Continuous compliance posture maintenance (not just at audit time).
- Multi-account orgs with consolidated compliance reporting.

## When NOT to use it
- No compliance obligations and no plan to get any.
- Workloads where your auditor uses a third-party governance tool with direct AWS integration (Vanta, Drata, Tugboat Logic).
- Tiny orgs where manual evidence gathering for the few controls in scope is cheaper than learning Audit Manager.

## Key concepts

**Framework.** A bundled set of controls organized by compliance standard. AWS provides frameworks for major standards; you can clone and customize, or build your own.

**Assessment.** An ongoing evaluation against a framework, scoped to specific AWS accounts and Regions. Generates evidence continuously.

**Control.** A single requirement in a framework (e.g., "PCI DSS 1.2.1 — restrict inbound and outbound traffic"). Controls map to **data sources** that produce evidence.

**Data sources** for evidence:
- **AWS Config evaluations** — compliance status for relevant rules.
- **AWS Security Hub** findings.
- **AWS CloudTrail** events.
- **Manual evidence upload** — for controls that need human attestation (e.g., "policy doc reviewed by board").

**Evidence finder.** Search across evidence by control, time, account, resource — the audit-trail navigator.

**Assessment reports.** PDF reports per control, packaged for auditors.

**Delegation.** Assign control reviewers to subject-matter experts (e.g., the Networking team reviews "network segmentation" controls; Security reviews IAM controls).

**Sharing.** Share custom frameworks across accounts / Regions.

## Pricing model

- **Per active resource per month** assessed.
- **Volume-tiered** (cheaper per resource at higher counts).
- **Evidence storage** included.

## Quotas & limits

- **Custom frameworks per account**: 100.
- **Concurrent assessments**: bounded.
- **Evidence retention**: 2 years default.

## Common pitfalls

- **Standing up Audit Manager the week before an audit.** Evidence needs time to accumulate. Run continuous assessments well before audit cycles.
- **No mapping plan to the auditor's expectations.** The framework Audit Manager ships with may not match exactly what your auditor asks for. Coordinate with the auditor on control mapping before building the assessment.
- **All evidence treated as "complete."** Manual evidence (policy docs, attestations) needs human curation — Audit Manager can't tell whether the PDF you uploaded actually says what the control requires.
- **Audit Manager but no Config.** Most evidence comes from Config; without Config rules on, Audit Manager has nothing to evaluate.
- **One-off audits ignored after.** Continuous assessments are the point. Re-running once a year wastes most of the value.

## Pairs well with
- [Config](config.md) — primary evidence source.
- [Security Hub CSPM](security-hub.md) — findings as evidence.
- [CloudTrail](../observability/cloudtrail.md) (forthcoming) — control evidence on API activity.
- **AWS Artifact** — official AWS compliance reports (SOC 2 etc. for AWS itself).
- **AWS Organizations** — multi-account scope.

## Pairs well with these repo pages
- [Config](config.md), [Security Hub CSPM](security-hub.md), [Artifact](artifact.md).

## Further reading
- [AWS Audit Manager documentation](https://docs.aws.amazon.com/audit-manager/).
- [Supported frameworks](https://docs.aws.amazon.com/audit-manager/latest/userguide/Framework-libraries.html).
- [Evidence finder](https://docs.aws.amazon.com/audit-manager/latest/userguide/evidence-finder.html).
- [Audit Manager pricing](https://aws.amazon.com/audit-manager/pricing/).
