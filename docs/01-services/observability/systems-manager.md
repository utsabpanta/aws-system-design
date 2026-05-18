# Systems Manager (SSM)

> **One-line summary.** AWS's "operations hub" — a family of capabilities for managing EC2 fleets, hybrid hosts, patching, runbooks, secrets, secure shell access, and (since 2024) the home of the migrated OpsWorks Stacks workloads.

## TL;DR
- An umbrella of capabilities, not one tool. The most-used pieces: **Session Manager** (shell access without SSH), **Run Command** (execute commands on instances), **Patch Manager** (managed patching), **State Manager** (desired-state config), **Automation** (runbooks), **Parameter Store** (covered separately in [`../security-identity/parameter-store.md`](../security-identity/parameter-store.md)).
- Replaces SSH bastion patterns with **Session Manager** (IAM-controlled, audit-logged, no inbound ports).
- **Inventory** + **Compliance** + **Patch Manager** + **State Manager** together cover most fleet-management needs.
- **OpsWorks Stacks ended May 26, 2024** and OpsWorks for Puppet / Chef Automate in early 2024 — Application Manager (a Systems Manager capability) is the migration target.
- **Automation runbooks** (SSM documents) are the codified operations primitive — restart a service, rotate a certificate, drain a node — invocable from Lambda / EventBridge / a human.

## When to use it
- Manage EC2 instances at scale (patching, config, shell access).
- Hybrid management — register on-prem servers as **SSM managed instances**.
- Replace SSH bastions with **Session Manager**.
- Codify runbooks via **SSM Automation documents**.
- Org-wide patching policy via **Patch Manager**.
- Inventory and compliance reporting on the EC2 fleet.

## When NOT to use it
- Pure container workloads — most SSM features target instances; ECS / EKS have their own analogs.
- Workloads that don't run on EC2 / on-prem — Parameter Store is the one SSM feature universally useful.
- Workloads where you've standardized on a third-party config management (Ansible, Salt, Puppet) and don't want to mix.

## Key capabilities

### Session Manager
- **Browser-based shell** or `aws ssm start-session` CLI.
- **IAM-authenticated, fully audit-logged** (every keystroke to S3 / CloudWatch Logs).
- **No SSH key distribution, no inbound ports, no bastion**.
- Port forwarding for accessing internal services (DB consoles, web UIs) through the SSM channel.
- The right replacement for SSH bastions in 2026.

### Run Command
- Execute predefined or ad-hoc commands across many instances.
- Targets by **instance ID**, **tag**, or **resource group**.
- Rate control + error threshold for staged rollouts.

### State Manager
- Define **associations** (a document + a target + a schedule) for desired-state config — install package, ensure service running, apply config file.
- Auto-remediate drift.
- Common pattern: pair with **AWS Config** for compliance reporting.

### Patch Manager
- Define **patch baselines** (rules for which patches to approve / deny).
- **Patch groups** (tag-based instance groups).
- **Maintenance windows** for scheduled patching.
- Cross-OS support (Linux, Windows, macOS).
- Critical-only patching for sensitive workloads.

### Automation
- **SSM documents** (YAML / JSON) define multi-step runbooks.
- Execute as Lambda / EventBridge / CloudWatch alarm targets.
- **AWS-managed automation documents** for common operations (restart EC2, rotate keys, encrypt EBS, snapshot, etc.).
- The codified-runbook primitive that lets on-call action be a single API call instead of a `kbd` page in Confluence.

### Inventory
- Periodic collection of installed software, OS info, network config, custom inventory items per instance.
- Searchable / queryable via the SSM console or Athena (Inventory → S3).

### Compliance
- Aggregate Patch + State Manager + Custom Compliance data into a unified compliance dashboard per resource.

### Maintenance Windows
- Schedule windows when Automation / Run Command / Patch Manager can run.
- Used to bound blast radius of routine operations.

### Application Manager
- Cross-service application view (CloudFormation stacks, ECS services, Lambda functions, EC2 instances tagged as an application).
- **Migration target for AWS OpsWorks Stacks** (which ended May 2024).
- Aggregates operational data per application.

