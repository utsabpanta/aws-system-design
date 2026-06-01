# FSx

> **One-line summary.** Four managed file system flavors — Windows File Server, Lustre, NetApp ONTAP, OpenZFS — for workloads that need a specific filesystem feature set EFS can't provide.

## TL;DR

- FSx is a service family, not a single service. Each "flavor" is a managed version of a specific filesystem: **FSx for Windows File Server** (SMB), **FSx for Lustre** (HPC parallel filesystem), **FSx for NetApp ONTAP** (NAS with NetApp features), **FSx for OpenZFS** (POSIX with ZFS snapshots, clones, compression).
- Pick by feature requirement, not by performance number. Each flavor exists because a specific class of workload needed a feature the others (or EFS) couldn't provide.
- All flavors are multi-AZ-capable (with some single-AZ options for cost), KMS-encrypted at rest, backed up by AWS Backup, and reachable from any VPC-attached compute.
- The biggest gotcha across the family is networking — each FSx file system has a specific DNS name and SG; cross-VPC / cross-account access usually means VPC peering or AWS Transit Gateway.

## When to use it

- **FSx for Windows** — Active Directory–joined SMB shares for Windows apps (file shares, IIS log targets, .NET Framework apps).
- **FSx for Lustre** — HPC, ML training, video rendering, financial modeling — anywhere a parallel filesystem with sub-ms latency and hundreds of GiB/s throughput matters. Native S3 import/export.
- **FSx for NetApp ONTAP** — lift-and-shift NetApp workloads, multi-protocol (SMB + NFS) shares, instant zero-byte clones, deduplication, snapshots, SnapMirror replication.
- **FSx for OpenZFS** — POSIX NFS with ZFS features (snapshots, clones, compression, large recordsize). Modern, open, lower licensing baggage than ONTAP for greenfield POSIX needs.

## When NOT to use it

- A "plain" Linux NFS share — use **EFS** instead, which has a much simpler operational model.
- Object storage — use **S3**.
- Single-instance block storage — use **EBS**.
- Cheap cold archive — use **S3 Glacier**, not an idle FSx for OpenZFS.

## Key concepts

### FSx for Windows File Server

- **SMB 2.0 / 3.x**, integrated with **AWS Managed Microsoft AD** or your self-managed AD.
- Single-AZ or **Multi-AZ** with synchronous replication and automatic failover.
- **Distributed File System (DFS) Namespaces** for global namespace across multiple file systems.
- Supports **Data Deduplication**, **Volume Shadow Copies**, **ACLs** (Windows-style).
- Storage tiers: **SSD** (low latency) or **HDD** (cheaper, ~3× lower IOPS).
- Replication: **AWS DataSync** for cross-Region copies.

### FSx for Lustre

- **POSIX parallel filesystem**, designed for HPC.
- Throughput scales with capacity (50–1,000 MB/s per TiB) — provisioned at file-system creation.
- **Scratch** (single-AZ, no replication, lower-cost, intended ephemeral) vs **Persistent** (SSD, durable, multi-AZ available on newer deployment options).
- **Native S3 linkage** — import objects from S3 into Lustre, work on them, export back. Used heavily in genomics, video, ML training pipelines.
- Mount via Lustre client (Linux only). Latency: sub-ms. Throughput: hundreds of GiB/s on large file systems.

### FSx for NetApp ONTAP

- Full NetApp ONTAP — SMB, NFS v3/v4.1, **iSCSI**, plus NetApp-specific features (FlexVols, Snapshots, FlexClones, SnapMirror, SnapVault, deduplication, compression).
- Multi-AZ HA pairs with automatic failover.
- **Storage tiering** — frequently-accessed blocks on SSD, cold blocks tiered to S3 (capacity pool).
- The right answer when you're migrating from on-prem NetApp and want the same admin tooling; also the cleanest multi-protocol (SMB + NFS) story on AWS.

### FSx for OpenZFS

