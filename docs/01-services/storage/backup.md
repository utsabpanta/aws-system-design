# AWS Backup

> **One-line summary.** Centralized, policy-driven backup orchestration for most stateful AWS services — EBS, RDS, Aurora, DynamoDB, EFS, FSx, S3, Storage Gateway, Neptune, DocumentDB, EKS, and more.

## TL;DR
- One place to define backup schedules, retention, cross-Region copy, and cross-account copy across every backup-able AWS service. Replaces the per-service snapshot-cron sprawl.
- **Vault Lock** + **Compliance mode** + **logically air-gapped vaults** are the cyber-resilience trifecta — backups that even a compromised root account can't delete.
- **Restore testing** automatically validates that recovery actually works, on a schedule. A backup that's never been restored is not a backup.
- **AWS Backup Audit Manager** gives you organization-wide controls and dashboards — backup coverage, retention compliance, RPO compliance, air-gapped-vault usage.
- Costs are charged per GB of backup storage (warm + cold tiered) plus cross-Region transfer. Centralizing in a separate backup account is the canonical pattern.

## When to use it
- You operate any of the supported services and want a single backup policy plane.
- You need cross-Region and/or cross-account backup copies for DR or ransomware resilience.
- You have compliance requirements that demand WORM retention or air-gapped backups.
- You want to prove backups actually restore (Restore Testing).
- You need to centralize backup audit/reporting across an AWS Organization.

## When NOT to use it
- Continuous data replication (real-time, sub-second RPO) — AWS Backup is point-in-time snapshots, not streaming replication. Use service-native replication (Aurora Global, DynamoDB Global Tables, S3 Replication).
- Backup of services AWS Backup doesn't support (third-party SaaS, custom on-prem workloads not on Storage Gateway). Look at service-native tools.
- Application-consistent backups for unsupported applications — Backup uses crash-consistent snapshots for many sources; ensure your app tolerates that or quiesce before backup.

## Key concepts

**Backup plan** — the policy. Defines schedules (cron), lifecycle (move to cold storage after N days, expire after M days), copy actions (to other Regions / accounts), and assigned resources.

**Backup vault** — the destination. KMS-encrypted; access controlled via vault access policies.

**Vault Lock** — once enabled, the vault's retention policy (min/max retention) cannot be relaxed. Two modes:
- **Governance** — IAM users with `vaultlock:DeleteBackupVaultLockConfiguration` can override.
- **Compliance** — nobody can override or disable for the lock's lifetime, including root. Required for regulated workloads.

**Logically air-gapped vault** — a vault type with extra protection: each is encrypted with an AWS-owned or customer-managed KMS key, ships with Vault Lock Compliance mode, and can be **shared cross-account via AWS RAM** so a separate account (your "backup account") can restore *from* the vault directly without first copying. The post-2024 standard for cyber-resilient backup architectures. EKS support added in March 2026; now spans 24+ Regions.

**Restore testing plan** — schedules automated restores of recovery points to validate they actually restore. Tests can include PITR, multiple resource types, and a destination configuration (often a test account/VPC). Failures fire alarms. The only credible answer to "have you tested your DR?"

**AWS Backup Audit Manager** — organization-wide controls and reports. Pre-built controls include "all backups are encrypted," "backup frequency meets policy," "backups are stored in logically air-gapped vault," and "resource has minimum N restore points." Reports delivered to S3.

**Cross-account / cross-Region copy.** A backup plan can copy each recovery point to another vault in another Region and/or another account in the same step. The standard pattern: production account creates backups → copy action ships them to a "logical backup" account in the same Region for ransomware isolation and to another Region for DR.

**Supported resources (2026, abridged):** EBS, RDS (most engines), Aurora, DynamoDB, EFS, FSx (all flavors), S3, Storage Gateway, Neptune, DocumentDB, EKS, Timestream, Redshift, EC2 instance, VMware workloads via VMware Cloud on AWS, SAP HANA. Check the docs — the list grows quarterly.

## Pricing model

- **Warm storage** — per GB-month, varies by source service.
- **Cold storage** — per GB-month, much cheaper, with a 90-day minimum (or 180 days for some services).
- **Cross-Region copy** — per GB transferred.
- **Cross-account copy** — no transfer fee within the same Region; charged for the destination storage.
- **Restore** — per-GB restore charge for some sources (notably EFS); EBS/RDS restores are free.
- **Backup Audit Manager** — per evaluation.
- **Restore testing** — restore charges apply during testing; the testing plan itself is free.

The numbers are competitive with rolling your own snapshot cron, and the operational simplification is significant. The "logical backup account" pattern adds Region-internal storage costs but no transfer.

## Quotas & limits

- **Backup plans per account per Region**: 100.
- **Backup vaults per account per Region**: 100.
- **Concurrent backup jobs**: source-service-dependent.
- **Retention**: from days to ~100 years.
- **Recovery points per vault**: very high; the limits are practical (cost) not technical.

## Common pitfalls

- **No restore testing.** A backup you've never restored is folklore. Wire up Restore Testing Plans and treat failures as production incidents.
- **Vault in the same account as the source.** A compromised production account can delete its own vault. Centralize backups in a separate "logical backup" account with cross-account copy.
- **No Vault Lock.** Without it, an attacker with admin can rm-rf your backups. Lock vaults; use Compliance mode for regulated workloads.
- **No logically air-gapped vault for critical workloads.** A backup an attacker can encrypt or delete isn't a backup. Air-gapped vaults solve this without an offline tape robot.
- **Cold storage for short-lived backups.** 90- or 180-day minimum durations mean transitioning a 30-day-retention backup to cold storage costs *more*, not less. Lifecycle to cold only for genuinely long-retention backups.
- **No cross-Region copy.** A Region-wide event takes out both production and the backup if they're co-located. Cross-Region copy is the cheapest DR primitive AWS sells.
- **Default KMS key.** Use a customer-managed KMS key with explicit key policy — locks down who can decrypt restored data even if vault access leaks.
- **Forgetting EKS / new service-type support.** AWS Backup added support for new services regularly (EKS air-gapped vault in Mar 2026). Re-check coverage when new services land.
- **Backup Audit Manager not turned on.** Without it, "are we actually backing up everything we said we'd back up?" has no automated answer. Turn it on; ship reports to a central S3 bucket.

## Pairs well with
- [S3](s3.md) — backups for S3 buckets; also where Backup Audit Manager reports land.
- [Glacier tiers](glacier.md) — Backup's cold storage uses Glacier-class durability.
- **AWS Organizations + RAM** — share backup vaults across accounts.
- **AWS KMS** — encryption keys for vaults.
- **EventBridge** — react to backup job completion / failure events.
- **CloudWatch** — backup job metrics and alarms.

## Pairs well with these repo pages
- `docs/02-patterns/disaster-recovery-strategies.md` — where AWS Backup fits in the DR pattern catalog (forthcoming).
- [Reliability pillar](../../05-well-architected/reliability.md) — the operational practices behind making backups credible.

## Further reading
- [AWS Backup documentation](https://docs.aws.amazon.com/aws-backup/).
- [AWS Backup logically air-gapped vault](https://docs.aws.amazon.com/aws-backup/latest/devguide/logicallyairgappedvault.html).
- [Restore testing](https://docs.aws.amazon.com/aws-backup/latest/devguide/restore-testing.html).
- [AWS Backup Audit Manager](https://docs.aws.amazon.com/aws-backup/latest/devguide/aws-backup-audit-manager.html).
- [Building cyber resiliency with AWS Backup](https://aws.amazon.com/blogs/storage/building-cyber-resiliency-with-aws-backup-logically-air-gapped-vault/).
