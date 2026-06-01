# ECS (Elastic Container Service)

> **One-line summary.** AWS-native container orchestrator. Schedules Docker containers onto EC2 or Fargate without you running a Kubernetes control plane.

## TL;DR

- The right default for containers on AWS unless you specifically need Kubernetes APIs. Simpler, cheaper, and tighter AWS integration than EKS.
- Two launch types: **Fargate** (serverless, AWS owns the host) and **EC2** (you own the host, bin-pack workloads, pair with Spot for big savings).
- **ECS Express Mode** (launched Nov 2025) collapses the "container + ALB + autoscaling" recipe into one command. Use it for greenfield services unless you already have an opinionated platform.
- Service discovery via AWS Cloud Map; mesh via AWS App Mesh (Envoy-based) or your own (Istio, Linkerd) if you really need it.
- The biggest gotcha is networking — `awsvpc` mode (the default for Fargate) gives each task its own ENI, which is great for isolation and burns ENI quota on EC2 launch types.

## When to use it

- Standard containerized web services and workers, where you'd otherwise reach for EKS.
- Teams who don't want to operate Kubernetes (control plane upgrades, IRSA, cluster autoscaler, etc.).
- Workloads that benefit from tight AWS integration: IAM roles per task, ALB target groups, Service Connect, CloudWatch Container Insights out of the box.
- Greenfield apps where ECS Express Mode's "one command, full stack" is exactly what you want.
- Migrating off **App Runner** (closing to new customers 2026-04-30) — ECS Express Mode is the AWS-recommended target.

## When NOT to use it

- You need portability — multi-cloud, on-prem with KubeEdge, or a CNCF-ecosystem dependency (Argo, Tekton, Knative). Use EKS or self-managed Kubernetes.
- The workload is a single HTTP service that fits Lambda or a managed PaaS — those are cheaper end-to-end.
- You need stateful workloads with persistent local storage and pod affinity (databases, distributed storage). Use EC2, EKS with persistent volumes, or a managed equivalent.

## Key concepts

**Cluster** — a logical grouping of tasks and services. A cluster on Fargate is essentially free; a cluster on EC2 has the EC2 instances as its capacity.

**Task definition** — the blueprint. JSON spec for one or more containers, their CPU/memory, IAM task role, volumes, networking mode. Versioned; deploys move services from one task definition revision to the next.

**Task** — a running instantiation of a task definition. One task = one or more containers sharing a network namespace.

**Service** — keeps N tasks of a given task definition running. Wires them to an ALB/NLB target group, handles rolling/blue-green deploys via CodeDeploy, and integrates with Service Connect for service discovery.

**Launch types:**

- **Fargate** — AWS provisions the host. You pay per vCPU-second and GB-second. No node management. Right default for most teams.
- **EC2** — you operate the EC2 hosts (in an Auto Scaling Group). Cheaper per unit at high utilization, supports daemon-set patterns (one task per host), supports Spot for big savings.
- **External** (ECS Anywhere) — register your own VMs (on-prem or in another cloud) and run ECS tasks on them. Niche.

**Networking modes:**

- **`awsvpc`** (default for Fargate, recommended for EC2) — each task gets its own ENI in your VPC, IAM-attachable security group, and routable IP. Per-task isolation, but ENI count limits how many tasks per EC2 host.
- **`bridge`**, **`host`**, **`none`** — legacy / specialty modes for EC2 only.

**Service Connect** — built-in service-to-service discovery and load balancing using Envoy sidecars managed by ECS. The native answer to "how does service A find service B"; replaces App Mesh for most use cases.

**ECS Express Mode** — single-command deployment: `aws ecs create-service-express --image my-image:tag`. Auto-provisions a Fargate service, an ALB (or shares one across up to 25 services using host-header rules), auto-scaling on CPU, security groups, and an auto-generated URL. Free; resources land in your account so you keep full control as you grow.

**CodeDeploy / ECS deploy controllers** — three options:

