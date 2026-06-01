# EMR (Elastic MapReduce)

> **One-line summary.** Managed Hadoop ecosystem on AWS — Spark, Hive, Presto / Trino, HBase, Flink, Hudi / Iceberg / Delta — running on EC2, EKS, Outposts, or **EMR Serverless**.

## TL;DR

- The right answer for large-scale Spark / Hive / Presto / Trino workloads that need full control of the cluster, custom packages, or specialized configurations.
- **Four deployment models**: **EC2 clusters** (classic), **EKS** (Kubernetes-managed pods), **Serverless** (no cluster — pay per job execution), **Outposts** (on-prem rack).
- **EMR Serverless** is the modern default for most "Spark job" workloads — no cluster to manage; auto-scales per job.
- For pure ad-hoc SQL on data lakes, **Athena** is usually simpler. EMR shines when you need Spark code, custom Hadoop ecosystems, or sustained heavy workloads.
- Spot-friendly: EMR's task instance fleets pair beautifully with Spot for 60–90% cost reduction on batch.

## When to use it

- Sustained, code-driven Spark / Hive / Presto / Trino workloads.
- Custom Hadoop ecosystem requirements (HBase, JupyterHub-on-cluster, custom JARs).
- ML preprocessing pipelines on tens of TB to PB datasets.
- Data lakehouse formats — **Apache Hudi / Iceberg / Delta Lake** are pre-bundled.
- EKS-resident data teams who want Spark-on-K8s under AWS management (EMR on EKS).
- Existing on-prem Spark / Hadoop being lifted to AWS.

## When NOT to use it

- Ad-hoc analytical SQL — **Athena**.
- Pure serverless Spark with minimal config — **Glue Spark jobs** or **EMR Serverless** (which is closer to Glue in operational shape).
- Real-time stream processing — **Managed Service for Apache Flink** (formerly Kinesis Data Analytics).
- Tabular analytics — **Redshift**.
- Tiny / occasional workloads — pay-per-cluster-hour for an EMR cluster doesn't amortize.

## Key concepts

### Deployment models

**EMR on EC2.** Classic. You provision a cluster (master + core + task nodes) on EC2. Lives until you terminate (or until idle, with auto-termination). Most flexible; most operational overhead.

**EMR on EKS.** Run Spark / Flink on an existing EKS cluster. EMR provides the Spark distribution, Hive metastore integration, and the job submission API; EKS handles the pod scheduling. Right for teams that already operate EKS.

**EMR Serverless.** No cluster. Submit a job; EMR provisions and tears down workers automatically. Pay per worker-hour while jobs run. Spark and Hive supported. The right default for "I just want to run Spark jobs" workloads.

**EMR on Outposts.** EMR clusters on your AWS Outposts hardware.

### Engines pre-bundled

- **Spark** — the primary engine in 2026.
- **Hive** — SQL on top of Hadoop.
- **Presto / Trino** — distributed SQL.
- **HBase** — wide-column NoSQL.
- **Flink** — stream processing (also available as Managed Apache Flink).
- **JupyterHub / Zeppelin** — notebooks on cluster.
- **Hudi / Iceberg / Delta Lake** — table formats.
- **Tez, MapReduce** — legacy frameworks (still supported).

### Cluster topology (EMR on EC2)

- **Primary (master) node** — coordinates the cluster.
- **Core nodes** — run HDFS DataNodes (storage) and tasks.
- **Task nodes** — task-only, no HDFS, ideal Spot candidates.

### Instance fleets

- **Uniform instance groups** — fixed instance type per node group.
- **Instance fleets** — mix multiple instance types and Spot/on-demand within one fleet; EMR picks optimally based on availability and price.

Instance fleets + Spot for task nodes is the canonical cost-optimized pattern.

### Storage

- **HDFS** on core nodes (lost on cluster termination) — for hot shuffle / intermediate data.
- **EMRFS** — Spark / Hive reads/writes S3 directly (the production pattern). HDFS as scratch only.
- **EBS volumes** attached to nodes for shuffle and OS.

### Auto-scaling

EMR clusters can auto-scale task nodes based on YARN metrics. EMR Serverless auto-scales transparently per job.

### Security

KMS encryption at rest (EBS, S3, HDFS), TLS in transit between cluster components, Kerberos auth optional. **Lake Formation** integration for fine-grained permissions.

## Pricing model

- **EMR on EC2** — EMR per-hour fee per node + underlying EC2 (or Spot) + EBS.
- **EMR on EKS** — small per-vCPU-hour EMR fee + your EKS cluster + node costs.
- **EMR Serverless** — per worker-vCPU-hour and per worker-GB-hour while the job runs.
- **EMR on Outposts** — EMR fee + your Outposts capacity.
- **Data transfer** — same AWS rules.

EMR on EC2 + Spot task nodes is the cheapest at sustained high utilization. EMR Serverless wins at low / variable utilization.

## Quotas & limits

- **Clusters per account per Region**: 50 default (raisable).
- **Nodes per cluster**: thousands (high).
- **Job concurrency (Serverless)**: bounded by application capacity (configurable).
- **Steps per cluster (EMR on EC2)**: 256 active.
- **Concurrent serverless applications**: bounded; raisable.

## Common pitfalls

- **EMR on EC2 for occasional jobs.** Per-hour cluster cost piles up. Use EMR Serverless.
- **Storing data in HDFS.** HDFS dies with the cluster. Use S3 (EMRFS) for durable data; HDFS as scratch only.
- **No Spot on task fleet.** Leaving 60–90% on the table.
- **Skipping Lake Formation integration.** Permissions managed at the cluster / S3 layer instead of the Catalog. Lake Formation centralizes this.
- **Old EMR release version.** EMR releases bundle specific Spark / Hive / Hadoop versions. Track current releases — newer Spark (3.5+) has meaningful performance improvements.
- **One huge cluster for everyone.** Multi-tenant clusters with mixed-priority jobs create starvation. Multiple smaller clusters or EMR Serverless per workload often work better.
- **EMR on EC2 instead of EMR on EKS when you already run EKS.** EKS-side has cluster autoscaling and bin-packing for free; running both is duplicate operational overhead.
- **No auto-termination.** A cluster left running overnight bills overnight. Set idle-timeout.

## Pairs well with

- [S3](../storage/s3.md), **S3 Tables** — primary data lake.
- [Glue](glue.md) — Catalog metastore for EMR.
- [Lake Formation](lake-formation.md) — fine-grained perms.
- [EKS](../compute/eks.md) — EMR on EKS host.
- [Step Functions](../integration-messaging/step-functions.md) — orchestrate EMR steps.
- **JupyterHub / SageMaker Studio** — notebook front-ends.

## Pairs well with these repo pages

- [Glue](glue.md), [Athena](athena.md), [Lake Formation](lake-formation.md).
- `docs/04-reference-architectures/batch-etl-glue.md`, `docs/04-reference-architectures/data-lake-on-s3.md` (forthcoming).

## Further reading

- [Amazon EMR documentation](https://docs.aws.amazon.com/emr/).
- [EMR Serverless](https://docs.aws.amazon.com/emr/latest/EMR-Serverless-UserGuide/).
- [EMR on EKS](https://docs.aws.amazon.com/emr/latest/EMR-on-EKS-DevelopmentGuide/).
- [EMR Spot integration](https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-instance-purchasing-options.html).
- [EMR release versions](https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-release-components.html).
