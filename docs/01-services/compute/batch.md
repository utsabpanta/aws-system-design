# Batch

> **One-line summary.** Managed batch job scheduler — submit jobs, AWS provisions compute (EC2 or Fargate), runs them in priority/queue order, and tears down when idle.

## TL;DR

- The right primitive for "I have N independent jobs to run, here's how big each one is, please find me compute." HPC, genomics, financial risk runs, ML preprocessing, video transcoding farms.
- Runs on **EC2**, **Fargate**, or **EKS** compute environments. EC2 + Spot is the cost winner; Fargate is the operationally simplest; EKS lets you reuse an existing cluster.
- **Multi-node parallel (MNP) jobs** — for MPI/HPC workloads needing inter-node communication — are EC2-only. Fargate doesn't support MNP.
- Built-in job array (run the same job N times with a per-index variable — perfect for embarrassingly parallel work) and job dependencies.
- The mental model is "Kubernetes Jobs with AWS managing the cluster" — but simpler if you don't already have Kubernetes.

## When to use it

- High-throughput batch processing — render farms, genomics pipelines, ETL backfills, Monte Carlo simulations, ML data preprocessing.
- Workloads with thousands of independent units (use job arrays).
- Cost-sensitive batch where Spot interruption is acceptable.
- HPC / MPI workloads with inter-node messaging (EC2 multi-node parallel jobs).
- Jobs that exceed Lambda's 15-minute timeout but don't justify a long-lived service.

## When NOT to use it

- Online / latency-sensitive request handling. Batch jobs queue and start in seconds-to-minutes — wrong shape for HTTP.
- Streaming or always-on workers — use ECS/EKS services or Lambda.
- One-off interactive workloads — submit-and-wait via SDK works but feels heavy; consider Step Functions or a direct ECS RunTask.
- Workloads already orchestrated by Step Functions Distributed Map, which has gotten close to Batch's "fan-out N tasks" capability for many cases (and integrates with all of AWS).

## Key concepts

**Compute environment** — the pool of capacity Batch can schedule onto. Three flavors:

- **Managed EC2** — Batch creates and scales an ASG; supports On-Demand, Spot, and instance-type lists ("best-fit" or "spot-capacity-optimized" allocation strategies).
- **Managed Fargate** — Batch provisions Fargate tasks per job. No cluster sizing; pay per job. Caveats: no MNP, no GPU, max 16 vCPU / 120 GB per task.
- **Unmanaged** — you bring your own ECS cluster; Batch just dispatches jobs.
- **EKS** — Batch dispatches jobs as Kubernetes pods onto an existing EKS cluster.

**Job queue** — a priority-ordered queue. Each queue maps to one or more compute environments. Higher-priority queue jobs run first; Batch scales the compute environments based on queued demand.

**Job definition** — the blueprint. Container image, command, CPU/memory, vCPU count, environment variables, IAM role, retry strategy, timeout, instance type hints, MNP node count (for multi-node parallel).

**Job** — a submitted unit. Goes through SUBMITTED → PENDING → RUNNABLE → STARTING → RUNNING → SUCCEEDED / FAILED.

**Array jobs** — submit one job with `arraySize: N`, get N independent child jobs with `AWS_BATCH_JOB_ARRAY_INDEX` set 0..N-1. The right primitive for embarrassingly parallel work (process N files, fit M models).

**Multi-node parallel (MNP) jobs** — Batch launches N EC2 instances coordinated as one job, with the rank-0 node as "main" and the rest as workers. Used for MPI, distributed training, etc. **EC2 only — Fargate does not support MNP.**

**Job dependencies** — `dependsOn: [{ jobId: "..." }]` runs job B after job A succeeds. Supports `SEQUENTIAL` and `N_TO_N` dependency types for arrays.

**Spot integration.** Managed EC2 compute environments support Spot natively. The `SPOT_CAPACITY_OPTIMIZED` allocation strategy picks instance types from the deep end of the Spot pool to minimize reclaim frequency.