- **Rolling** (ECS default): replace tasks one batch at a time.
- **Blue/Green** (via CodeDeploy): two target groups, shift traffic, can canary or auto-rollback on alarm.
- **External** (custom controller, e.g., Flagger): for advanced canary patterns.

## Pricing model

- **Fargate launch type** — per vCPU-second and per GB-second, billed per second with a 1-minute minimum. Add storage above the included 20 GB ephemeral. **Fargate Spot** is ~70% cheaper than on-demand with 2-minute reclaim notice, available in most Regions for x86 and Graviton.
- **EC2 launch type** — you pay for the underlying EC2 instances (any of the Savings Plans / Spot discounts apply). ECS the service is free.
- **ECS Express Mode** — no premium; you pay for the Fargate tasks and the ALB only.
- **Data transfer** — same as everything else on AWS (cross-AZ chatter is the surprise line item).

Compute Savings Plans cover Fargate at the same discount as EC2 (~30–66%). Apply them; the math is identical.

## Quotas & limits

- **Services per cluster**: 5,000 default.
- **Tasks per service**: 5,000.
- **Task definitions** (revisions): 1M per account per Region. You can register more than you'll ever use; old revisions don't cost anything.
- **Fargate concurrent tasks**: regional quota, default ~1,000 vCPUs, raisable.
- **`awsvpc` ENI density on EC2**: bounded by the instance's ENI/IP-per-ENI cap (use `awsvpcTrunking` to multiply this on supported instance types).
- **Container image size**: 10 GB pulled into the Fargate task's writable layer (with caching via ECR pull-through cache / Fargate's host caching).

## Common pitfalls

- **Sizing Fargate too small.** A 0.25 vCPU / 512 MB task with a JVM workload will thrash. Right-size with Container Insights metrics; don't optimize for the lowest billable size.
- **Pulling massive images.** Fargate cold-pull from a private ECR adds seconds to task startup. Use multi-stage builds, distroless / slim base images, and Image Builder for golden images.
- **Not using IAM task roles.** Embedding access keys in containers is a security hole. Always set `taskRoleArn`; AWS SDKs auto-discover the role via the task metadata endpoint.
- **One ALB per service.** ALB has a per-hour cost and a connection ceiling; share one ALB across many services using host- or path-based listener rules (which is exactly what ECS Express Mode does for you).
- **Ignoring `stopTimeout` and `SIGTERM` handling.** Tasks killed mid-flight serve 500s during deploys. Implement graceful shutdown and set `stopTimeout: 30` or higher.
- **Cross-AZ chatter at full mesh.** Service Connect, App Mesh, or topology-aware routing reduce this. Bills get ugly fast at high QPS otherwise.
- **EC2 launch type without Spot.** Half the point of EC2 over Fargate is mixing on-demand and Spot for cost — use Capacity Providers and Spot to capture the discount.

## Pairs well with

- **ALB / NLB** — L7 / L4 ingress.
- **ECR** — private container registry; pull-through caches mirror public registries.
- **Service Connect or App Mesh** — service discovery and traffic shaping.
- **CloudWatch Container Insights** — built-in observability.
- **AWS Fargate Spot** — cheap, eviction-tolerant compute.
- **CodeDeploy** — blue/green and canary deploys.
- **EventBridge + Scheduled Tasks** — cron-style container runs.

## Pairs well with these repo pages

- [Fargate](fargate.md) — the serverless launch type ECS most often runs on.
- [App Runner](app-runner.md) — what to migrate off of toward ECS Express Mode.
- [EKS](eks.md) — when you need Kubernetes APIs instead.

## Further reading

- [Amazon ECS documentation](https://docs.aws.amazon.com/AmazonECS/).
- [ECS Express Mode docs](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/express-service-overview.html).
- [Service Connect deep dive](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-connect.html).
- [Fargate Spot best practices](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/fargate-capacity-providers.html).
- Amazon Builders' Library — "Caching challenges and strategies", "Avoiding insurmountable queue backlogs".
