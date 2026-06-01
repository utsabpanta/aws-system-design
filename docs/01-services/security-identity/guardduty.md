# GuardDuty

> **One-line summary.** Managed threat-detection service. Continuously analyzes CloudTrail, VPC Flow Logs, DNS, S3, EKS, RDS, Lambda, and Malware Protection scans to surface suspicious activity — no agents, no rules to write.

## TL;DR

- The single highest-leverage security tool AWS sells. **Turn it on in every account, every Region.** Cost is small; the value is enormous.
- Detects compromise patterns (instance reaching a known C2 IP, IAM credentials exfiltrated, S3 bucket scanned by a known recon source, EC2 mining cryptocurrency, RDS brute-force, EKS pod talking to a bad domain) with zero configuration.
- **Add-on protection plans** — S3 Protection, EKS Protection, Malware Protection, RDS Protection, Lambda Protection, EKS Runtime Monitoring — each adds a per-feature dimension.
- Findings flow into **Security Hub CSPM**, **Detective** (auto-integrated), and **EventBridge** for auto-remediation.
- ML / heuristics-based — false positives exist; tune via suppression rules and trusted IP lists.

## When to use it

- Every AWS account, period. The cost is trivial relative to the detection capability.
- Multi-account orgs: enable as a delegated admin from the security account; findings centralize automatically.
- Workloads with elevated risk (financial, healthcare, customer PII at scale) — the add-on plans (RDS Protection, Malware Protection, Runtime Monitoring) further reduce mean-time-to-detect.

## When NOT to use it

- Essentially never "off." Cost-tune the add-on plans per workload, but the base service should always be on.

## Key concepts

**Detector.** The GuardDuty resource per Region per account. Enables analysis of the data sources you've turned on.

**Foundational data sources** (no extra fee beyond GuardDuty base):

- **CloudTrail management events** — AWS API activity.
- **VPC Flow Logs** — network flow telemetry.
- **DNS query logs** — domain-name patterns (talking to known bad domains).

**Add-on protection plans** (additional per-feature pricing):

- **S3 Protection** — CloudTrail data events on S3 (object-level access patterns), unusual access, large-scale tampering.
- **EKS Protection** — Kubernetes API audit logs.
- **EKS Runtime Monitoring** — per-node eBPF agent for runtime kernel-level signals (process anomalies, syscall patterns).
- **Malware Protection** — on-demand and event-driven scans of EBS volumes and S3 objects.
- **RDS Protection** — authentication anomalies on RDS / Aurora.
- **Lambda Protection** — network activity from Lambda functions.

**Finding severity.** Low / Medium / High. Each finding has a type, affected resource, and recommendation.

**Trusted IP lists / threat IP lists.** Allow-list known-good IPs to suppress findings; deny-list known-bad IPs to amplify.

**Suppression rules.** Filter findings by attributes (`finding type = Recon:IAMUser/UserPermissions AND severity < 4`) — archive automatically. Use sparingly; over-suppression hides real issues.

**Multi-account.** Delegated admin in a security account; member accounts enrolled centrally. Findings aggregate to the admin account.

**Integrations.**

- **Security Hub CSPM** — automatic finding aggregation.
- **Detective** — automatic finding ingestion + investigation graph.
- **EventBridge** — every finding emitted as an event for custom routing (SIEM, Lambda auto-remediation, Slack alert).

## Pricing model

- **Foundational analysis** — per million events analyzed (CloudTrail, VPC Flow Logs, DNS queries).
- **Add-on plans** — per-feature pricing:
  - **S3 Protection** — per million CloudTrail data events scanned.
  - **EKS Protection** — per million Kubernetes audit events.
  - **EKS Runtime Monitoring** — per vCPU-hour scanned.
  - **Malware Protection** — per GB scanned.
  - **RDS Protection** — per million RDS authentication events.
  - **Lambda Protection** — per million network events.

GuardDuty's base cost is small relative to the security value. Add-on costs require sizing per workload — a busy CloudTrail data-event stream from S3 can be the dominant line item.

## Quotas & limits

- **Detectors per account per Region**: 1 (one per Region).
- **Member accounts per delegated admin**: thousands.
- **Trusted / threat IP list size**: 250,000 IPs.

## Common pitfalls

- **Turned off in some Regions.** A compromise can happen in *any* Region you have resources in — including ones you don't actively use. Enable everywhere.
- **No multi-account aggregation.** Findings sitting in 50 member accounts that no one looks at. Use delegated admin in the security account.
- **No EventBridge routing.** Findings stay in the console where no one sees them. Route to SIEM / Slack / auto-remediation Lambda.
- **All add-on plans on by default.** S3 Protection on a CloudTrail with billions of S3 events is expensive. Enable based on threat model and traffic volume.
- **Over-suppression.** Suppressing every "noisy" finding type leaves you blind to the real ones. Tune suppression rules narrowly and revisit quarterly.
- **No runbook for high-severity findings.** A page at 3 AM that says "GuardDuty: High" with no playbook is the failure mode. Map finding types to runbooks.
- **Skipping Runtime Monitoring on critical EKS workloads.** Container-runtime threats are increasingly the attack surface; Runtime Monitoring catches what API-level signals miss.

## Pairs well with

- **Security Hub CSPM** — aggregates findings.
- **Detective** — graphs and investigates findings.
- **EventBridge** — finding-driven automation.
- **AWS Lambda** — auto-remediation runbooks.
- **AWS Organizations** — multi-account delegated admin.

## Pairs well with these repo pages

- [Security Hub CSPM](security-hub.md), [Detective](detective.md), [Inspector](inspector.md).
- [Security pillar](../../05-well-architected/security.md).

## Further reading

- [Amazon GuardDuty documentation](https://docs.aws.amazon.com/guardduty/).
- [GuardDuty protection plans](https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_data-sources.html).
- [Finding types](https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_finding-types-active.html).
- [GuardDuty multi-account management](https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_organizations.html).
