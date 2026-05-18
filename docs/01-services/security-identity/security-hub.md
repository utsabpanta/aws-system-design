# Security Hub (CSPM)

> **One-line summary.** AWS's central security findings aggregator and Cloud Security Posture Management (CSPM) service. Consolidates findings from GuardDuty, Inspector, Macie, Config, IAM Access Analyzer, Firewall Manager, and partner tools, and scores your org against standards (AWS Foundational Security Best Practices, CIS, PCI, NIST).

## TL;DR
- One pane of glass for security findings across AWS services and integrated third-party tools, with normalized **AWS Security Finding Format (ASFF)** and OCSF support.
- Continuously evaluates resources against **security standards** (AWS Foundational Security Best Practices is the right baseline; CIS, PCI DSS, NIST 800-53 also available).
- **Automation Rules** auto-update or suppress findings in near-real-time based on criteria. **EventBridge** routing for custom workflows (auto-remediation, ticketing, paging).
- **Recently rebranded to "Security Hub CSPM"** (Cloud Security Posture Management) and gained **CloudWatch Logs ingestion of findings** (org-wide enablement, March 2026).
- Multi-account aggregation via delegated admin; findings from all member accounts roll up to a security account.

## When to use it
- Any AWS Organization with multiple accounts and security services running — Security Hub is the right aggregation layer.
- Compliance reporting against standards (AFSBP, CIS, PCI, NIST).
- Driving auto-remediation workflows from security findings.
- Cross-account / cross-Region finding triage in a SOC or security operations function.

## When NOT to use it
- Single-account, tiny footprint — direct GuardDuty / Inspector consoles may suffice.
- Workloads where you've fully standardized on a third-party CSPM (Wiz, Orca, Prisma, Lacework) — running both is duplicative.

## Key concepts

**Standards.** Pre-built control sets evaluated continuously against your resources:
- **AWS Foundational Security Best Practices (AFSBP)** — the right baseline.
- **CIS AWS Foundations Benchmark v1.x / v3.x.**
- **PCI DSS.**
- **NIST 800-53.**
- **Custom standards** — pick controls from a catalog or create your own.

Each control has a compliance status (Passed / Failed / Unknown / Not Applicable) per resource.

**Findings.** Normalized to **AWS Security Finding Format (ASFF)** — JSON with severity, resource, account, Region, type, recommendation. Optional **Open Cybersecurity Schema Framework (OCSF)** format for cross-vendor compatibility.

**Finding providers.**
- **AWS-native:** GuardDuty, Inspector, Macie, IAM Access Analyzer, Config, Firewall Manager, Health, Audit Manager, Systems Manager Patch Manager, Detective.
- **Partner integrations:** dozens of third-party security products send findings to Security Hub via the ASFF API.
- **Custom:** your own scanner can post findings to Security Hub.

**Automation Rules.** Define criteria (severity ≥ High AND resource type = S3 AND label contains "production"); update the finding (change severity, change workflow status, suppress, set note, update tags). Evaluated in near-real-time on every new finding.

**EventBridge integration.** Every finding emitted as an event. Build rules that target Lambda (auto-remediation), Step Functions (multi-step response), SNS (paging), SQS (ticketing).

**CloudWatch Logs ingestion (2026).** Configure Security Hub to deliver findings to CloudWatch Logs in ASFF or OCSF format using CloudWatch Pipelines. Useful for retention, Logs Insights queries, and SIEM forwarding. Enables organization-wide enablement rules.

**Insights.** Pre-built and custom saved searches over findings (e.g., "high-severity findings on production accounts in the last 24 h").

**Multi-account / multi-Region aggregation.** Delegated admin in a security account; designate an aggregator Region; findings from all member accounts and all linked Regions flow there.

## Pricing model

- **Standards evaluations** — per security check per month.
- **Findings ingested** — per million findings ingested per month from non-AWS sources (AWS-native sources are typically billed under the source service).
- **Volume-tiered** — cheaper at higher volume.

The bulk of typical cost is the AWS-native services that produce the findings (GuardDuty, Inspector, etc.); Security Hub itself adds modest aggregation cost.

## Quotas & limits

- **Findings per account per Region**: high (millions retained).
- **Custom insights per account per Region**: 100.
- **Automation rules per account per Region**: high (raisable).
- **Standards enabled** — multiple simultaneously.

## Common pitfalls

- **Not enabled.** Security Hub without it = no aggregation. Turn it on with AWS Foundational Security Best Practices as the starting standard.
- **One control standard, never re-tuned.** AFSBP is a baseline; add CIS / PCI as the compliance regime requires. Re-evaluate standards quarterly.
- **No automation rules.** Findings sit in the console. Auto-suppress noise, auto-escalate criticals.
- **EventBridge unused.** Without EventBridge routing, no ticketing, no paging, no remediation Lambdas. Wire it up.
- **Findings noise leaves real issues invisible.** Tune via suppression rules + automation rules + (where appropriate) disabling controls that don't fit your architecture (documented exceptions).
- **Single Region.** Findings in non-aggregator Regions stay there. Set the aggregator Region; cover every Region you have resources in.
- **Forgetting to enable in new member accounts.** Auto-enable via Organizations and the security-account delegated admin.
- **No SIEM forwarding.** Many SOCs operate from a SIEM, not directly from Security Hub. Use the EventBridge → SIEM integration or the new CloudWatch Logs delivery + a Logs subscription.

## Pairs well with
- [GuardDuty](guardduty.md), [Inspector](inspector.md), [Macie](macie.md), [Detective](detective.md), [Config](config.md), [Audit Manager](audit-manager.md), **IAM Access Analyzer**, **Firewall Manager** — primary AWS finding sources.
- **EventBridge + Lambda / Step Functions** — auto-remediation.
- **CloudWatch Logs** — finding delivery for retention / SIEM forwarding.
- **SIEM / SOAR** (Splunk, Datadog Security, Wiz, Orca, etc.) — bidirectional integration.

## Pairs well with these repo pages
- [GuardDuty](guardduty.md), [Inspector](inspector.md), [Macie](macie.md), [Detective](detective.md), [Config](config.md), [Audit Manager](audit-manager.md).
- [Security pillar](../../05-well-architected/security.md).

## Further reading
- [AWS Security Hub CSPM documentation](https://docs.aws.amazon.com/securityhub/).
- [AWS Foundational Security Best Practices](https://docs.aws.amazon.com/securityhub/latest/userguide/fsbp-standard.html).
- [Automation rules](https://docs.aws.amazon.com/securityhub/latest/userguide/automation-rules.html).
- [CloudWatch Logs ingestion of findings (2026)](https://aws.amazon.com/about-aws/whats-new/2026/03/amazon-cloudwatch-securityhub-findings/).
- [AWS Security Finding Format (ASFF)](https://docs.aws.amazon.com/securityhub/latest/userguide/securityhub-findings-format.html).