- POSIX NFS (v3 / v4 / v4.1 / v4.2), multi-protocol via dual-deployment with SMB possible.
- **Snapshots, clones, compression** out of the box — ZFS's headline features without operating it yourself.
- **Single-AZ HA, Multi-AZ HA**, and standard single-AZ deployments.
- Up to ~1M+ IOPS and ~21 GB/s throughput on the largest configurations.
- Often the right "modern POSIX" choice for ML datasets, genomics, build farms, and dev environments needing snapshots/clones — without NetApp licensing.

### Common to all

- **Backups** via AWS Backup with cross-Region copy and Vault Lock support.
- **KMS** encryption at rest, TLS-in-transit where the protocol supports it.
- **VPC-attached**, with per-AZ ENIs that clients connect to.

## Pricing model

- **Storage** per GB-month, flavor- and tier-dependent.
- **Throughput / IOPS** — Lustre and NetApp price throughput separately; Windows / OpenZFS often roll throughput into storage tier.
- **Backups** per GB-month of backup storage.
- **Data transfer** — same AWS rules (cross-AZ chatter, NAT egress).
- **NetApp ONTAP capacity pool (S3 tiering)** is much cheaper per GB than SSD; tier aggressively for cold data.

FSx is typically more expensive per GB than EFS or S3. The price is for the protocol / feature set, not the raw storage.

## Quotas & limits

Each flavor has its own quotas (defaults are raise-on-request):

- **Max file system size**: hundreds of TiB across most flavors; PB-scale for Lustre.
- **Throughput per file system**: from GB/s (Windows / OpenZFS at upper tiers) to hundreds of GiB/s (Lustre).
- **Concurrent connections**: thousands.
- **File systems per account per Region**: typically 100 default.
- **Lustre client compatibility** — Linux only, specific Lustre client version per AWS docs.

## Common pitfalls

- **Reaching for FSx when EFS suffices.** EFS is simpler, multi-AZ by default, cheaper for most NFS use cases. FSx makes sense for the specific features above, not as "EFS but better."
- **Single-AZ Multi-Workload for production.** Some FSx flavors default to single-AZ; for production, opt for Multi-AZ where supported.
- **Lustre Scratch as durable storage.** Scratch is intentionally lower-cost and lower-durability; treat it as a working set fed from S3.
- **Cross-Region access without replication.** FSx mount targets are Region-scoped. Cross-Region access means replicating (DataSync, SnapMirror) into a target file system in the other Region.
- **Missing AD integration plan for Windows / NetApp SMB.** Both rely on AD for authentication; provision Managed AD or wire to existing AD before creating the file system.
- **Not tiering NetApp capacity pool.** A NetApp file system that keeps everything on SSD is dramatically more expensive than one that tiers cold blocks to the capacity pool (S3-backed).
- **No backups configured.** None of the FSx flavors back themselves up automatically beyond a default daily snapshot in a small window — wire up AWS Backup with cross-Region copy and Vault Lock for anything important.
- **Lustre client version mismatch.** Production Lustre clients pinned to outdated versions get strange errors when AWS updates the server side. Track the supported client version explicitly.

## Pairs well with

- **AWS Managed Microsoft AD** — directory for FSx Windows / NetApp SMB.
- **AWS Backup** — managed backup with cross-Region copy.
- **AWS DataSync** — bulk migrations to/from FSx.
- **S3** — both Lustre and NetApp ONTAP integrate with S3 (Lustre import/export; ONTAP capacity pool tiering).
- **EC2 / ECS / EKS** — the compute that mounts the file system.

## Pairs well with these repo pages

- [EFS](efs.md) — the simpler NFS alternative for general POSIX workloads.
- [S3](s3.md) — the object store underneath Lustre/ONTAP tiering, and the right answer when POSIX isn't required.

## Further reading

- [Amazon FSx documentation hub](https://docs.aws.amazon.com/fsx/).
- [FSx for Windows File Server](https://docs.aws.amazon.com/fsx/latest/WindowsGuide/).
- [FSx for Lustre](https://docs.aws.amazon.com/fsx/latest/LustreGuide/).
- [FSx for NetApp ONTAP](https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/).
- [FSx for OpenZFS](https://docs.aws.amazon.com/fsx/latest/OpenZFSGuide/).
- [Lustre + S3 data repository associations](https://docs.aws.amazon.com/fsx/latest/LustreGuide/overview-dra-data-repo.html).
