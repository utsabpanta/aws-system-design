# Storage Gateway

> **One-line summary.** Hybrid cloud storage — an on-prem (or VM) appliance that presents standard storage protocols (NFS / SMB / iSCSI / VTL) to local clients and stores the data in S3, EBS snapshots, or FSx behind the scenes.

## Status

Storage Gateway is **active**, but the underlying appliance OS is migrating:

> ⚠️ **Amazon Linux 2 (AL2) gateway appliances are being retired.** As of **January 5, 2026**, AWS restricts new AL2 gateway activations. On **June 30, 2026**, AL2-based gateways stop receiving software updates and AWS support ends. Affected: S3 File Gateway v1.x, Tape Gateway v2.x, Volume Gateway v2.x. **Migrate to the AL2023-based gateway version before June 30, 2026.** Existing AL2 gateways continue running after that date but unpatched.

## TL;DR
- The bridge between on-prem storage protocols and AWS cloud storage. Four flavors: **S3 File Gateway**, **FSx File Gateway**, **Volume Gateway**, **Tape Gateway**.
- The appliance runs on-prem as a VM (VMware/Hyper-V/KVM), on a hardware appliance, or in EC2. Local cache absorbs hot reads/writes; cold data lives in AWS.
- Right for hybrid scenarios: extending on-prem NAS into the cloud, replacing tape backup infrastructure, backing up on-prem workloads to S3, presenting cloud-stored files to legacy on-prem apps.
- The big planning item in 2026 is the **AL2 → AL2023 migration deadline (June 30, 2026)** — don't sleep on it.
- For pure cloud workloads (no on-prem footprint), Storage Gateway is the wrong choice — go directly to S3 / EBS / FSx / EFS.

