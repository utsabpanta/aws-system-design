# Fargate

> **One-line summary.** Serverless compute engine for containers. You hand AWS a task definition or pod spec; AWS provisions the host and runs the container.

## TL;DR

- A *launch type*, not a standalone service — you consume Fargate via ECS or EKS.
- "No nodes" is the value prop. No EC2 instances to size, patch, scale, or pay for when idle.
- **Fargate Spot** runs containers on spare capacity at ~70% off, with a 2-minute reclaim notice. Available for both ECS and (with caveats) EKS workloads.
- Costs more per vCPU-hour than equivalent EC2; the math favors Fargate when ops time + idle capacity dominate, EC2 when you can run at >70% utilization with Reserved/Spot capacity.
- The biggest gotcha is image pull time at startup — large containers add seconds to scale-out latency, which compounds during traffic spikes.

## When to use it

- You want containers without operating EC2 hosts.
- Workloads have spiky or unpredictable load — you pay only for running tasks.
- The team is small and ops time matters more than per-vCPU price.
- Workloads where each task wants its own ENI / IAM role / network namespace (Fargate forces `awsvpc` and per-task IAM).
- ECS Express Mode services (always Fargate underneath).

## When NOT to use it

- High, steady utilization where EC2+Spot+Savings Plans wins on cost.
- GPU workloads — Fargate has no GPU support (use EC2 or EKS with GPU node groups).
- Workloads needing privileged containers, custom kernel modules, or `host` networking (none of which Fargate allows).
- DaemonSets in Kubernetes (Fargate on EKS is per-pod, not per-node — DaemonSets don't make sense).
- Tasks that need very large local storage cheaply (Fargate ephemeral storage is up to 200 GB; price-per-GB exceeds EBS).

## Key concepts

**Launch type vs Capacity Provider.** "Launch type" is the legacy way to pick Fargate (`launchType: FARGATE`); "Capacity Providers" (`FARGATE`, `FARGATE_SPOT`) are the modern way and let you mix on-demand and Spot in a single ECS service with weights and base counts.

**vCPU / memory matrix.** Fargate sells tasks in discrete (vCPU, memory) combinations: 0.25 vCPU with 0.5–2 GB, 0.5 vCPU with 1–4 GB, 1 vCPU with 2–8 GB, up to **16 vCPU with 120 GB** on x86 and Graviton. Memory is in 1 GB increments within the matrix. Picking a size outside the matrix isn't allowed.

**Architecture: x86 vs Graviton.** Set `runtimePlatform.cpuArchitecture: ARM64` on the task definition. Graviton tasks are ~20% cheaper per vCPU-hour with no other downside if your container is multi-arch (build with `docker buildx`).

**Ephemeral storage.** Each task gets 20 GB of free ephemeral writable storage; you can request up to 200 GB at additional cost. Lost when the task stops.

**Networking.** Fargate always uses `awsvpc` mode — each task has its own ENI in your VPC subnet, with its own security group. Public assignment requires the subnet to be public *or* the task to be in a private subnet with a NAT route. VPC Endpoints to ECR, S3, CloudWatch Logs are usually worth setting up to avoid NAT charges for image pulls and log writes.

**Pull-through cache (ECR).** Mirror public images (Docker Hub, GHCR, public ECR) into your private ECR on demand. Reduces external rate-limit risk and speeds repeat pulls.

**Fargate Spot.** Same Fargate pricing model, ~70% off. AWS reclaims tasks with a 2-minute SIGTERM. Use for stateless workers, batch, async consumers; pair with **Capacity Provider Strategies** (e.g., `FARGATE_SPOT weight=4, FARGATE weight=1 base=2`) to maintain a baseline of on-demand for serving traffic while burst capacity rides Spot.

**Cold start vs warm start.** "Task startup time" = control-plane provisioning (~10s, Region-dependent) + image pull (proportional to image size) + container init. Fargate caches images at the host level so subsequent task starts on the same host can be faster, but you don't control which host. For latency-sensitive scale-out, keep images small and use the [Seekable OCI](https://github.com/awslabs/soci-snapshotter) image format (lazy-pull) where supported.

## Pricing model

- **Per vCPU-second and per GB-second**, with a 1-minute minimum charge per task.
- Pricing differs by Region and by architecture (Graviton is cheaper).
- **Fargate Spot** is ~70% off, eligible for ECS in most Regions and EKS via dedicated profiles.
- **Ephemeral storage** above 20 GB billed per GB-hour.
- **Compute Savings Plans** apply at the same flexible discount they apply to EC2 / Lambda.
- **Data transfer** — same surprise line items as everywhere else (cross-AZ, NAT egress).

The breakeven vs EC2: at ≳70% steady-state utilization with multi-year Savings Plans, EC2 is cheaper per unit of work. Below that, Fargate's pay-per-task model wins because there's no idle capacity charge.

## Quotas & limits

- **vCPU per Region** for on-demand Fargate: default in the low thousands, raisable.
- **Fargate Spot vCPU**: separate quota.
- **Tasks per service**: 5,000 (ECS limit).
- **Maximum task size**: 16 vCPU / 120 GB on x86 and Graviton.
- **Concurrent ECR pulls**: bounded by per-host throughput.
- **Ephemeral storage**: 200 GB max per task.

## Common pitfalls

- **Choosing the smallest size to save money.** A 0.25 vCPU JVM task GC-thrashes. Right-size on Container Insights; cheapest-bill ≠ cheapest cost-per-request.
- **Massive images.** A 4 GB image adds seconds to every cold scale-out, multiplied across many tasks during a traffic spike. Build slim — distroless / Alpine / multi-stage.
- **No `stopTimeout` for graceful shutdown.** Tasks get SIGKILL after 30 s by default; HTTP serving tasks should set this to whatever's needed to finish in-flight requests.
- **No Spot Capacity Provider for stateless workers.** Leaving 70% on the table.
- **NAT egress for image pulls and logs.** ECR / S3 / CloudWatch Logs Interface endpoints (or Gateway for S3) save real money at scale.
- **Per-task IAM ignored.** Use `taskRoleArn` instead of stuffing credentials into env vars.
- **Fargate on EKS for DaemonSets.** Doesn't work; DaemonSets need real nodes.
- **Assuming Fargate scales instantly.** Provisioning + image pull = seconds-to-minutes. For latency-critical scale-out, keep a warm baseline.

## Pairs well with

- [ECS](ecs.md) — the most common front door to Fargate.
- [EKS](eks.md) — Fargate profiles for serverless pods, with caveats.
- **ECR + pull-through cache** — image distribution.
- **ALB / NLB** — ingress.
- **CloudWatch Container Insights** — observability.
- **Compute Savings Plans** — discount even on Fargate.

## Further reading

- [AWS Fargate documentation](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html).
- [Fargate Capacity Providers (Spot)](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/fargate-capacity-providers.html).
- [Fargate task sizing](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html#fargate-tasks-size).
- [Seekable OCI for fast container startup](https://aws.amazon.com/blogs/aws/aws-fargate-enables-faster-container-startup-using-seekable-oci/).
- Amazon Builders' Library — "Reducing scale-out delay with Auto Scaling and warm pools".
