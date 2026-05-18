# EFS (Elastic File System)

> **One-line summary.** Managed, multi-AZ NFS v4.1 file system. POSIX semantics, mountable from EC2, ECS, EKS, and Lambda. Pay only for the bytes you store and (optionally) the throughput you use.

## TL;DR
- The right answer when you need a shared POSIX filesystem on AWS. Mountable from many compute targets simultaneously, multi-AZ by default.
- **Elastic Throughput** mode is now the default — throughput scales automatically with workload, pay per use. Replaces the old Bursting / Provisioned debate for most teams.
- Two storage classes (**Standard** multi-AZ, **One Zone** single-AZ), each with an **IA** (Infrequent Access) tier that lifecycle-policies move cold data into for ~85% lower storage cost.
- Cheaper than running your own NFS server; usually more expensive per GB than EBS or S3. Right when you need the *file* abstraction, not when you're using it as a fallback "shared disk."
- Lambda's native EFS mount makes EFS the standard way to share gigabyte-sized files (models, datasets, libraries) between Lambdas without per-invocation download cost.

## When to use it
- Container or EC2 workloads needing a shared POSIX filesystem (legacy apps, CMS uploads, build artifacts shared across CI workers).
- Lambda functions that need access to large files (ML models, large dependencies) without re-downloading per cold start.
- Home directories for analytics / dev environments.
- High-concurrency read workloads where many compute targets read the same files.

## When NOT to use it
- A database backing store. EFS adds NFS overhead and is much more expensive per IOPS than EBS. RDS uses EBS for a reason.
- Object-shaped data — use S3 (with Mountpoint for S3 if you really need POSIX-ish access).
- Latency-critical small-file workloads. EFS adds NFS round-trip overhead; sub-ms latency isn't its strength.
- Single-instance workloads — EBS is cheaper, simpler, faster.

## Key concepts

**File system** — the top-level resource. Region-scoped. Has a DNS name (`fs-xxx.efs.<region>.amazonaws.com`); mount via standard NFS client or the **EFS mount helper** (which handles IAM auth, encryption-in-transit setup, retries).

**Mount targets** — per-AZ ENIs that NFS clients connect to. Create one per AZ you want to mount from. Each has its own security group.

**Storage classes:**
- **Standard** — multi-AZ, the default.
- **One Zone** — single-AZ, ~47% cheaper. Use for non-critical / reproducible data.
- Both have a corresponding **IA (Infrequent Access)** tier for cold data, and an **Archive** tier (introduced for long-term archival, even cheaper). Lifecycle policies move files automatically based on access time.

**Throughput modes:**
- **Elastic** (default) — throughput auto-scales with workload. Pay only for the throughput you use (per GB read/written). Best for spiky or unpredictable load. Recommended default in the EFS console.
- **Provisioned** — fixed throughput in MiB/s regardless of file system size. Pay per provisioned MiB/s. Use when you need guaranteed throughput independent of usage spikes.
- **Bursting** — baseline throughput proportional to file system size (50 KiB/s per GB), with burst credits. Free (included in storage). Fine for small / steady workloads; doesn't scale well.

**Performance modes** (set at creation, can't change):
- **General Purpose** — lowest latency. The default; right for almost everything.
- **Max I/O** — higher aggregate throughput, higher per-operation latency. Niche; effectively legacy.

**IAM authorization** — mount with `iam` and `tls` options to require an IAM role and TLS in transit. **Access Points** scope mounts to a sub-directory and a UID/GID, useful for multi-tenant or container scenarios.

**Replication** — EFS supports cross-Region (and cross-account) replication to a target file system, with continuous async replication. RPO ~minutes; good enough for most DR.

## Pricing model

- **Storage** — per GB-month, class-dependent (Standard > One Zone, and each has IA / Archive tiers ~85–95% cheaper).
- **Elastic Throughput** — per GiB read and per GiB written.
- **Provisioned Throughput** — per MiB/s-month above the baseline included with storage.
- **Bursting** — free (included with storage).
- **Lifecycle transitions** — free.
- **Cross-Region replication** — destination storage + cross-Region transfer.

Elastic Throughput plus the IA tier (with lifecycle policy) is the configuration most teams should default to — pay for what you use, archive cold data automatically.

## Quotas & limits

- **File systems per account per Region** — 1,000 default.
- **Connected NFS clients** — up to 25,000 per file system.
- **Throughput** — up to 20+ GiB/s aggregate per file system (Elastic / Provisioned).
- **IOPS** — up to ~55,000 read / ~25,000 write at the file-system level (varies by Region and mode).
- **Max file size** — 47.9 TiB.
- **Mount targets per AZ** — 1.
- **Lambda concurrent mounts** — high; the bottleneck is usually mount-target ENI capacity, not Lambda concurrency.

## Common pitfalls

- **EFS as a database disk.** NFS overhead + per-GB-read/write pricing destroys both performance and cost. Use EBS.
- **Bursting mode in production at scale.** Burst credits run out; throughput drops to a tiny baseline. Use Elastic Throughput unless you can model it precisely.
- **No lifecycle policy.** Cold data sits in Standard burning storage cost. A simple "Standard → IA after 30 days, Archive after 90" policy saves 70%+ on typical workloads.
- **No mount target in one of the AZs you're using.** Cross-AZ EFS mounts work but pay cross-AZ data transfer. Create one mount target per AZ that has clients.
- **Encryption-in-transit off.** EFS supports TLS via the mount helper; turn it on.
- **No IAM auth.** Without it, anyone with VPC routing and a port-2049 SG hole can mount. Use IAM auth + Access Points.
- **Forgetting Access Points for multi-tenant containers.** They give per-tenant root directory and UID/GID, simpler than per-file POSIX permissions.
- **Cross-Region replication as your only DR.** Recovery point objective is ~minutes; for tight RPO you need a sync-replicating store (DB) or app-level dual-write.

## Pairs well with
- [EC2](../compute/ec2.md), [ECS](../compute/ecs.md), [EKS](../compute/eks.md), [Lambda](../compute/lambda.md) — all mount EFS natively.
- **DataSync** — bulk migrate to/from EFS (from on-prem NFS, S3, other EFS, FSx).
- **Backup** — managed EFS backups with vault locking.
- **EFS CSI driver** for EKS — dynamic provisioning of EFS-backed PersistentVolumes.

## Pairs well with these repo pages
- [S3](s3.md) — the alternative when you don't need POSIX semantics.
- [FSx](fsx.md) — when you need SMB (Windows), high-performance HPC (Lustre), or NetApp ONTAP features.
- [EBS](ebs.md) — when only one instance needs the disk.

## Further reading
- [Amazon EFS documentation](https://docs.aws.amazon.com/efs/).
- [EFS performance modes and throughput modes](https://docs.aws.amazon.com/efs/latest/ug/performance.html).
- [EFS lifecycle management](https://docs.aws.amazon.com/efs/latest/ug/lifecycle-management-efs.html).
- [EFS replication](https://docs.aws.amazon.com/efs/latest/ug/efs-replication.html).
- [EFS for Lambda](https://docs.aws.amazon.com/lambda/latest/dg/configuration-filesystem.html).