## When to use it
- Existing on-prem servers need to read/write to AWS-hosted storage using their native protocol (SMB share for a Windows app, NFS for a Linux workload, iSCSI LUN for a legacy DB, VTL for tape-backup software).
- Migrating tape backup infrastructure to AWS (Tape Gateway replaces physical tape libraries; backup software thinks it's still talking to LTO).
- Extending on-prem NAS into the cloud for capacity expansion without changing client paths.
- Backing up on-prem files to S3 / Glacier with a cache for fast restores of recent files.

## When NOT to use it
- All-AWS workloads — use S3 / EBS / EFS / FSx directly.
- Real-time / synchronous replication between on-prem and cloud — Storage Gateway is asynchronous; for tight RPO, use database-native replication or DataSync with frequent runs.
- Bulk one-time migrations — use **DataSync** or **Snowball** instead; Storage Gateway optimizes for ongoing access, not one-shot migration.

## Key concepts

### Four gateway types

**S3 File Gateway** — NFS v3 / v4.1 / SMB v2 / v3. Files stored as S3 objects (one file = one object). Each file gets the S3 storage class you configure (Standard / IA / Intelligent-Tiering); use lifecycle policies for further tiering. Read-through and write-through caching on the local appliance.

**FSx File Gateway** — SMB only. Sits in front of an FSx for Windows File Server file system; provides a low-latency local cache for branch-office / remote-site access to a centrally-hosted FSx share.

**Volume Gateway** — presents iSCSI block volumes. Two modes:
- **Cached volumes** — primary data in S3, recent reads/writes cached locally. Cheap to expand.
- **Stored volumes** — primary data on-prem, snapshots backed up to AWS as EBS snapshots. Local performance, cloud backup.

**Tape Gateway** — Virtual Tape Library (VTL). Looks like an LTO tape changer to your backup software (NetBackup, Veeam, Backup Exec, etc.). Virtual tapes stored in S3 / Glacier / Deep Archive.

### Common across types
- **Local cache** — sized at deploy time on the appliance. Larger cache = better hit rate, more local hardware required.
- **Upload bandwidth limiting** — throttle how much WAN bandwidth the gateway can use.
- **CloudWatch metrics** — `CacheHitPercent`, `CloudBytesUploaded`, `CloudBytesDownloaded`, queue depth.
- **Activation** — gateway VM contacts AWS to associate with your account; uses an activation key.
- **Encryption** — KMS for at-rest; TLS in transit.
- **High availability on VMware** — failover via VMware HA when the appliance VM dies.

## Pricing model

- **Per-gateway hourly fee** — small, per gateway.
- **Storage** — at standard rates for the destination (S3 storage class, FSx, EBS snapshot).
- **Requests** — S3 request charges apply for files (S3 File Gateway), and for tape operations (Tape Gateway).
- **Data transfer** — egress from AWS to on-prem at standard internet rates.
- **Volume Gateway snapshots** — billed as EBS snapshots (incremental, S3-backed).
- **CloudWatch logs / metrics** — at standard rates.

The bill is usually dominated by the underlying S3 / EBS / FSx storage and the egress data transfer back to on-prem; the per-gateway hourly fee is minor.

## Quotas & limits

- **Gateways per account per Region**: 100.
- **File shares per S3 File Gateway**: 50.
- **iSCSI volumes per Volume Gateway**: 32 (cached), 32 (stored), 32 TiB per volume.
- **Virtual tapes per Tape Gateway**: 1,500 active.
- **Total virtual tape storage**: 1 PiB (cached layer).
- **Local cache disk per gateway**: appliance-specific; typically TiB-scale.

## Common pitfalls

- **AL2 retirement deadline.** Migrate to AL2023-based gateway versions before **2026-06-30**. Track via the [Storage Gateway AL2 to AL2023 migration campaign](https://docs.aws.amazon.com/filegateway/latest/files3/al2-to-al2023-migration.html).
- **Undersized cache.** A cache too small for the working set thrashes — every read becomes a cloud round-trip. Size by workload, monitor `CacheHitPercent`.
- **Network/WAN as the bottleneck.** Storage Gateway is fundamentally limited by the WAN link between on-prem and AWS. Large file workloads need Direct Connect for predictable throughput.
- **Using S3 File Gateway as a database backing store.** It's eventually-consistent across gateways and not a POSIX filesystem in the strict sense; databases will be unhappy.
- **One gateway as the SPOF.** No HA by default; the gateway VM is a single point. Use VMware HA or run gateways in pairs with active/passive failover.
- **Forgetting that S3 lifecycle still applies.** Files in an S3 File Gateway bucket are subject to whatever lifecycle policy you've set on the bucket. Restore-from-Glacier doesn't play well with always-on file access.
- **Tape Gateway with no retention plan.** Backup software's tape retention controls virtual tape lifecycle. Misconfiguration leaves expired tapes consuming S3 storage; or worse, deletes tapes you needed.
- **Stored-volume mode for capacity expansion.** Stored volumes keep all data on-prem; you don't gain capacity, you gain backup. Use cached volumes to expand capacity into S3.

## Pairs well with
- [S3](s3.md) and [Glacier tiers](glacier.md) — the destination for File Gateway and Tape Gateway data.
- [FSx](fsx.md) — what FSx File Gateway fronts.
- [EBS](ebs.md) — Volume Gateway snapshots land as EBS snapshots.
- **AWS DataSync** — for bulk migration before / alongside Storage Gateway.
- **Direct Connect** — predictable WAN throughput between on-prem and AWS.
- **AWS Backup** — manages Storage Gateway Volume Gateway snapshots.

## Pairs well with these repo pages
- [Backup](backup.md) — for backing up workloads served by Storage Gateway.
- `docs/04-reference-architectures/hybrid-on-prem-vpn.md` (forthcoming) — hybrid topologies.

## Further reading
- [AWS Storage Gateway documentation](https://docs.aws.amazon.com/storagegateway/).
- [Storage Gateway AL2 to AL2023 migration](https://docs.aws.amazon.com/filegateway/latest/files3/al2-to-al2023-migration.html).
- [S3 File Gateway](https://docs.aws.amazon.com/filegateway/latest/files3/).
- [Tape Gateway](https://docs.aws.amazon.com/storagegateway/latest/tgw/).
- [Volume Gateway](https://docs.aws.amazon.com/storagegateway/latest/vgw/).