### Parameter Store
Separately documented in [`../security-identity/parameter-store.md`](../security-identity/parameter-store.md) — hierarchical config / secret store; free Standard tier.

### Distributor
- Package and distribute software to instances at scale.
- Versioned packages installable via SSM Run Command.

### Change Calendar
- Define windows (open / closed) for production change activity.
- Automation respects calendar state — won't run during closed windows.

### Change Manager
- Approval workflow + audit trail for production changes.
- Integrates with State Manager / Automation.

### OpsCenter
- Centralized place for operational items (OpsItems) tied to events / alarms / findings.
- Replaces ad-hoc ticketing for AWS-internal operational issues.

### Quick Setup
- One-click setup for the canonical operational baseline (Session Manager + Inventory + Patch baseline + State Manager defaults) across an Organization.

### Fleet Manager
- Visual UI for the instance fleet — disk, processes, services, file system browse, restart — without SSH.

## Pricing model

- **Most Systems Manager features are free** (Session Manager, Run Command, State Manager, Patch Manager, Inventory, Maintenance Windows, Distributor, OpsCenter, Application Manager).
- **Advanced features** (Change Manager, Change Calendar) and **OpsCenter beyond the free tier** have per-OpsItem fees.
- **Automation document execution** — most AWS-published documents are free; some custom executions count toward Lambda / API call charges of downstream services.
- **Parameter Store** — see [Parameter Store page](../security-identity/parameter-store.md) (Standard tier free).

## Quotas & limits

- **Managed instances per account per Region**: high (thousands+).
- **Concurrent Run Command executions**: 100 default per account per Region.
- **Maintenance windows per account per Region**: 100.
- **Automation document size**: 64 KB.
- **Session Manager concurrent sessions**: instance-class dependent.

## Common pitfalls

- **SSH bastion left in place after Session Manager rollout.** Defeats the security gain; remove the bastion.
- **No automation runbooks for common ops.** Every restart / rotate / snapshot done manually = drift + error. Codify with SSM Automation.
- **Session Manager logging not enabled.** Default sessions aren't logged to S3/CloudWatch. Always enable.
- **Patch Manager with default baseline.** Default baselines patch broadly; for production, define your own baseline with explicit deny-lists / criticality filters.
- **One maintenance window for everything.** Different workloads have different acceptable downtime windows. Per-workload windows.
- **Inventory enabled but never queried.** Inventory data is most useful exported to S3 + queried via Athena for compliance reports.
- **Mixed SSM + manual SSH in production.** Pick one access model; mixed = unaudited access through whichever path is open.
- **OpsWorks-using workloads not migrated.** OpsWorks Stacks fully ended May 26, 2024; migrate to Application Manager.

## Pairs well with
- [Parameter Store](../security-identity/parameter-store.md) — the SSM-hosted config / secret tier.
- [EC2](../compute/ec2.md), on-prem hosts — managed instances.
- [CloudWatch](cloudwatch.md), [CloudTrail](cloudtrail.md) — observability of SSM activity.
- [EventBridge](../integration-messaging/eventbridge.md) — trigger Automation runbooks from events.
- [Lambda](../compute/lambda.md) — wrap Automation document invocations.
- [AWS Config](../security-identity/config.md) — Compliance + State Manager pair.
- [Secrets Manager](../security-identity/secrets-manager.md) — for rotated secrets (vs Parameter Store's simpler model).

## Pairs well with these repo pages
- [CloudWatch](cloudwatch.md), [CloudTrail](cloudtrail.md), [Config](../security-identity/config.md), [Parameter Store](../security-identity/parameter-store.md).
- [Operational Excellence pillar](../../05-well-architected/operational-excellence.md).

## Further reading
- [AWS Systems Manager documentation](https://docs.aws.amazon.com/systems-manager/).
- [Session Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html).
- [Patch Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-patch.html).
- [SSM Automation documents](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-automation.html).
- [Migrating OpsWorks Stacks to Systems Manager Application Manager](https://docs.aws.amazon.com/opsworks/latest/userguide/migrating-to-systems-manager.html).
- [Quick Setup](https://docs.aws.amazon.com/systems-manager/latest/userguide/quick-setup.html).
