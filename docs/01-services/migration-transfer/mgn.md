# MGN (Application Migration Service)

> **One-line summary.** Managed server / VM lift-and-shift migration to AWS. Replicate source servers (physical, VMware, Hyper-V, other clouds) to EC2 with minimal downtime; cut over when ready.

## TL;DR

- Block-level replication of running servers to AWS EC2. Source can be physical, VMware, Hyper-V, EC2 in another account / Region, Azure, GCP — anything with the lightweight **AWS Replication Agent** installed (or agentless via VMware vCenter).
- **Continuous replication** to a staging area in AWS; test cutovers without disrupting source; final cutover converts the replicated disks into running EC2 instances in minutes-to-hours.
- **Linux / Windows** server migrations; lifts the OS, all installed software, all data, network configuration as a working EC2 instance.
- Pairs with **DMS** (databases), **DataSync** (files), **Migration Hub / AWS Transform** (assessment + orchestration) for end-to-end migration programs.
- The right service for "rehost" (lift-and-shift) migrations; if you're refactoring / modernizing, you'd use it less or not at all.

## When to use it

- Lift-and-shift migration of on-prem servers (data center evacuation, post-acquisition consolidation, VMware exit).
- Cross-cloud migration (Azure / GCP → AWS).
- EC2-to-EC2 migrations (cross-account, cross-Region) when AWS-native snapshot copy isn't enough.
- Disaster recovery setups where MGN-as-DR replication is the warm-standby tier (AWS Elastic Disaster Recovery — DRS — is a sibling product specifically for DR).

## When NOT to use it

- Database migrations — use **DMS**.
- Pure file migrations — use **DataSync**.
- Greenfield workloads — there's nothing to migrate; build native on AWS.
- Modernization (containerize, rearchitect) — MGN gets you to AWS as a VM; modernization is a separate phase (often Strangler Fig style, using **AWS Transform** for assessment).

## Key concepts

### Replication

- **AWS Replication Agent** — lightweight, installed on the source server. Block-level continuous replication to a staging area in your AWS account.
- **Agentless replication** — for VMware vSphere (vCenter 7.0/8.0), use the **MGN VMware Connector** instead of installing per-VM agents.
- Replication is **continuous** — the source keeps running; replication catches up in near-real-time.

### Source server lifecycle

1. **Add source** — via agent or connector.
2. **Replication** — initial sync (hours-days for big disks) + ongoing.
3. **Test launch** — spin up a test EC2 instance from the replicated disks, validate.
4. **Cutover** — final sync, stop source, launch production EC2.
5. **Archived** — source marked done; replication can stop.

### Wave / application grouping

- **Applications** — group source servers logically.
- **Waves** — sequence applications for batch cutovers (e.g., "all of Wave 1 cuts over together").

### Post-launch actions

- Run scripts on the new EC2 instance after launch (install agents, change config, register with monitoring).
- Built-in post-launch actions: install SSM Agent, run CloudWatch agent install, etc.

### Supported sources

- **Operating systems**: Windows Server 2012, 2016, 2019, 2022 (some 2008 / 7 support remaining until 2026-12-30 — verify per OS).
- **Linux**: most modern distributions (RHEL, CentOS, Amazon Linux, Ubuntu, SUSE, Debian — note: **Debian 6-9 support ends 2026-04-30**).
- **Cloud sources**: AWS (cross-account/region), Azure, GCP, OCI.
- **On-prem**: VMware, Hyper-V, physical servers.

### Recent (2026) features

- **AWS Transform integration** (Mar 2026) for AI-assisted migration / modernization.
- **EBS snapshots stored in Local Zones** (where supported).
- **UEFI boot mode** retention during migration.
- **MGN connector** can communicate with Windows servers over HTTP and authenticate Linux with password.

### OS deprecation notes

- **Windows 2003** — no longer supported as of 2026-02-15.
- **Windows 2008 / Windows 7** — support ends 2026-12-30.
- **Debian 6.x–9.x** — support ends 2026-04-30.

### AWS Elastic Disaster Recovery (DRS)

A sibling service using similar replication technology, specifically for disaster recovery (not migration). For warm-standby cross-Region DR setups, evaluate DRS instead of MGN.

## Pricing model

- **Free** for the first 90 days per source server (the migration window).
- **Beyond 90 days**: per-source-server-per-hour fee (the staging area).
- **Underlying AWS resources** (EBS snapshots, EBS volumes for staging, EC2 once cut over, data transfer) billed normally.

The 90-day free window is generous for typical migrations. Servers stuck in replication beyond that incur ongoing cost — close out cutovers promptly.

## Quotas & limits

- **Source servers per account per Region**: 1,000 default (raisable).
- **Applications per account per Region**: bounded; high.
- **Concurrent test / cutover launches**: bounded.
- **Replication throughput**: depends on instance class chosen for the staging area and your source's network bandwidth.

## Common pitfalls

- **Replication agent on production servers without testing.** Install on test instances first; verify minimal impact on source performance.
- **No bandwidth plan from on-prem.** Initial replication can take days for large fleets. **Direct Connect** dramatically speeds this; without it, plan for weeks on slow links.
- **Cutover without test launches.** Test the launched instance for application correctness before the real cutover.
- **OS version on the deprecation list.** Verify before starting; AWS may not replicate the OS or AWS support may end mid-project.
- **Post-launch actions skipped.** New EC2 instances need agents, monitoring, IAM roles configured. Use built-in or custom post-launch actions.
- **Not using waves.** Manual cutover of dozens of servers is error-prone. Use the wave/application model for orchestrated cutovers.
- **Leaving sources in MGN past 90 days.** Bills accumulate. Cut over and archive promptly.
- **Confusing MGN with DRS.** MGN is for migration to AWS; DRS is for ongoing DR replication. Pick the right one.

## Pairs well with

- [DMS](dms.md) — databases.
- [DataSync](datasync.md) — files.
- [Migration Hub](migration-hub.md) — assessment + orchestration.
- **AWS Transform** — AI-assisted migration planning.
- [Direct Connect](../networking/direct-connect.md) — fast replication path from on-prem.
- [Systems Manager Application Manager](../observability/systems-manager.md) — operational view of migrated apps.
- **AWS Elastic Disaster Recovery (DRS)** — sibling for DR.

## Pairs well with these repo pages

- [DMS](dms.md), [DataSync](datasync.md), [Migration Hub](migration-hub.md), [Application Discovery Service](application-discovery-service.md).

## Further reading

- [AWS Application Migration Service (MGN) documentation](https://docs.aws.amazon.com/mgn/).
- [Supported operating systems](https://docs.aws.amazon.com/mgn/latest/ug/Supported-Operating-Systems.html).
- [Agentless VMware replication](https://docs.aws.amazon.com/mgn/latest/ug/agentless-replication.html).
- [Post-launch actions](https://docs.aws.amazon.com/mgn/latest/ug/post-launch-actions.html).
- [AWS Elastic Disaster Recovery (DRS)](https://docs.aws.amazon.com/drs/).
