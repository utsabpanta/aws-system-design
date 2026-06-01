# Control Tower

> **One-line summary.** AWS's opinionated **landing zone** — pre-built AWS Organizations + IAM Identity Center + CloudTrail + Config + logging baseline, with **Account Factory** for governed account provisioning.

## TL;DR

- The right starting point for a new multi-account AWS Organization. Provisions the AWS-recommended baseline in one click: an Organizations setup, IAM Identity Center, log archive + audit accounts, baseline guardrails (Controls), and Account Factory.
- **Controls** (formerly "guardrails") are pre-built SCPs, AWS Config rules, and CloudFormation Hooks grouped by intent (mandatory, strongly recommended, elective).
- **Account Factory** — provision new member accounts that automatically inherit the baseline.
- **Account Factory Customization (AFC)** (Service Catalog-based) and **Account Factory for Terraform (AFT)** (GitOps / Terraform-based) extend Account Factory for org-specific customizations beyond the AWS baseline.
- For teams already heavily invested in Terraform or with bespoke landing-zone tooling, Control Tower may add unwanted opinion — but for greenfield, it's a huge head start.

## When to use it

- Greenfield AWS Organizations setup.
- Teams that want the AWS-recommended landing zone without designing one.
- Compliance-driven environments wanting a managed Control library and continuous compliance reporting.
- Standardized account provisioning across many teams / environments.

## When NOT to use it

- Existing AWS Organizations with deeply customized landing zones (Control Tower's enrollment can be disruptive).
- Workloads where the team prefers fully custom IaC for the landing zone.
- Single-account / very small AWS footprints.

## Key concepts

### Landing zone

Initial provisioning includes:

- **AWS Organizations** with a standard OU layout: `Security`, `Sandbox`, `Workloads` (Prod / NonProd), plus your own additions.
- **Two foundational accounts**:
  - **Log Archive** — central S3 buckets for CloudTrail logs, Config snapshots, etc.
  - **Audit / Security** — central account for security tooling (GuardDuty admin, Security Hub admin, IAM Access Analyzer admin).
- **IAM Identity Center** as the SSO baseline.
- **CloudTrail organization trail** delivering to the Log Archive account.
- **AWS Config** with aggregator to the Audit account.
- **Baseline Controls** applied to OUs.

### Controls (formerly Guardrails)

- **Mandatory** — always enforced; can't be disabled.
- **Strongly recommended** — opt-in; AWS strongly suggests.
- **Elective** — opt-in; supplemental.

Categories:

- **Preventive** — SCPs that block disallowed actions.
- **Detective** — Config rules that flag violations.
- **Proactive** — CloudFormation Hooks that block non-compliant resources before they're created.

Controls map to compliance frameworks (CIS, NIST 800-53, PCI DSS, SOC 2 — visible via Audit Manager).

### Account Factory

- **Provision a new account** with parameters (name, OU, email, baseline guardrails).
- Auto-applies the baseline (CloudTrail trail member, Config recorder, Identity Center permission sets).

### Account Factory Customization (AFC)

- Define a **CloudFormation blueprint** (via Service Catalog) that runs at account provisioning.
- Bootstrap each new account with a baseline of org-specific resources (default VPC, baseline IAM roles, monitoring agents).

### Account Factory for Terraform (AFT)

- **GitOps-style** account provisioning using Terraform.
- Pipeline triggers from a Git push to a request repo.
- Per-account customization runs Terraform / shell / Python after provisioning.
- More flexible than AFC for teams already invested in Terraform.

### Enrollment of existing accounts

- Enroll an existing AWS account into a Control Tower OU.
- Baseline Controls and tooling apply to the enrolled account.

### Account lifecycle

Provision → customize → use → close. Account closure goes through Organizations.

### Drift detection

Control Tower detects when accounts drift from the landing-zone configuration (manual changes to SCPs, missing roles, deleted CloudTrail) and surfaces it for remediation.

### Region governance

Designate which Regions Control Tower governs. New baselines / Controls apply only to those Regions.

## Pricing model

- **Control Tower itself is free.**
- You pay for the underlying services it provisions (CloudTrail logs to S3, Config evaluations, GuardDuty, Identity Center, etc.).
- **AFT** pipelines incur CodePipeline + CodeBuild + DynamoDB + Lambda costs.

## Quotas & limits

- **Accounts per landing zone**: same as Organizations limit (raisable to thousands).
- **OUs**: 5 levels deep, 1,000 OUs per org.
- **Controls per landing zone**: full library available; check current docs for max enabled count.
- **AFT pipelines / runs**: bounded by CodePipeline limits.

## Common pitfalls

- **Skipping Control Tower for greenfield orgs.** Build-your-own landing zones take months and often miss something. Control Tower covers the baseline AWS would recommend.
- **Manual changes to Control Tower-managed resources.** Causes drift; Control Tower will try to reconcile. Use Account Factory / AFT / parameterized Controls for changes.
- **No customization plan beyond the baseline.** AFC / AFT exists precisely for org-specific customization; otherwise every team adds the same things by hand.
- **Putting workloads in the management account.** Don't — the management account can't have SCPs applied. Workloads go in member accounts.
- **No region governance plan.** Letting users create resources in any Region adds compliance and cost surface. Govern Regions explicitly.
- **Skipping the Audit / Log Archive accounts.** Their separation is the whole point — don't shortcut by putting logs / security tools in the workload accounts.
- **Enrolling existing accounts without auditing.** Pre-existing resources may violate Controls; enroll carefully with a remediation plan.
- **Control Tower disabled to "regain control."** Most issues are solved with custom AFC blueprints or AFT customizations, not by disabling Control Tower.

## Pairs well with

- [Organizations](organizations.md) — Control Tower runs on top.
- [IAM Identity Center](../security-identity/iam-identity-center.md) — provisioned by Control Tower.
- [CloudTrail](cloudtrail.md), [AWS Config](../security-identity/config.md), [Security Hub](../security-identity/security-hub.md), [GuardDuty](../security-identity/guardduty.md) — set up automatically.
- [Service Catalog](service-catalog.md) — AFC blueprints.
- [CloudFormation](../devops/cloudformation.md) — AFC blueprint format.
- **Terraform** — AFT alternative.
- [Audit Manager](../security-identity/audit-manager.md) — frameworks Control Tower Controls map to.

## Pairs well with these repo pages

- [Organizations](organizations.md), [IAM Identity Center](../security-identity/iam-identity-center.md), [CloudTrail](cloudtrail.md), [Config](../security-identity/config.md).
- `docs/04-reference-architectures/multi-account-organization.md` (forthcoming).

## Further reading

- [AWS Control Tower documentation](https://docs.aws.amazon.com/controltower/).
- [Account Factory Customization](https://docs.aws.amazon.com/controltower/latest/userguide/af-customization-page.html).
- [Account Factory for Terraform (AFT)](https://docs.aws.amazon.com/controltower/latest/userguide/aft-overview.html).
- [Controls reference](https://docs.aws.amazon.com/controltower/latest/userguide/controls.html).
- [Landing zone setup](https://docs.aws.amazon.com/controltower/latest/userguide/setting-up.html).
