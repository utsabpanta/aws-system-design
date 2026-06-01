# App Runner

> **One-line summary.** Fully managed container/web app service — push an image or a Git repo, AWS runs it behind an HTTPS endpoint with autoscaling and TLS.

## Status

> ⚠️ **AWS App Runner is closed to new customers as of April 30, 2026.** Existing customers can continue to use the service; AWS continues security and availability patches but is **not adding new features**. For new workloads, AWS recommends migrating to **[Amazon ECS Express Mode](ecs.md)** (launched November 2025).
>
> The rest of this page documents App Runner for existing users and for understanding what shipped before the closure. If you're starting fresh, jump to ECS Express Mode in [`ecs.md`](ecs.md).

## TL;DR
- A PaaS-style runtime for containers and source-code apps. Hand it an ECR image or a GitHub repo with a runtime config; it builds, deploys, and runs.
- Auto-scales from 0 to N instances on request rate. Built-in HTTPS endpoint, custom domains, VPC connector for private downstream access.
- **Closed to new customers since 2026-04-30.** Use ECS Express Mode for the equivalent experience on a service AWS is actively investing in.
- For existing users: stable, no major changes planned. Plan a migration path — running on a frozen service indefinitely is a risk.
- Pricing is per active-instance vCPU-second and GB-second plus a flat per-month per-app fee for automated deploys; not always cheaper than equivalent Fargate.

## When to use it
- You're already using App Runner and want to understand it better. (Otherwise, see below.)
- Documenting an existing architecture or migrating off it.

## When NOT to use it
- **Any new project.** Use [ECS Express Mode](ecs.md) instead — it's the AWS-recommended successor, has no service closure risk, and is actively gaining features.
- Workloads needing GPU, sub-second cold-start guarantees, or fine-grained networking.
- Long-running compute, batch, or anything that doesn't fit the "stateless HTTP service" mold.

## Key concepts (for existing users)

**Service** — the top-level App Runner resource. One service = one app = one HTTPS endpoint.

**Source.**
- **Container image source** — pulls from ECR (private or public). Deploys triggered manually, by webhook, or by image update notification.
- **Source-code source** — connects to a GitHub repo via a CodeStar connection. App Runner builds the container in a managed pipeline based on a runtime config (Python, Node.js, Java, .NET, Go, Ruby, PHP).

**Auto-scaling** — configured by min/max instances and a concurrency target (requests in flight per instance). Idle instances scale to a configurable minimum (1 by default). Pricing distinguishes "provisioned" (always running) from "active" (handling a request) time.

**VPC connector** — outbound private connectivity to your VPC (e.g., to reach RDS). Required for any downstream that's not internet-public.

**Custom domains** — bring your own domain; App Runner provisions ACM certs and DNS validation.

**Auto-deployments** — webhook from ECR image push or GitHub push triggers a redeploy automatically.

**Observability.** Application logs and access logs ship to CloudWatch Logs. Metrics in CloudWatch under `AWS/AppRunner`. X-Ray supported via SDK instrumentation.

## Pricing model

- **Provisioned-instance fee** for instances kept warm (minimum capacity) — per vCPU-second and GB-second.
- **Active-instance fee** for instances actively serving requests — higher than provisioned.
- **Build fee** for source-code services (per build-minute).
- **Per-application monthly fee** if you enable automated deployments.
- **Data transfer** at standard AWS rates.

A typical price point (US East / US West / EU Ireland / Asia Pacific Tokyo) sits around fractions of a cent per GB-hour, with idle/provisioned cheaper than active. The exact numbers have shifted since launch — check the [official pricing page](https://aws.amazon.com/apprunner/pricing/) before sizing anything.

For most workloads, equivalent Fargate (via ECS Express Mode) lands in the same cost ballpark with more flexibility.

## Quotas & limits

- **Services per Region**: 100 (raisable).
- **Concurrent service operations** (create, update, deploy): limited.
- **Maximum vCPU / memory per instance**: 4 vCPU / 12 GB.
- **Max concurrent requests per instance**: configurable, up to 200.
- **Custom domains per service**: 5.
- **VPC connectors per Region**: 10.
- **Build timeout**: 30 minutes for source-code services.

## Common pitfalls

- **Starting new projects on it.** Don't. ECS Express Mode is the path AWS is investing in. App Runner is in security-patches-only mode.
- **Assuming cheap idle.** With min instances > 0, you pay for provisioned capacity 24/7 even at zero traffic. Set min instances to 1 for warm starts, accept full scale-to-zero (and the cold-start hit) otherwise.
- **VPC connector for everything.** Adds latency; only use for downstreams that aren't internet-public.
- **GitHub source for production builds.** The managed build is opinionated; for any non-trivial pipeline, build the container in CI and deploy from ECR.
- **Letting auto-deploy run unguarded.** Image-push triggers redeploy with no canary. For production-grade rollout, control deploys explicitly via the API.
- **Skipping the migration plan.** Even if your App Runner service runs fine today, the service is no longer actively developed. Build a migration plan now while you have time.

## Migrating to ECS Express Mode

Migrating off App Runner to ECS Express Mode follows a predictable shape:

1. **Container image stays the same** — App Runner already runs containers; the same image runs on ECS Express Mode.
2. **One `aws ecs create-service-express` call** creates the equivalent stack (Fargate task, ALB target group, autoscaling, security group, generated URL).
3. **Domain migration** — point your custom domain at the new ALB (Route 53 record swap).
4. **Auto-deploy hook** — replace the ECR image-push webhook with an EventBridge rule → ECS deploy or a CodePipeline source action.
5. **Observability** — already CloudWatch on both sides; minimal re-wiring.

See [`ecs.md`](ecs.md) for ECS Express Mode specifics.

## Pairs well with
- **ECR** — the container source.
- **VPC connector + RDS / ElastiCache** — private downstream access.
- **Route 53 + ACM** — custom domain and TLS.
- **CloudWatch Logs / Metrics / X-Ray** — observability.

## Pairs well with these repo pages
- [ECS](ecs.md) — the recommended successor (ECS Express Mode).
- [Fargate](fargate.md) — what runs underneath ECS Express Mode.
- [Lightsail](lightsail.md) — adjacent "easy mode" container hosting for personal-scale workloads.

## Further reading
- [AWS App Runner availability change](https://docs.aws.amazon.com/apprunner/latest/dg/apprunner-availability-change.html) — the official closure notice.
- [Announcing Amazon ECS Express Mode](https://aws.amazon.com/about-aws/whats-new/2025/11/announcing-amazon-ecs-express-mode/).
- [AWS App Runner documentation](https://docs.aws.amazon.com/apprunner/) (still maintained for existing users).