## Pricing model

- **Batch the service is free.** You pay only for the underlying compute (EC2, Fargate, or EKS data plane) and any storage/data transfer.
- **EC2** — pay-per-instance-hour. Spot eligible. Savings Plans / Reserved Instances apply.
- **Fargate** — pay-per-vCPU-second and per GB-second. Spot eligible.
- **EKS** — pay your normal EKS cluster + data-plane costs.
- **Storage** — EBS for EC2-mounted scratch space; FSx for Lustre if you need high-throughput shared scratch.

For long-running batch fleets, EC2 Spot with Compute Savings Plans for the on-demand base usually wins by a large margin.

## Quotas & limits

- **Compute environments per account per Region**: 50 (raisable).
- **Job queues per account per Region**: 50 (raisable).
- **Job definitions**: no practical limit on revisions.
- **Array job size**: up to 10,000 child jobs per array.
- **Max job timeout**: configurable; recommend setting it explicitly.
- **Concurrent vCPUs**: bounded by your EC2 / Fargate / EKS vCPU quotas, *not* by Batch itself.
- **MNP node count**: up to 1,000 EC2 nodes per multi-node parallel job (varies by instance type and placement group).

## Common pitfalls

- **Picking Fargate when you need MNP.** Multi-node parallel jobs require EC2. Fargate will silently never run them.
- **No retry strategy.** Spot reclaim or transient failure → job marked FAILED, you re-submit by hand. Set `retryStrategy.attempts: 3+` with evaluateOnExit clauses for clean retries.
- **One huge job instead of an array.** A 10,000-file job that's a single container with a for-loop loses Batch's parallelism and re-running on failure means re-doing all the work. Array jobs with per-index input let you retry just the failed children.
- **Container image bloat slowing scale-out.** Every EC2 instance Batch launches pulls the image. Use slim images and consider [ECR pull-through cache](https://docs.aws.amazon.com/AmazonECR/latest/userguide/pull-through-cache.html).
- **Bad instance type list.** Limiting to one instance type means Spot reclaims hit you hardest. Allow a broad list with `SPOT_CAPACITY_OPTIMIZED` strategy.
- **No `EFS` / `FSx for Lustre` for shared scratch.** Workflows that pass large intermediate files between jobs reinvent S3 with extra latency. FSx for Lustre + S3 import is the HPC pattern.
- **Confusing Batch with Step Functions Distributed Map.** Distributed Map is great for serverless fan-out via Lambda/ECS; Batch is better when you need MNP, deep Spot integration, or compute environments measured in thousands of vCPUs.

## Pairs well with

- **EC2 Spot Capacity Providers** — cost optimization for batch fleets.
- **FSx for Lustre** — high-throughput shared scratch (Lustre integrates with S3 for input/output).
- **S3** — input and output store for batch pipelines.
- **Step Functions** — orchestrate Batch jobs as steps with retries, parallelism, error handling.
- **EventBridge** — trigger Batch jobs on schedule or events.
- **CloudWatch Logs + Container Insights** — per-job stdout/stderr and metrics.

## Pairs well with these repo pages

- [EC2](ec2.md), [Fargate](fargate.md), [EKS](eks.md) — the compute substrates.
- `docs/04-reference-architectures/batch-etl-glue.md` (forthcoming) — batch ETL patterns.

## Further reading

- [AWS Batch documentation](https://docs.aws.amazon.com/batch/).
- [AWS Batch best practices](https://docs.aws.amazon.com/batch/latest/userguide/best-practices.html).
- [Multi-node parallel jobs](https://docs.aws.amazon.com/batch/latest/userguide/multi-node-parallel-jobs.html).
- [Genomics workflows on AWS Batch](https://aws.amazon.com/blogs/industries/scalable-and-cost-effective-batch-processing-for-ml-workloads-with-aws-batch-and-amazon-fsx/).
- Step Functions Distributed Map docs — for comparing serverless fan-out alternatives.
