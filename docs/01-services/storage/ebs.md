# EBS (Elastic Block Store)

> **One-line summary.** Network-attached block storage for EC2. Persistent, snapshot-able, multi-AZ via snapshots, and the default place to put a database that needs durable disk.

## TL;DR

- The "EC2 hard drive" — but on the other side of a fast network, so it survives the instance and can be detached/reattached.
- **`gp3` is the default for everything in 2026.** A 2025 update bumped it to up to **80,000 IOPS** and **2,000 MiB/s**, closing most of the historical gap with io1/io2.
- **`io2 Block Express`** for the workloads that genuinely need sub-ms latency, > 80k IOPS, or 99.999% durability — the highest in EBS.
- Snapshots are incremental, S3-backed, and the standard mechanism for backup and AMI creation. EBS Multi-Attach (io1/io2 only) lets multiple instances mount the same volume; almost never the right answer.
- Cost surprises: unattached volumes still bill (and accumulate from terminated instances), snapshots accumulate forever without a lifecycle policy.

## When to use it

- The boot volume for any EC2 instance.
- Single-instance databases (RDS uses EBS under the hood; self-managed Postgres / MySQL / Mongo on EC2 lives on EBS).
- Application working storage that needs to outlive a single instance (queue persistence, cache snapshots, build artifacts).
- Anywhere you'd reach for "a disk."

## When NOT to use it

- Shared filesystem across many instances — use **EFS** (NFS) or **FSx**, not EBS Multi-Attach.
- Object-shaped data — use **S3**; EBS is the wrong unit of access (and storage cost) for that.
- Truly ephemeral high-perf scratch — **instance store** (NVMe local to the host) is faster and cheaper-per-GB if you don't need durability.

## Key concepts

