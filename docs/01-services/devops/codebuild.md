# CodeBuild

> **One-line summary.** Managed build service. Run CI builds, tests, and arbitrary commands in containers — no build server fleet to operate.

## TL;DR

- Serverless build infrastructure. Defines a build in a **buildspec.yml** (or via CodePipeline / GitHub Actions / Jenkins integration); CodeBuild provisions a container, runs your steps, returns artifacts to S3.
- Wide range of **compute types**: small / medium / large / X-large / 2X-large CPU / GPU instances on AWS-managed runtimes (Amazon Linux 2023, Ubuntu, Windows) or your own container image.
- **Reserved capacity** for predictable workloads avoids the per-build cold-start; **on-demand** for sporadic builds.
- **Lambda compute mode** (recent) runs builds inside Lambda — sub-second startup for the smallest builds, no longer-running container.
- Integrates with CodePipeline, GitHub, GitLab, Bitbucket, CodeCommit, EventBridge.

## When to use it

- AWS-native CI/CD pipelines with CodePipeline.
- GitHub Actions / GitLab CI replacement for teams committed to AWS-managed builds.
- Container image builds (ECR push) inside private AWS networks.
- Workloads requiring access to private VPC resources during build (test against private DBs, internal package repos).
- Builds needing AWS IAM-issued credentials with no static secrets.

## When NOT to use it

- Teams happy with GitHub Actions / GitLab CI / CircleCI — switching for marginal benefit isn't worth it.
- Workloads needing complex matrix / fan-out CI patterns that other tools handle more ergonomically.
- Tiny, occasional builds where setting up CodeBuild is heavier than alternatives.

## Key concepts

### Build projects

A **build project** is the configurable unit: source location, environment (compute + image + runtime), buildspec, IAM role, artifact destination, VPC config, cache settings, logging destination.

### buildspec.yml

YAML file describing build phases (`install`, `pre_build`, `build`, `post_build`) and environment variables. Lives in the repo root by default; can be inline in the project config.

### Compute types

- **General-purpose** — small / medium / large / X-large / 2X-large containers (vCPU / RAM tiers).
- **GPU** — for ML training / inference builds.
- **ARM (Graviton)** — for ARM container builds and ARM-native test runs.
- **Lambda compute mode** — sub-second startup; for very small / quick builds.

### Runtime images

- **AWS-managed images** — current Amazon Linux 2023 / Ubuntu / Windows Server with common runtimes (Node, Python, Java, Go, .NET, Ruby, Docker, Android, etc.).
- **Custom images** — bring your own container image from ECR / Docker Hub.

### Build environments

- **On-demand** — provision per build; pay per build-minute. Default.
- **Reserved capacity** — fleet of always-on build instances; cheaper at sustained high build volume; no cold start.
- **Lambda mode** — sub-second cold start; included compute under Lambda's pricing model.

### Source integrations

- **CodeCommit, GitHub, GitHub Enterprise, GitLab, GitLab Self-Managed, Bitbucket** — pull source on build trigger.
- **S3** — source from an archive in S3.
- **No source** — for builds that fetch what they need at runtime.

### Webhooks

GitHub / GitLab / Bitbucket / CodeCommit can trigger builds on push / PR events.

### Artifacts

Build output to S3 (or to no destination for pure test runs).

### Caching

- **S3 cache** — generic file cache.
- **Local cache** — Docker layer cache, source cache, custom cache paths.

### VPC mode

Build container attaches to a VPC subnet — can reach private RDS / ElastiCache / internal package mirrors during build.

### IAM

- **Service role** — IAM role the build container assumes (CodeBuild has access to AWS services as scoped).
- Per-build IAM is the right way to authorize against AWS resources; no static credentials needed.

### Reports

CodeBuild parses test results (JUnit / TestNG / Cucumber / NUnit / Visual Studio TRX / Surefire / TAP) and presents pass/fail tracking + flakiness analysis.

## Pricing model

- **Per build-minute** by compute type. Lambda compute mode billed at Lambda rates.
- **Reserved capacity** — flat hourly per build-server, regardless of build activity.
- **Data transfer / S3 storage / CloudWatch Logs** as usual.

For high-volume CI (hundreds of builds/day), reserved capacity is cheaper than on-demand.

## Quotas & limits

- **Projects per account per Region**: 5,000 default.
- **Concurrent builds**: 60 default (raisable significantly).
- **Build timeout**: up to 8 hours.
- **Artifact size**: bounded by S3.
- **Custom images**: pulled from ECR / Docker Hub at build start.

## Common pitfalls

- **Long builds with no caching.** Re-installing every dependency every build is slow and expensive. Use S3 cache + local Docker layer cache.
- **Docker-in-Docker builds without privileged mode.** Container builds inside CodeBuild require `privileged: true` on the project. (Or use Docker buildx / Kaniko alternatives.)
- **No VPC config when build needs private resources.** Build will fail to reach private DBs / package mirrors.
- **Static credentials in buildspec.** Use the service role + IAM-issued credentials.
- **One huge project for everything.** Per-project visibility makes failures opaque. One project per logical build target.
- **No Reports for test results.** Tests pass / fail counts in CloudWatch Logs is hard to track; configure Reports for proper pass-rate trending.
- **Skipping Lambda compute mode for fast tests.** Sub-second startup beats container startup for short-running test suites.

## Pairs well with

- [CodePipeline](codepipeline.md) — orchestration.
- [CodeCommit](codecommit.md) / **GitHub** / **GitLab** / **Bitbucket** — source.
- [ECR](../compute/ecs.md) — container image destination.
- [S3](../storage/s3.md) — artifact storage.
- [CloudWatch Logs](../observability/) (forthcoming) — build logs.
- [Secrets Manager](../security-identity/secrets-manager.md) / [Parameter Store](../security-identity/parameter-store.md) — credentials / config.
- [SAM CLI](sam.md), [CDK](cdk.md), [CloudFormation](cloudformation.md) — deploy from build.

## Pairs well with these repo pages

- [CodePipeline](codepipeline.md), [CodeDeploy](codedeploy.md), [CodeCommit](codecommit.md), [ECS](../compute/ecs.md), [Lambda](../compute/lambda.md).

## Further reading

- [AWS CodeBuild documentation](https://docs.aws.amazon.com/codebuild/).
- [buildspec.yml reference](https://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html).
- [Reserved capacity](https://docs.aws.amazon.com/codebuild/latest/userguide/sample-reserved-capacity.html).
- [Lambda compute mode](https://docs.aws.amazon.com/codebuild/latest/userguide/lambda-compute.html).
- [Build reports](https://docs.aws.amazon.com/codebuild/latest/userguide/test-reporting.html).
