# MWAA (Managed Workflows for Apache Airflow)

> **One-line summary.** Managed Apache Airflow — DAGs run on AWS-operated worker, scheduler, and web-server fleets in your VPC. Open-source Airflow, AWS does the operations.

## TL;DR
- The right answer when your data team already speaks Airflow and you want a managed equivalent on AWS without operating EKS-hosted Airflow yourself.
- Supports **Airflow 3.0** (latest, 2026) and **Airflow 2.11** (added January 2026). AWS commits to supporting at least three minor versions at any time; **Airflow 2.4.3 / 2.5.1 / 2.6.3 reached end of support on December 30, 2025**.
- Environment sizes (small / medium / large) determine worker / scheduler / web-server capacity; auto-scaling for workers within bounds.
- DAGs live in S3; AWS pulls them into the environment. Plugins, requirements, custom config also via S3.
- For new pipeline orchestration, evaluate **Step Functions Distributed Map** (serverless fan-out) or **Glue Workflows** (data-integration native) before committing to Airflow. MWAA wins for teams already invested in Airflow's ecosystem.

## When to use it
- Existing Airflow DAGs being lifted to AWS.
- Data teams already trained on Airflow.
- Pipelines that need Airflow's specific operators / hooks / sensors (large catalog including AWS-native and third-party).
- Workflows where the DAG-as-code Python model is the team's preferred orchestration UX.

## When NOT to use it
- Greenfield workflows where Step Functions covers the use case — Step Functions is significantly cheaper at low scale and has tighter AWS integration.
- ETL-specific orchestration — **Glue Workflows** is data-pipeline-native and cheaper for pure Glue jobs.
- Low-volume workflows where the per-hour MWAA cost (always-on environment) doesn't amortize.

## Key concepts

**Environment.** The MWAA resource. Includes scheduler, web server (Airflow UI), and worker fleet. Sized at creation:
- **Small** — a few workers, lower-throughput.
- **Medium** — more workers, higher concurrency.
- **Large** — maximum capacity tier.

**Workers** auto-scale within configured min/max bounds.

**DAGs.** Python files in S3; MWAA syncs them to the environment.

**Plugins** and **requirements.txt** also pulled from S3 — custom operators, sensors, packages.

**Networking.** Environment runs in your VPC. Web server can be public (via AWS-hosted endpoint) or private (reachable only from the VPC).

**Authentication.** Airflow UI auth via IAM Identity Center or IAM identity (federated).

**Logging.** Scheduler, worker, web-server, DAG processing, and task logs sent to CloudWatch Logs.

**Supported Airflow versions (2026).** Airflow 3.0 (latest), 2.11 (added Jan 2026), and a rolling support window for the recent 2.x minor versions. Old patches reach EOL on AWS's schedule; **2.4.3 / 2.5.1 / 2.6.3 ended support Dec 30, 2025**.

**Integration.** Airflow's AWS provider package covers most AWS services (S3, EMR, EKS, Athena, Glue, Redshift, SageMaker, DynamoDB, Lambda) with mature operators.

## Pricing model

- **Per environment-hour** by size (small / medium / large).
- **Additional worker-hour** charges when auto-scaling beyond the included workers.
- **Storage** for metadata DB (included in environment cost; backed by an AWS-managed Aurora).
- **Data transfer**, **S3 storage** for DAGs, **CloudWatch Logs ingestion** all at standard rates.

MWAA's always-on environment cost is the dominant line item. Tiny / occasional workloads usually find Step Functions or Glue Workflows cheaper.

## Quotas & limits

- **Environments per Region per account**: 10 default (raisable).
- **Workers per environment**: bounded by size + max auto-scale.
- **DAG count**: high (thousands).
- **Concurrent tasks**: depends on size + worker count + Airflow config.
- **Metadata DB**: AWS-managed; not user-configurable.

## Common pitfalls

- **Running an Airflow version near EOL.** Plan upgrades quarterly; AWS pulls support on a schedule (most recently Dec 30, 2025 for several 2.x patch versions).
- **One huge environment for everything.** Better to split by environment / team boundary for blast-radius reasons.
- **DAG sprawl.** Hundreds of DAGs without lifecycle ownership accumulate. Tag DAGs with team / owner; audit periodically.
- **Heavyweight plugins / requirements.** Bloat environment startup time. Use slim requirements; vendor-lock to specific versions.
- **Public web server in production.** Default-public web server is convenient for dev; production should be private-VPC with VPN / Verified Access in front.
- **Airflow XCom for large data.** XCom uses the metadata DB — large XComs hurt scheduler performance. Pass S3 paths instead of payloads.
- **No DR plan.** Cross-Region MWAA recovery requires DAG-in-S3 replication + a standby environment in the target Region.
- **Forgotten secrets / connections in the Airflow UI.** Manage Airflow connections via Secrets Manager backend, not via the UI (which doesn't audit cleanly).

## Pairs well with
- **S3** — DAG storage.
- **Secrets Manager** — connection / variable storage backend.
- [Glue](../analytics/) (forthcoming), [EMR](../analytics/) (forthcoming), [Athena](../analytics/), **Redshift** — common DAG targets.
- **Lambda / ECS** — sub-DAG step execution.
- **CloudWatch Logs** — logging destination.
- **EventBridge** — trigger MWAA DAGs from AWS events.

## Pairs well with these repo pages
- [Step Functions](step-functions.md) — the AWS-native orchestration alternative.
- `docs/04-reference-architectures/batch-etl-glue.md`, `docs/04-reference-architectures/streaming-etl-kinesis.md` (forthcoming).

## Further reading
- [Amazon MWAA documentation](https://docs.aws.amazon.com/mwaa/).
- [Supported Airflow versions](https://docs.aws.amazon.com/mwaa/latest/userguide/airflow-versions.html).
- [MWAA architecture](https://docs.aws.amazon.com/mwaa/latest/userguide/what-is-mwaa.html).
- [Apache Airflow Amazon provider](https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/index.html).
- [MWAA pricing](https://aws.amazon.com/managed-workflows-for-apache-airflow/pricing/).
