# Application Discovery Service (ADS)

> **One-line summary.** Inventory and analyze on-prem (or other-cloud) servers and applications before migrating. Agentless via VMware vCenter, or agent-based on individual servers. Feeds **Migration Hub** Strategy Recommendations and EC2 Instance Recommendations.

## TL;DR
- The "what do we have before we migrate?" service. Without this, planning is guesswork.
- Two collection modes: **Agentless Collector** (a VM deployed to your VMware vCenter that polls cluster info) and **Agent-based** (small agent installed on individual servers — Linux / Windows).
- Captures **server inventory** (CPU, RAM, OS, network interfaces), **performance data** (CPU / memory / network / disk over time), **process inventory**, **TCP connections** (to map dependencies between servers).
- Feeds **Migration Hub** — Strategy Recommendations, EC2 Instance Recommendations, application grouping all use ADS data.
- Data export to S3 / Athena for custom analysis.

## When to use it
- Before any non-trivial migration to AWS.
- Inventorying an on-prem estate after acquisition / for divestiture.
- Building a dependency map between servers (which talk to which).
- Right-sizing target EC2 instances based on actual usage (not provisioned size).

## When NOT to use it
- Already migrated workloads — ADS is for the pre-migration discovery phase.
- Cloud-resident workloads — use **AWS Config**, **Resource Explorer**, or your existing tooling.
- Tiny one-server migrations — manual inventory might be faster than installing ADS.

## Key concepts

### Agentless Collector
- A VM appliance deployed to your VMware vCenter.
- Polls vCenter for inventory + performance data on all VMs in the cluster.
- No per-VM agent install.
- Easiest for VMware-heavy environments.

### Discovery Agent
- Small agent installed on individual Linux / Windows servers.
- More detailed data than agentless (process inventory, TCP connections — the data needed for dependency mapping).
- Required for non-VMware on-prem servers (physical, Hyper-V) or any environment without vCenter.

### Import (file-based)
- Upload a CSV of servers if you've already inventoried via another tool.
- Limited fidelity vs agent / agentless.

### Data captured
- **Server**: hostname, OS family / version, CPU type / count, RAM, network interfaces, hypervisor.
- **Performance**: CPU / memory / network / disk metrics over time (minute / hour aggregation).
- **Process inventory** (agent only): running processes.
- **Network dependencies** (agent only): TCP source / destination / port / volume — used to map dependencies between servers.
- **Application metadata**: tags, app grouping.

### Application grouping
Servers can be grouped into **applications** logically (manually or by ML-suggested groupings from observed traffic patterns).

### Migration Hub integration
- ADS data automatically populates Migration Hub.
- **Strategy Recommendations** uses ADS data to recommend per-app modernization paths.
- **EC2 Instance Recommendations** uses ADS performance data to size target instances.

### Export to S3 / Athena
- Dump ADS data to S3 for custom analysis.
- Athena queries against the data for "show me all servers > 64 GB RAM running Java 8" style questions.

## Pricing model

- **ADS itself is free.**
- **Agentless Collector / Discovery Agent** are free.
- **Data storage in ADS** — free.
- **Export to S3** — pay S3 / Athena costs.
- **Migration Hub Strategy Recommendations / EC2 Instance Recommendations** are free; they consume ADS data.

The whole discovery side of migration is free; ADS removes that as a planning blocker.

## Quotas & limits

- **Servers per account**: bounded; high (tens of thousands).
- **Applications per account**: bounded.
- **Performance data retention**: 90 days default.
- **Data export size**: bounded by S3 capacity.

## Common pitfalls

- **Migration without discovery.** Plan-by-anecdote ("I think we have 200 servers") consistently underestimates / overestimates. Run ADS first.
- **Agentless-only collection in a non-VMware environment.** Discovery Agent is the only path for physical / Hyper-V / other-cloud sources.
- **Skipping the agent on key servers.** Dependency mapping needs TCP-connection data, which only agents provide. Skipping agents leaves you with no dependency map.
- **Treating ML-suggested application groups as final.** They're a starting point; validate with the application owners.
- **Short collection windows.** Performance data captured over a week underestimates monthly / quarterly peaks. Collect for at least 30 days, preferably 60-90.
- **Not exporting to S3 for custom analysis.** ADS console is OK for browsing; real planning queries belong in Athena.
- **Agent push to internet-restricted networks without considering proxies.** Discovery Agent needs outbound HTTPS to AWS; configure proxies if your environment requires it.
- **Forgetting ADS exists after migration.** Decommission the collector / agents on migrated servers.

## Pairs well with
- [Migration Hub](migration-hub.md) — the primary consumer of ADS data.
- [MGN](mgn.md) — server-by-server migration using ADS recommendations.
- [DMS](dms.md) — database-side counterpart for inventorying databases.
- **AWS Transform** — newer AI-driven evolution that uses ADS data.
- [S3](../storage/s3.md), [Athena](../analytics/athena.md), [QuickSight](../analytics/quicksight.md) — custom analysis of exported ADS data.

## Pairs well with these repo pages
- [Migration Hub](migration-hub.md), [MGN](mgn.md), [DMS](dms.md), [DataSync](datasync.md).

## Further reading
- [AWS Application Discovery Service documentation](https://docs.aws.amazon.com/application-discovery/).
- [Agentless Collector](https://docs.aws.amazon.com/application-discovery/latest/userguide/agentless-collector.html).
- [Discovery Agent](https://docs.aws.amazon.com/application-discovery/latest/userguide/discovery-agent.html).
- [Migration Hub Strategy Recommendations](https://docs.aws.amazon.com/migrationhub-strategy/).
- [EC2 Instance Recommendations](https://docs.aws.amazon.com/migrationhub/latest/ug/ec2-recommendations.html).
