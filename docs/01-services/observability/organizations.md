# Organizations

> **One-line summary.** Multi-account governance for AWS. Group accounts into OUs, attach **Service Control Policies (SCPs)** and **Resource Control Policies (RCPs)** as org-wide guardrails, consolidate billing, share resources cross-account via **RAM**.

## TL;DR

- The right structure for any AWS footprint with more than ~3 accounts: a management account at the root, accounts organized into **Organizational Units (OUs)** (e.g., `Workloads/Prod`, `Workloads/NonProd`, `Sandbox`, `Security`, `Logging`, `Infrastructure`).
- **SCPs** restrict identity-based permissions org-wide ("no one can disable CloudTrail," "no resources outside approved Regions"). **RCPs** (newer) restrict what resource-based policies can grant ("no S3 bucket can be public," "no KMS key can be shared cross-account-without-org").
- **Consolidated billing** — one bill across all member accounts; pooled Reserved Instance / Savings Plan discounts.
- **AWS Resource Access Manager (RAM)** shares resources (VPC subnets, Transit Gateway, Route 53 Resolver rules, License Manager licenses, Glue Data Catalog, AppMesh meshes, OpenSearch Serverless collections, IAM Identity Center permission sets, etc.) cross-account.
- **Delegated administration** lets a non-management account run specific services (Security Hub, GuardDuty, Config, IAM Access Analyzer, etc.) on behalf of the org — keeps the management account small.

## When to use it

- Any AWS workload that spans more than ~3 accounts.
- Compliance environments needing per-account isolation.
- Multi-tenant SaaS with account-per-tenant.
- M&A scenarios consolidating multiple AWS accounts.
- Multi-team orgs wanting per-team accounts with shared guardrails.

## When NOT to use it

- True single-account / solo-engineer setup — Organizations adds complexity without much benefit at that scale.
- Workloads where the team will not maintain the OU structure / governance practice.

## Key concepts

### Account types

- **Management account** (formerly "master") — created when you set up Organizations; cannot have SCPs applied to it; **billing center, source of truth**.
- **Member accounts** — joined via invitation or created via Account Factory (Control Tower).

### Organizational Units (OUs)

Tree structure beneath the root. Common shape:

```
Root
├── Security (log archive, audit)
├── Infrastructure (network, shared services)
├── Workloads
│   ├── Prod
│   └── NonProd
├── Sandbox
└── Suspended
```

SCPs / RCPs apply to OUs (and inherit to all member accounts).

### Service Control Policies (SCPs)

- **Restrict identity-based permissions** org-wide. Don't grant; only restrict.
- Examples: "deny disabling CloudTrail," "deny resources outside approved Regions," "deny IAM-user creation in production," "deny actions without MFA."
- Up to 5 SCPs per OU (raisable).
- Inherit from root → OU → child OU → account.

### Resource Control Policies (RCPs)

- Newer (post-2024) counterpart to SCPs. **Restrict what resource-based policies (and resource-based grants) can do** org-wide.
- Examples: "no S3 bucket policy can grant `s3:GetObject` to `*`," "no KMS key can be shared with principals outside the org."
- Pairs with SCPs (which restrict identity-based policies).

### Consolidated billing

- One bill across the org.
- **Pooled discounts** — Savings Plans / Reserved Instances in any account apply to usage in any account in the org (within the same family / Region constraints).
- **Cost allocation tags** propagate.
- Account-level cost data via **Cost Explorer** + **CUR**.

### AWS Resource Access Manager (RAM)

- Share specific resources cross-account: VPC subnets, Transit Gateways, Route 53 Resolver rules, Glue Catalog, License Manager licenses, S3 outposts, AppSync APIs, OpenSearch Serverless collections, and more.
- Sharing scoped to: specific accounts, OUs, or the whole org.
- Cleaner than cross-account IAM role assumption for resource-share patterns.

### Delegated administration

- Designate a non-management account as the delegated admin for a service (Security Hub, GuardDuty, Config, IAM Access Analyzer, Macie, Inspector, Audit Manager, etc.).
- The delegated admin manages the service for the whole org without needing management-account access.
- Standard pattern: the **security account** is delegated admin for security tooling.

### Trusted access

Some services require Organizations to enable "trusted access" before they can operate org-wide (CloudTrail organization trail, Config aggregator, Service Catalog, etc.).

### Tag policies

- Define required tag keys / allowed tag values org-wide.
- Non-compliant resources flagged.

### Backup policies

- Org-wide AWS Backup configurations applied to member accounts.

### AI Services Opt-out policies

- Org-wide opt-out from AWS AI services using customer data for service improvement.

## Pricing model

- **Organizations itself is free.**
- **Consolidated billing is free.**
- **SCPs / RCPs / tag policies / backup policies / AI opt-out are free.**
- **AWS RAM is free.**
- **Account creation is free** (you pay only for resources in each account).

The free pricing of the governance layer is the point: the foundation that makes account-per-team / account-per-environment practical.

## Quotas & limits

- **Accounts per organization**: 10 default for new orgs; raisable to thousands.
- **OUs per organization**: 1,000.
- **OU nesting depth**: 5.
- **SCPs per OU / account**: 5 default (raisable to 10).
- **Resource shares per account (RAM)**: 5,000.
- **Trusted access integrations**: bounded by AWS service list.

## Common pitfalls

- **Single account for everything.** Blast radius problems on every front (security, billing, quota). Use Organizations + per-environment / per-team accounts.
- **No SCPs.** Identity-based permissions are unbounded. SCPs are the org-wide guardrail.
- **SCPs that only `Deny`, untested.** A new SCP can silently break workloads. Test in a sandbox OU first.
- **No log archive / security accounts.** Logs in the workload account can be deleted by compromise. Use the AWS-recommended log archive + audit account pattern.
- **No delegated admin for security services.** Management-account-only admin → human bottleneck and unnecessary exposure of the management account.
- **No RCPs.** SCPs alone leave resource-policy gaps (a bucket policy can still grant cross-org access). RCPs close that gap.
- **Manual account creation in the console.** Use **Control Tower Account Factory** or **AFT** for repeatable, customized account provisioning.
- **Forgetting that the management account can't have SCPs applied.** Don't put workloads in the management account.

## Pairs well with

- [Control Tower](control-tower.md) — opinionated landing zone built on Organizations.
- [Service Catalog](service-catalog.md) — product catalog scoped to OUs.
- [IAM Identity Center](../security-identity/iam-identity-center.md) — workforce access across accounts.
- [Security Hub](../security-identity/security-hub.md), [GuardDuty](../security-identity/guardduty.md), [Config](../security-identity/config.md), **IAM Access Analyzer** — delegated-admin services.
- [CloudTrail](cloudtrail.md) — organization trail.
- **AWS Backup** — org-wide backup policy.

## Pairs well with these repo pages

- [Control Tower](control-tower.md), [IAM Identity Center](../security-identity/iam-identity-center.md), [CloudTrail](cloudtrail.md).
- `docs/04-reference-architectures/multi-account-organization.md` (forthcoming).

## Further reading

- [AWS Organizations documentation](https://docs.aws.amazon.com/organizations/).
- [Service Control Policies (SCPs)](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html).
- [Resource Control Policies (RCPs)](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_rcps.html).
- [AWS RAM](https://docs.aws.amazon.com/ram/).
- [Delegated administration](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_integrate_services_list.html).
