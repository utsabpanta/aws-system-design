# CDK (Cloud Development Kit)

> **One-line summary.** Define AWS infrastructure in **TypeScript, Python, Java, C#, or Go**. Compiles to CloudFormation; deploys through CloudFormation; gives you programming-language ergonomics over raw YAML.

## TL;DR

- The most popular way to write IaC for AWS in 2026. **CDK v2** (current) replaces v1 (which ended support June 2023). All new projects should be v2.
- **Constructs** are reusable infrastructure components at three abstraction levels: **L1** (1:1 to CloudFormation resources), **L2** (curated AWS-recommended defaults), **L3** (patterns combining multiple resources for a use case).
- **Construct Library** (`aws-cdk-lib`) ships AWS-supported L2 / L3 constructs. **Construct Hub** lists community / partner constructs.
- **CDK Pipelines** define self-mutating CI/CD pipelines in CDK itself — the pipeline updates itself when its definition changes.
- Recent (2026) stable: **CDK Mixins** (compose construct behaviors), **EKS v2** (production-ready EKS module).

## When to use it

- Any AWS-only IaC where you want type-safety, code reuse, and IDE help.
- Teams already in TypeScript / Python / Java / .NET — write infra in the same language as the app.
- Complex deployments where YAML templating would be unmanageable (loops, conditionals, dynamic resource counts).
- Self-mutating CI/CD via CDK Pipelines.

## When NOT to use it

- Multi-cloud — Terraform / Pulumi are the cross-cloud choice.
- Teams committed to Terraform — switching adds friction without clear benefit.
- Pure declarative YAML preference — some teams genuinely prefer reviewing CloudFormation templates over reading TypeScript.

## Key concepts

### Stacks and Apps

- **App** — root of the CDK tree.
- **Stack** — a CloudFormation stack, defined as a class inheriting from `Stack`.
- **Construct** — any composable piece of infrastructure; the unit of reuse.

### Construct levels

- **L1 (Cfn-Resource)** — auto-generated 1:1 mappings to CloudFormation resources (`CfnBucket`). All AWS resources have L1 coverage.
- **L2** — curated AWS-recommended constructs with sane defaults (`new Bucket(this, 'MyBucket', { encryption: BucketEncryption.S3_MANAGED })`). The right starting point.
- **L3 (Patterns)** — combine multiple resources into use-case patterns (`ApplicationLoadBalancedFargateService` provisions VPC + ALB + ECS Service + Task Def + IAM in one construct).

### `aws-cdk-lib`

The unified AWS Construct Library. One npm/PyPI/Maven package contains all AWS modules. Stable APIs.

### Construct Hub

Discover community / partner constructs (Datadog, MongoDB, Cloudflare, Slack, etc.). Reusable patterns published by AWS Solutions / community.

### CDK Pipelines

A self-mutating CI/CD pipeline defined in CDK. When the CDK source changes (including the pipeline definition itself), the pipeline updates first, then deploys downstream stacks.

### Synth / deploy

- `cdk synth` — compile to CloudFormation.
- `cdk deploy` — deploy via CloudFormation (uploads template, executes change set).
- `cdk diff` — show changes vs deployed state.
- `cdk destroy` — delete stack.

### Bootstrapping

`cdk bootstrap` creates the staging bucket / ECR repo and roles CDK uses per account/Region. Required per environment.

### Aspects

Cross-cutting modifications to a construct tree — apply IAM policy boundaries, tag everything, enforce naming, etc.

### Escape hatches

When the L2 doesn't expose a setting you need, drop to the L1 via `node.defaultChild` and configure directly.

### Recent (2026) features

- **CDK Mixins** (stable) — compose construct behaviors via composable mixins.
- **EKS v2** (graduated to stable) — production-ready EKS module with cleaner APIs.

### Migration from CDK v1

CDK v1 entered maintenance in June 2022 and ended support June 2023. Migrate via [the v1→v2 guide](https://docs.aws.amazon.com/cdk/v2/guide/migrating-v2.html); the surface change is largely import paths (`@aws-cdk/aws-s3` → `aws-cdk-lib/aws-s3`) and a few deprecations.

## Pricing model

- **CDK itself is free.**
- **Underlying CloudFormation** is free.
- **AWS resources you create** billed as normal.

## Quotas & limits

- Inherited from **CloudFormation** (stack count, resources per stack, template size).
- **Construct count** in one app — bounded only by memory; very large apps may benefit from stack splitting.

## Common pitfalls

- **L1 everywhere because "we want control."** L2s offer the right defaults; L1 means re-implementing them. Use L2 first; drop to L1 via escape hatches when needed.
- **One stack with everything.** Hard to reason about, slow updates, large blast radius. Split by lifecycle (data, compute, networking).
- **`cdk deploy` from a developer laptop in production.** Audit trail, environment drift. Use CDK Pipelines or a deploy account.
- **`cdk diff` skipped before deploy.** Surprises. Always diff first; require CI to gate on diff review.
- **No bootstrap on a new account / Region.** First `cdk deploy` will fail; bootstrap first.
- **Hardcoded Region / account.** Stacks become non-portable. Use environment-agnostic constructs or env-from-context.
- **CDK v1 still in use.** v1 reached EOL June 2023; security patches stopped. Migrate.
- **Constructs not tested.** Unit-test constructs with `aws-cdk-lib/assertions`; otherwise regressions appear in deploy.

## Pairs well with

- [CloudFormation](cloudformation.md) — the engine underneath.
- [CodePipeline](codepipeline.md) — CDK Pipelines integration.
- [SAM](sam.md) — share patterns; some teams use SAM CLI to invoke CDK-built Lambdas locally.
- **Construct Hub, AWS Solutions Constructs** — pattern libraries.
- **`cdk-nag`** — security/compliance linting for CDK apps.
- **Projen** — meta-tool for managing the CDK project itself (deps, scripts, configs).

## Pairs well with these repo pages

- [CloudFormation](cloudformation.md), [SAM](sam.md), [CodePipeline](codepipeline.md).

## Further reading

- [AWS CDK v2 documentation](https://docs.aws.amazon.com/cdk/v2/guide/).
- [CDK Pipelines](https://docs.aws.amazon.com/cdk/v2/guide/cdk_pipeline.html).
- [Construct Hub](https://constructs.dev/).
- [Migrating from CDK v1 to v2](https://docs.aws.amazon.com/cdk/v2/guide/migrating-v2.html).
- [CDK best practices](https://docs.aws.amazon.com/cdk/v2/guide/best-practices.html).
- [cdk-nag](https://github.com/cdklabs/cdk-nag).
