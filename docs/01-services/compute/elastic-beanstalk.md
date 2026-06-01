# Elastic Beanstalk

> **One-line summary.** AWS's classic PaaS — give it your app code and a platform (Python, Node, Java, Go, .NET, PHP, Ruby, Docker), it provisions EC2, ALB, ASG, RDS, and runs the deploy.

## TL;DR

- The original "git push, AWS handles the rest" service on AWS, launched 2011. Still actively maintained — AWS continues to ship new platform versions in 2026.
- It's a thin layer over EC2 + Auto Scaling Group + ALB + (optional) RDS. You can drop down to the underlying resources at any time.
- The model fits a single-app team well; less idiomatic for microservices or containerized fleets, where ECS/EKS won.
- **Watch the platform branch lifecycle** — AWS retires individual platform branches on a schedule (e.g., Amazon Linux 2 reaches EOL on June 30, 2026, taking AL2-based platform branches with it). Migrate to Amazon Linux 2023 branches.
- For new projects in 2026, consider **ECS Express Mode** (containerized, simpler) or **App Runner** (closing to new customers — see below) before defaulting to EB.

## When to use it

- Single-application teams who want a deploy story without operating ECS/EKS.
- Lift-and-shifting an existing app (Rails, Spring Boot, Django, Express, ASP.NET) onto AWS quickly.
- You want AWS to manage capacity, health checks, rolling deploys, and basic blue/green without writing CloudFormation yourself.
- Workloads where the EB platform list (Python, Node, Java, Go, .NET, PHP, Ruby, Docker, multi-container Docker on ECS) covers your runtime needs.

## When NOT to use it

- Microservices / container fleets — ECS or EKS gives you proper service-to-service primitives.
- You need fine-grained control over the underlying CloudFormation / IaC. EB's nested stacks are awkward to extend and easy to get wrong.
- Modern container workflows where you'd rather think in terms of images and task definitions than "platform branches."
- New apps where ECS Express Mode (released Nov 2025) gives you a similar one-command experience with a cleaner mental model.

## Status

Elastic Beanstalk is **actively maintained**, not deprecated. AWS continues to ship new platform versions (Amazon Linux 2023 branches added throughout 2025/2026) and security updates.

The lifecycle nuance worth knowing: **platform branches** (e.g., "Python 3.11 running on Amazon Linux 2") have individual retirement schedules tied to upstream language EOLs and the underlying Amazon Linux version. **Amazon Linux 2 reaches end of life on June 30, 2026**, after which all AL2-based platform branches retire on that schedule. Migrating to the equivalent Amazon Linux 2023 branch is a config change and a redeploy.

## Key concepts

**Application** — the top-level container in EB. Has a name and zero or more environments.

**Environment** — a running deployment (`my-app-prod`, `my-app-staging`). Comes in two configurations:

- **Web server environment** — ALB / NLB in front, EC2 instances behind, optional RDS.
- **Worker environment** — SQS-backed background workers. EB polls SQS and posts messages to a local HTTP endpoint on each instance.

**Application version** — an immutable bundle of your code (S3-stored). Deploys promote a version to an environment.

**Platform / platform branch / platform version** — the runtime stack EB installs on each EC2 instance. *Platform* is the language (Python, Java, …). *Platform branch* is a specific OS + runtime combo (e.g., "Python 3.11 running on 64bit Amazon Linux 2023"). *Platform version* is a specific patched build of that branch.

**Deployment policies** — EB knows how to do `AllAtOnce`, `Rolling`, `RollingWithAdditionalBatch`, `Immutable`, and `Traffic-Splitting` (true canary) deploys. `Immutable` and `Traffic-Splitting` are the production-grade options.

**Configuration files (`.ebextensions`)** — YAML / JSON files in `.ebextensions/` inside your source bundle that customize the underlying CloudFormation (install packages, set parameters, run commands on deploy).

**Saved configurations** — capture an environment's settings as a reusable template.

**Managed updates** — opt-in weekly maintenance window for EB to apply minor platform version patches automatically.

## Pricing model

- **Elastic Beanstalk the service is free.**
- You pay for the underlying AWS resources: EC2, EBS, ALB / NLB, RDS, S3 (for versions), CloudWatch.
- All standard discount mechanisms apply (Savings Plans, Reserved Instances for the EC2 fleet; RDS Reserved Instances).

EB is one of the few PaaS-style products with no PaaS markup — the abstraction is free; you pay raw infra prices.

## Quotas & limits

- **Applications per Region**: 75 (raisable).
- **Application versions per Region**: 1,000 (raisable). Use the **application version lifecycle policy** so old versions get deleted from S3 — otherwise versions and the associated S3 storage accumulate.
- **Environments per Region**: 200 (raisable).
- **Configuration templates per application**: 50.
- **Environment manifest (`.ebextensions`)**: 16 KB per file, total config size limited.

## Common pitfalls

- **Ignoring platform branch retirements.** EB will eventually stop deploying to retired branches. Subscribe to [Elastic Beanstalk release notes](https://docs.aws.amazon.com/elasticbeanstalk/latest/relnotes/relnotes.html) and migrate at least 90 days before the retirement date.
- **RDS inside the environment.** EB lets you create an RDS instance "as part of" the environment. Convenient for dev; in prod it ties the database lifecycle to the environment — terminating the environment destroys the DB. Always create RDS *outside* the environment for production.
- **Application versions never cleaned up.** Without a lifecycle policy, every deploy adds an S3 artifact forever. EB's lifecycle policy auto-deletes old versions.
- **`AllAtOnce` deploys in production.** Causes downtime on every deploy. Use `Immutable` or `Traffic-Splitting`.
- **`.ebextensions` for things CloudFormation does better.** New CFN/CDK is much more maintainable than 200-line ebextensions hooks.
- **Treating EB as a container orchestrator.** The "multi-container Docker" platform is built on ECS; if you're going down that road, just use ECS directly.
- **Single-instance environments in production.** That's the default for the smallest tier — no ALB, no failover. Fine for dev, dangerous in prod.

## Pairs well with

- **RDS** (created separately) — managed database tier.
- **CloudWatch Logs** — stream EC2 logs out of the environment.
- **Route 53** — friendly DNS in front of the EB-provided URL.
- **AWS X-Ray** — distributed tracing (X-Ray daemon ships as an EB extension).
- **CodePipeline** — wire up CI/CD that deploys to EB environments.

## Pairs well with these repo pages

- [EC2](ec2.md) — what's underneath.
- [ECS](ecs.md) — the modern containerized alternative.
- [App Runner](app-runner.md) — adjacent PaaS-style option (closing to new customers).

## Further reading

- [AWS Elastic Beanstalk documentation](https://docs.aws.amazon.com/elasticbeanstalk/).
- [Elastic Beanstalk platform support policy](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/platforms-support-policy.html).
- [Elastic Beanstalk platform release schedule](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/platforms-schedule.html).
- [Application version lifecycle](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/applications-lifecycle.html).
- [Immutable deployments](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/using-features.rolling-version-deploy.html#environmentmgmt-updates-immutable).