**Volume** — the disk. AZ-scoped (lives in one AZ; an instance in another AZ can't mount it). Attached to one instance at a time (unless Multi-Attach is enabled on io1/io2).

**Volume types (2026):**

| Type | Tier | IOPS (max) | Throughput (max) | Size | When to use |
|---|---|---|---|---|---|
| **gp3** | SSD | 80,000 (paid above 3,000 baseline) | 2,000 MiB/s (paid above 125) | 1 GiB – 64 TiB | **Default for almost everything.** Cheaper and faster than gp2. |
| gp2 | SSD | 16,000 | 250 MiB/s | 1 GiB – 16 TiB | Legacy. Migrate to gp3. |
| **io2 Block Express** | SSD | 256,000 | 4,000 MiB/s | up to 64 TiB | Tier-1 databases needing sub-ms p99 or > 80k IOPS. 99.999% annual durability. |
| io2 | SSD | 64,000 | 1,000 MiB/s | up to 16 TiB | Older flavor; pick io2 BE on supporting instances. |
| io1 | SSD | 64,000 | 1,000 MiB/s | up to 16 TiB | Legacy. Migrate to io2. |
| st1 | HDD | — (throughput-optimized) | 500 MiB/s | 125 GiB – 16 TiB | Sequential big-block workloads — data warehouse staging, log ingestion. |
| sc1 | HDD | — (cold) | 250 MiB/s | 125 GiB – 16 TiB | Infrequently accessed cold data on block. |

**Snapshots** — point-in-time, S3-backed, incremental (only changed blocks since the last snapshot are stored). Cross-Region copy is supported. **Fast Snapshot Restore (FSR)** pre-warms a snapshot in target AZs so volumes restored from it have no first-touch latency penalty.

**EBS-optimized instance** — almost all modern instance types are EBS-optimized by default (dedicated bandwidth to EBS, separate from network traffic). The instance type bounds the EBS throughput you can use — an `m5.large` is capped well below an `m5.4xlarge` regardless of the volume's spec.

**Encryption** — KMS-backed. Enable **EBS encryption by default** at the account level; the cost is zero and turning it on later is harder.

**Multi-Attach** — io1 / io2 only; up to 16 Nitro instances can mount the same volume. Useful narrowly for cluster filesystems (GFS2, OCFS2) that handle their own locking. Don't use it as "EFS for EBS" — POSIX semantics across attachers are your problem.

**Instance store vs EBS** — instance store NVMe (i, d, im, is, p4d, etc. families) is local to the host. Faster (microseconds), cheaper per GB, and *ephemeral* — data is gone on stop or host failure. Right for caches, scratch, shuffle. Wrong for anything durable.

## Pricing model

- **Storage** — per GB-month. gp3 is roughly 20% cheaper than gp2 for the same size at the baseline performance.
- **Provisioned IOPS / throughput** above the gp3 baseline (3,000 IOPS / 125 MiB/s) — paid per unit-month.
- **io2 / io2 BE** — per GB-month + per provisioned IOPS-month.
- **Snapshots** — per GB-month of changed blocks stored. Cross-Region snapshot copy charges data transfer.
- **FSR (Fast Snapshot Restore)** — per AZ-hour while enabled.
- **Data transfer** — EBS-to-EC2 in the same AZ is free; cross-AZ EBS access isn't normally a thing (a volume is single-AZ).

## Quotas & limits

- **gp3** — 80,000 IOPS / 2,000 MiB/s max, 64 TiB max.
- **io2 Block Express** — 256,000 IOPS / 4,000 MiB/s, 64 TiB. Supported only on Nitro instances with adequate EBS bandwidth.
- **Volume size** — capped per type.
- **Snapshots per Region** — high (10,000+) but accumulating snapshots without lifecycle is the bill killer, not the limit.
- **Concurrent snapshot copies** — bounded; large fan-out copy jobs should batch.
- **Volume modifications per volume** — one in-flight at a time; subsequent mods must wait.

## Common pitfalls

- **gp2 for new volumes.** gp3 is cheaper *and* faster. The modification is online and free. Just migrate.
- **Provisioning IOPS you can't use because the instance is too small.** EBS throughput is capped by the instance's EBS bandwidth. Right-size the instance with the volume; running 80k IOPS through an `m5.large` won't work.
- **Snapshots without a lifecycle policy.** Snapshots accumulate forever; bill grows linearly. Use **Data Lifecycle Manager (DLM)** to schedule snapshots and retention, or **AWS Backup** for cross-Region / cross-account policies.
- **Unattached volumes from terminated instances.** Set "delete on termination" on the launch template / ASG; audit with Trusted Advisor periodically.
- **No EBS encryption by default.** Turn it on at the account level; new volumes get encrypted automatically. Existing unencrypted volumes need snapshot → copy with encryption → restore.
- **Multi-Attach as "shared filesystem."** It's a cluster volume for cluster-aware filesystems only. POSIX-shared, single-writer is **EFS** or **FSx**.
- **HDD volumes (st1 / sc1) for random I/O.** They're throughput-optimized for sequential. Random reads tank.
- **Ignoring io2 Block Express for database tier-1.** If you're on io1 / io2 (non-BE), upgrade — it's typically a clear performance win on supported instances.

## Pairs well with

- [EC2](../compute/ec2.md) — almost always the consumer.
- **Data Lifecycle Manager (DLM)** — scheduled snapshots and retention.
- **AWS Backup** — cross-Region / cross-account / vault-locked backups.
- **EC2 Image Builder** — golden AMIs (built on EBS snapshots).
- **KMS** — encryption keys.
- **CloudWatch + EBS metrics** — `VolumeReadOps`, `VolumeWriteOps`, `BurstBalance`, `VolumeQueueLength` are the load-bearing operational metrics.

## Further reading

- [Amazon EBS documentation](https://docs.aws.amazon.com/ebs/).
- [EBS volume types](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-volume-types.html).
- [gp3 vs gp2 migration](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-modify-volume.html).
- [io2 Block Express](https://aws.amazon.com/ebs/provisioned-iops/).
- [Snapshot lifecycle with DLM](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/snapshot-lifecycle.html).
- Amazon Builders' Library — "Caching challenges and strategies" (when you need EBS-backed disk vs a cache).
