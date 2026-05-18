# DataSync

> **One-line summary.** Managed file / object transfer between on-prem (NFS / SMB / HDFS / S3-compatible) and AWS (S3 / EFS / FSx), or between AWS services. Faster, simpler, and more reliable than rolling your own `rsync` / scripts at scale.

## TL;DR
- The right service for **bulk and ongoing file movement** — initial dataset transfers, periodic sync from on-prem NAS, EFS-to-EFS replication, S3-to-S3 cross-account / cross-Region copy, HDFS-to-S3 dump.
- Built-in **incremental sync** (only changed files), **bandwidth throttling**, **task scheduling**, **encryption in transit** (TLS 1.2), **data validation** (per-file hash check), and **detailed reporting**.
- **Online transfer up to multi-GB/s** depending on source bandwidth and DataSync agent sizing — for sites with reasonable internet, DataSync usually beats Snowball Edge on simplicity and turnaround.
- Sources / targets include on-prem NFS / SMB / HDFS / Object Storage Server (S3-compatible), AWS S3 / EFS / FSx (all flavors), and DataSync Discovery for inventorying on-prem storage.
- **DataSync Discovery** assesses on-prem NFS / SMB storage and recommends AWS targets (often the prelude to a DataSync migration).

## When to use it
- Bulk one-time data transfer from on-prem to AWS (TB to PB at reasonable bandwidth).
- Periodic / continuous sync between on-prem NAS and S3 / EFS / FSx.
- EFS-to-EFS replication across Regions / accounts.
- S3 cross-Region / cross-account copies that need fine-grained scheduling and validation.
- HDFS migration to S3 for Hadoop cluster modernization.
- AWS Snowball Edge data, post-ingestion, syncing back to a different bucket.

## When NOT to use it
- Database migrations — use **DMS**.
- Server migrations — use **MGN**.
- Truly disconnected / very-low-bandwidth scenarios — **Snowball Edge** (DataSync still requires reasonable internet).
- Ongoing file-share access by applications (vs migration) — that's **Storage Gateway** or **EFS** / **FSx** with native mounting.

## Key concepts

### Locations
DataSync abstracts source / target as **locations**:
- **On-prem NFS** (v3 / v4 / v4.1).
- **On-prem SMB** (v2 / v3).
- **HDFS** (Hadoop FS).
- **Object Storage Server** (S3-compatible).
- **Amazon S3** (any storage class).
- **Amazon EFS**.
- **FSx for Lustre / Windows / NetApp ONTAP / OpenZFS**.
- **AWS Snowcone** (legacy device — note Snowcone is discontinued).

### Agents
- **DataSync agent** is a small VM (VMware / Hyper-V / KVM / EC2) installed at the source.
- Required for on-prem sources; the agent reads / writes to the on-prem source and ships to AWS over TLS.
- **No agent needed for AWS-to-AWS transfers**.

### Tasks
- A **task** ties a source location to a destination location with a sync configuration.
- **Schedule** — one-time or recurring (cron).
- **Filters** — include / exclude patterns.
- **Transfer mode** — `CHANGED` (sync changed files only, the default for incremental sync) or `ALL` (re-copy everything).
- **Verify mode** — verify checksums after transfer.
- **Bandwidth limit** — cap throughput per task.

### DataSync Discovery
- Read-only assessment of on-prem NFS / SMB storage clusters.
- Recommends AWS targets (S3 vs EFS vs FSx flavor) based on access patterns and capacity.
- Generates a migration plan; pairs with DataSync tasks for execution.

### Reports
- Per-task reports of files transferred / skipped / failed with reasons.
- Sent to S3 in CSV / JSON.

### Multi-region / multi-account
- Supports cross-Region S3 / EFS / FSx as source or destination.
- Cross-account via IAM role chaining + permissions on the target location.

### Encryption
- TLS 1.2 in transit.
- At-rest encryption inherits the destination's (S3 SSE, EFS KMS, FSx KMS).

## Pricing model

- **Per GB transferred** (the dominant cost).
- **Discovery** has its own per-storage-system-day fee.
- **Underlying AWS storage** (S3, EFS, FSx) billed normally.
- **DataSync agent compute** — if on EC2, EC2 cost; if VMware on-prem, your own infra.
- **No charge for incremental scanning** — only for actually-transferred data.

For multi-PB migrations, the per-GB cost adds up. Compare to **Snowball Edge** for very large transfers from disconnected sources.

## Quotas & limits

- **Tasks per account per Region**: 100 default.
- **Agents per account per Region**: 100 default.
- **Locations per account per Region**: 100 default.
- **Files per task**: tens of millions (very large file counts can hit task limits — split into multiple tasks).
- **Throughput per task**: up to several Gbps; depends on agent sizing and source bandwidth.

## Common pitfalls

- **Single task for hundreds of millions of files.** Task limits and scan time become problems. Split into multiple tasks by subtree or filter.
- **No bandwidth limit.** A DataSync task can saturate on-prem internet, hurting other workloads. Throttle.
- **Skipping the agent on-prem firewall.** The agent needs outbound HTTPS to AWS and inbound from your source. Misconfigured firewalls = silent failures.
- **`ALL` transfer mode in scheduled tasks.** Re-copies everything every run. Use `CHANGED` for incremental.
- **No verify mode.** Quiet corruption goes unnoticed. Enable verify in production.
- **Cross-account / cross-Region IAM not configured.** Permissions on the destination location must allow the DataSync service role. Easy to miss.
- **Treating DataSync as ongoing file-share access.** It's a sync / transfer service, not a live filesystem. Use Storage Gateway / EFS / FSx for that.
- **Forgetting Snowball Edge for genuinely huge / disconnected transfers.** For 100 TB+ from a remote site with slow internet, Snowball Edge is faster end-to-end.

## Pairs well with
- [S3](../storage/s3.md), [EFS](../storage/efs.md), [FSx](../storage/fsx.md) — AWS destinations.
- [Storage Gateway](../storage/storage-gateway.md) — for ongoing file-share access (different problem).
- [Snowball Edge](../edge/snow-family.md) — for genuinely disconnected / huge migrations.
- [DMS](dms.md), [MGN](mgn.md) — sibling services for databases / servers.
- [Migration Hub](migration-hub.md) — orchestration alongside DataSync.
- [Direct Connect](../networking/direct-connect.md) — predictable high-bandwidth path for large transfers.

## Pairs well with these repo pages
- [DMS](dms.md), [MGN](mgn.md), [Storage Gateway](../storage/storage-gateway.md), [Snowball Edge](../edge/snow-family.md).

## Further reading
- [AWS DataSync documentation](https://docs.aws.amazon.com/datasync/).
- [DataSync Discovery](https://docs.aws.amazon.com/datasync/latest/userguide/understanding-your-storage-environment.html).
- [Supported locations](https://docs.aws.amazon.com/datasync/latest/userguide/working-with-locations.html).
- [DataSync best practices](https://docs.aws.amazon.com/datasync/latest/userguide/best-practices.html).
- [DataSync pricing](https://aws.amazon.com/datasync/pricing/).
