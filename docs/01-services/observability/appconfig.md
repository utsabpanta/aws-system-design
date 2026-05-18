# AppConfig

> **One-line summary.** Managed runtime feature flags and dynamic config. Define configurations as code; deploy them gradually with validation, monitoring, and automatic rollback — decoupled from your application's deploy cycle.

## TL;DR
- For **feature flags, dynamic configuration, and operational toggles** that change independently of app deploys.
- Three concepts: **application** (logical app), **environment** (prod / staging / etc.), **configuration profile** (the data + its source — AppConfig hosted, S3, Parameter Store, Secrets Manager, CodePipeline).
- **Deployment strategies** define rollout (linear, exponential, canary, all-at-once). **Validators** (JSON schema / Lambda) prevent bad config from deploying.
- **Automatic rollback** on CloudWatch alarms during deployment — same idea as code blue/green, applied to config.
- **AppConfig Agent / Lambda extension** caches configs locally and polls in the background; near-zero latency on `getConfiguration` from your app.
- Compared to in-house feature-flag systems (Unleash, LaunchDarkly, Flagsmith): less feature-rich UX, deeper AWS integration, much cheaper at small scale.

## When to use it
- Feature flags for gradual feature rollout.
- Operational toggles (kill switches, circuit-breaker manual overrides, rate-limit knobs).
- Allow-list / deny-list updates without redeploying.
- Multi-environment configuration management with promotion workflows.
- Config that must update faster than your deploy cycle.

## When NOT to use it
- Static config baked at deploy time — env vars / Parameter Store are simpler.
- Heavy feature-flag UX needs (per-user targeting, experiments / A-B with statistical sig, user-segment management) — LaunchDarkly / Unleash / Flagsmith do these better.
- Long-form text / large blobs — AppConfig isn't a CMS.

## Key concepts

### Application
A logical name for your app (`payments-api`).

### Environment
A deployment target (`prod`, `staging`, `dev`). CloudWatch alarms can be attached to environments for rollback gating.

### Configuration profile
The data + its source. Sources:
- **AppConfig hosted configuration** — managed store inside AppConfig.
- **S3 bucket** — JSON / YAML / freeform.
- **Systems Manager Parameter Store** — String / SecureString.
- **Systems Manager document** — versioned.
- **AWS Secrets Manager** — for secret config.
- **CodePipeline** — pulled from a pipeline artifact.

### Validators
- **JSON schema** — validate structure of JSON config.
- **Lambda validator** — custom validation in code (call dependencies, sanity-check ranges).

Deployments fail before rolling if validation fails — bad config never reaches your app.

### Deployment strategies
- **AppConfig.Linear50PercentEvery30Seconds** — built-in.
- **AppConfig.Canary10Percent20Minutes** — built-in.
- **AppConfig.AllAtOnce** — immediate cutover.
- **Custom strategies** — define growth factor, deployment time, bake time.

### Automatic rollback
Attach **CloudWatch alarms** to the environment. If any fires during deployment or bake time, AppConfig rolls back automatically.

### AppConfig Agent (Lambda extension or sidecar)
- **Lambda extension** — runs alongside your Lambda function; caches config; you read from `localhost:2772` with no network call per invocation.
- **EC2 / ECS / EKS sidecar** — same idea, runs as a sidecar container or daemon.
- The right way to use AppConfig in production — avoids the per-request latency of direct `getConfiguration` API calls.

### Versions and immutability
Each configuration version is immutable. Deployments reference a specific version. Rollback = deploy a previous version.

### Feature flags (specific config profile type)
AppConfig supports **feature-flag-typed configuration profiles** with built-in schema validation for flag toggles + per-flag attributes (variant strings, percentages, allow-lists).

## Pricing model

- **Per million `getConfiguration` calls** (small).
- **Per configuration deployment** (small).
- **Hosted configuration storage** — first 1 MB free, per KB-month after.
- Lambda extension free; sidecar uses your underlying compute.

Extremely cheap for typical use.

## Quotas & limits

- **Applications per account per Region**: 100.
- **Environments per application**: 200.
- **Configuration profiles per application**: 100.
- **Configuration version size**: 1 MB.
- **Versions per configuration profile**: 100 (rolling — older versions auto-pruned).
- **Concurrent deployments per environment**: 1 (a deployment in flight blocks the next).

## Common pitfalls

- **Direct `getConfiguration` calls per request.** Hit rate limits; latency dominates. Use the Lambda extension / sidecar.
- **No validators.** A typo / missing field deploys to production. JSON-schema validators are cheap insurance.
- **No CloudWatch alarms on the environment.** Rollback gate doesn't exist; broken deploys ride out to 100% before anyone notices.
- **AllAtOnce deployments for risky changes.** Defeats the point. Use canary or linear.
- **Feature flags that live forever.** Stale flags accumulate; production becomes a maze of conditionals. Set retire-by dates; remove flag + dead branches.
- **Storing secrets in AppConfig hosted.** Use Secrets Manager for secrets; AppConfig for config. (You can wire AppConfig profiles whose source is Secrets Manager, which is the right pattern.)
- **Profile in S3 without versioning.** S3 versioning is required for AppConfig to track immutable profile versions when the source is S3.
- **One huge config profile.** Hard to reason about, slow validation. Split per concern.

## Pairs well with
- [Lambda](../compute/lambda.md), [ECS](../compute/ecs.md), [EKS](../compute/eks.md), [EC2](../compute/ec2.md) — config consumers.
- [Parameter Store](../security-identity/parameter-store.md), [Secrets Manager](../security-identity/secrets-manager.md), [S3](../storage/s3.md) — sources.
- [CloudWatch](cloudwatch.md) — alarm-driven rollback.
- [Systems Manager](systems-manager.md) — AppConfig is part of the SSM family.
- [CodePipeline](../devops/codepipeline.md) — automate deployments from pipelines.

## Pairs well with these repo pages
- [Parameter Store](../security-identity/parameter-store.md), [Secrets Manager](../security-identity/secrets-manager.md), [CloudWatch](cloudwatch.md), [Lambda](../compute/lambda.md).

## Further reading
- [AWS AppConfig documentation](https://docs.aws.amazon.com/appconfig/).
- [AppConfig feature flags](https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-creating-feature-flag.html).
- [Deployment strategies](https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-creating-deployment-strategy.html).
- [AppConfig Lambda extension](https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-integration-lambda-extensions.html).
- [Configuration validators](https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-creating-configuration-and-profile-validators.html).
