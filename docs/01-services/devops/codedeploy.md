# CodeDeploy

> **One-line summary.** Managed deployment service. Coordinates rolling, blue/green, and canary deployments to EC2, on-prem servers, ECS, and Lambda — with health-check-driven automatic rollback.

## TL;DR

- The deployment-orchestration piece. Most teams use CodeDeploy via **CodePipeline**, but it can be invoked standalone.
- Target types: **EC2 / on-prem instances**, **ECS (services)**, **Lambda (function versions)**.
- Deployment strategies vary by target:
  - **EC2**: in-place rolling (with batch sizes) and blue/green (with load-balancer swap).
  - **ECS**: blue/green via two target groups + traffic shift (`Linear`, `Canary`, `AllAtOnce`).
  - **Lambda**: traffic shift across function version aliases (`Linear`, `Canary`, `AllAtOnce`).
- **CloudWatch alarms** as automatic rollback triggers — if `5xx` rate, p99 latency, or any custom metric breaches during the shift, CodeDeploy rolls back.
- For most ECS / EKS workloads, the deployment surface is often the orchestrator's own (ECS rolling updates, Argo Rollouts on EKS); CodeDeploy adds value for managed blue/green with alarm-gated automatic rollback.

## When to use it

- Blue/green deployments for ECS services with traffic-shift control.
- Canary deployments for Lambda functions with weighted aliases.
- EC2 / Auto Scaling Group deployments with in-place or blue/green.
- On-prem (or VMware Cloud on AWS) hosts that you'd otherwise script deploys for.
- Any deployment where alarm-driven automatic rollback is a requirement.

## When NOT to use it

- Kubernetes-native deployments — Argo Rollouts, Flagger, or built-in Deployment / StatefulSet rolling updates fit better.
- Plain ECS rolling updates with no canary / blue-green need — ECS's built-in update suffices.
- Workloads where the deploy tool is GitOps-native (Flux / Argo) — CodeDeploy doesn't fit the model.

## Key concepts

### Application

Top-level CodeDeploy resource — names a logical deployment target (`my-service`).

### Deployment Group

Per-environment configuration (`my-service-prod`, `my-service-staging`). Targets specific EC2 instances (by tag / ASG / on-prem), an ECS service, or a Lambda function.

### Deployment Configuration

Defines the traffic-shift pattern:

- **AllAtOnce** — full cutover.
- **Half-at-a-time** (EC2).
- **One-at-a-time** (EC2).
- **Canary** (Lambda / ECS) — e.g., `10Percent5Minutes` shifts 10% for 5 minutes, then the rest.
- **Linear** — shift evenly over multiple intervals (e.g., `10Percent3Minutes`).
- **Custom** — your own percent/interval combinations.

### appspec.yml

For EC2/on-prem and ECS, the **appspec.yml** describes deployment lifecycle (file copies, scripts, hooks like `BeforeInstall`, `AfterInstall`, `ApplicationStart`, `ValidateService`). Lambda appspec maps function aliases to versions.

### Lifecycle hooks

Scripts that run at each phase (EC2/on-prem). For ECS/Lambda, hooks are Lambda functions that run at each phase and can perform validation, smoke tests, or even cancel the deploy.

### Traffic shifting (ECS / Lambda)

- **ECS blue/green** — CodeDeploy creates a new task set; ALB target groups swap traffic by weight.
- **Lambda blue/green** — function alias has weighted routing between versions.

### Alarms and rollback

- **CloudWatch alarms** attached to a deployment group; if any fires during deployment, CodeDeploy rolls back automatically.
- **Auto-rollback on failure** — failed deployments roll back by default.
- **Rollback on alarm** — explicit alarm list (HTTP 5xx rate, latency p99, custom error counts).

### Lambda hooks

For Lambda deployments, **BeforeAllowTraffic** and **AfterAllowTraffic** hooks are Lambda functions that run before / after traffic shift. Used for smoke tests; failure cancels the deployment.

### Deployment lifecycle (ECS blue/green)

1. New task set created.
2. Optional `BeforeInstall` / smoke tests.
3. Traffic shift starts (per chosen configuration).
4. `AfterAllowTestTraffic` (test listener) → `BeforeAllowTraffic` → `AfterAllowTraffic` hooks.
5. Old task set drained and terminated.

## Pricing model

- **Lambda / ECS / on-prem deployments** — **free** (you pay only for the underlying compute and any CloudWatch alarms).
- **On-prem instance deployments** — per on-prem-instance-update fee.
- **EC2 deployments** — **free** (you pay only for the underlying EC2).

CodeDeploy itself is free except for the on-prem-instance dimension.

## Quotas & limits

- **Applications per account per Region**: 1,000.
- **Deployment Groups per application**: 1,000.
- **Concurrent deployments**: bounded; raisable.
- **EC2 instances per deployment**: up to 1,000 (raisable).

## Common pitfalls

- **No alarms attached to the deployment group.** Without alarms, "successful deploy that broke prod" is silent. Always wire alarms.
- **AllAtOnce in production.** Defeats the point of CodeDeploy. Use Canary or Linear.
- **No `BeforeAllowTraffic` smoke test (Lambda).** A broken Lambda version gets traffic; downstream sees errors. Smoke-test before shifting traffic.
- **Aggressive canary in low-traffic services.** With 100 RPS, "10% canary for 5 min" sees 250 requests — too few to surface issues. Match canary duration / percent to traffic shape.
- **ECS blue/green without ALB.** Blue/green on ECS needs an ALB (or NLB) for traffic-group swap. Without one, in-place rolling is the only option.
- **EC2 lifecycle hooks not idempotent.** Re-deploys re-run scripts; non-idempotent ones break.
- **Lambda alias routing forgotten.** Many teams set up CodeDeploy for Lambda but invoke the unaliased function ARN, bypassing the alias. Always invoke via the alias.
- **Manual deploy of immutable artifacts.** "I'll deploy this hotfix from my laptop" defeats the audit trail. Always through CodePipeline or a tracked deployment invocation.

## Pairs well with

- [CodePipeline](codepipeline.md) — orchestration.
- [CodeBuild](codebuild.md) — produces deployment artifacts.
- [ECS](../compute/ecs.md), [Lambda](../compute/lambda.md), [EC2](../compute/ec2.md) — deployment targets.
- [CloudWatch](../observability/) (forthcoming) — alarms drive rollback.
- [ALB / NLB](../networking/elb.md) — required for ECS blue/green.
- [Systems Manager](../security-identity/parameter-store.md) — alternative for runbook-style EC2 deploys.

## Pairs well with these repo pages

- [CodePipeline](codepipeline.md), [CodeBuild](codebuild.md), [ECS](../compute/ecs.md), [Lambda](../compute/lambda.md).

## Further reading

- [AWS CodeDeploy documentation](https://docs.aws.amazon.com/codedeploy/).
- [Deployment configurations](https://docs.aws.amazon.com/codedeploy/latest/userguide/deployment-configurations.html).
- [appspec.yml reference](https://docs.aws.amazon.com/codedeploy/latest/userguide/reference-appspec-file.html).
- [Lambda blue/green with CodeDeploy](https://docs.aws.amazon.com/lambda/latest/dg/lambda-rolling-deployments.html).
- [Automatic rollbacks](https://docs.aws.amazon.com/codedeploy/latest/userguide/deployments-rollback-and-redeploy.html).
